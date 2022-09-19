import discord
import random
import asyncio
import re
from cogs.view import AlphaView
from discord.utils import get
from discord.ext import commands
from bfunc import settingsRecord, settingsRecord, alphaEmojis, commandPrefix, db

def admin_or_owner():
    async def predicate(ctx):
        output = ctx.message.author.id in [220742049631174656, 203948352973438995] or (get(ctx.message.guild.roles, name = "A d m i n") in ctx.message.author.roles)
        return  output
    return commands.check(predicate)

async def disambiguate(options, msg, author):
    view = AlphaView(options, author, True)
    msg = await msg.edit(view = view)
    await view.wait()
    await msg.edit(view = None)
    return view.state

"""
The purpose of this function is to do a general call to the database
apiEmbed -> the embed element that the calling function will be using
apiEmbedmsg -> the message that will contain apiEmbed
table -> the table in the database that should be searched in, most common tables are RIT, MIT and SHOP
query -> the word which will be searched for in the "Name" property of elements, adjustments were made so that also a special property "Grouped" also gets searched
"""
async def callAPI(ctx, apiEmbed="", apiEmbedmsg=None, table=None, query=None, tier=5, exact=False, filter_rit=True):
    
    #channel and author of the original message creating this call
    channel = ctx.channel
    author = ctx.author
    
    #do nothing if no table is given
    if table is None:
       return None, apiEmbed, apiEmbedmsg

    collection = db[table]
    
    #get the entire table if no query is given
    if query is None:
        return list(collection.find()), apiEmbed, apiEmbedmsg

    #if the query has no text, return nothing
    if query.strip() == "":
        return None, apiEmbed, apiEmbedmsg

    #restructure the query to be more regEx friendly
    invalidChars = ["[", "]", "?", '"', "\\", "*", "$", "{", "}", "^", ">", "<", "|"]

    for i in invalidChars:
        if i in query:
            await channel.send(f":warning: Please do not use `{i}` in your query. Revise your query and retry the command.\n")
            return None, apiEmbed, apiEmbedmsg
         
    query = query.strip()
    query = query.replace('(', '\\(')
    query = query.replace(')', '\\)')
    query = query.replace('+', '\\+')
    query = query.replace('.', '\\.')
    query_data =  {"$regex": query,
                    #make the check case-insensitively
                    "$options": "i"
                  }
    if exact:
        query_data["$regex"] = f'^{query_data["$regex"]}$'
        
    #search through the table for an element were the Name or Grouped property contain the query
    if table == "spells":
        filterDic = {"Name": query_data}
    else:
        filterDic = {"$or": [
                            {
                              "Name": query_data
                            },
                            {
                              "Grouped": query_data
                            }
                        ]
                    } 
    if table == "rit" or table == "mit":
        filterDic['Tier'] = {'$lt':tier+1}
    
     
    # Here lies MSchildorfer's dignity. He copy and pasted with abandon and wondered why
    #  collection.find(collection.find(filterDic)) does not work for he could not read
    # https://cdn.discordapp.com/attachments/663504216135958558/735695855667118080/New_Project_-_2020-07-22T231158.186.png
    records = list(collection.find(filterDic))
    
    #turn the query into a regex expression
    r = re.compile(query, re.IGNORECASE)
    #restore the original query
    query = query.replace("\\", "")
    #sort elements by either the name, or the first element of the name list in case it is a list
    def sortingEntryAndList(elem):
        if(isinstance(elem['Name'],list)): 
            return elem['Name'][0] 
        else:  
            return elem['Name']
    
    #create collections to track needed changes to the records
    remove_grouper = [] #track all elements that need to be removes since they act as representative for a group of items
    faux_entries = [] #collection of temporary items that will act as database elements during the call
    
    #for every search result check if it contains a group and create entries for each group element if it does
    for entry in records:
        # if the element is part of a group
        if("Grouped" in entry):
            # remove it later
            remove_grouper.append(entry)
            # check if the query is more specific about a group element
            newlist = list(filter(r.search, entry['Name']))
            """
            if the every element has been filtered out because of the code above then we know from the fact 
            that this was found in the search that the Grouper field had to have been matched, 
            indicating that the entire group needs to be listed
            """
            if(newlist == list()):
                newlist = entry['Name']
            # for every group element that needs to be considered, create a new element with just the name adjusted
            for name in newlist:
                #copy the Group entry to get all relevant information about the item
                faux_entry = entry.copy()
                #change the name from the list to the specific element.
                faux_entry["Name"]= name
                #add it to the tracker
                faux_entries.append(faux_entry)
    # remove all group representatives
    for group_to_remove in remove_grouper:
        records.remove(group_to_remove)
    #append the new entries
    records += faux_entries
    if filter_rit and table == "rit":
        # get all minor reward item results
        all_minors = list([record["Name"] for record in filter(lambda record: record["Minor/Major"]== "Minor", records)])
        records = filter(lambda record: record["Minor/Major"]!= "Major" or record["Name"] not in all_minors, records)

    
    #sort all items alphabetically 
    records = sorted(records, key = sortingEntryAndList)    
    #if no elements are left, return nothing
    if records == list():
        return None, apiEmbed, apiEmbedmsg
    else:
        #create a string to provide information about the items to the user
        infoString = ""
        if (len(records) > 1):
            #sort items by tier if the magic item tables were requested
            if table == 'mit' or table == 'rit':
                records = sorted(records, key = lambda i : i ['Tier'])
            queryLimit = 20
            #limit items to queryLimit
            for i in range(0, min(len(records), queryLimit)):
                if table == 'mit':
                    infoString += f"{alphaEmojis[i]}: {records[i]['Name']} (Tier {records[i]['Tier']}): **{records[i]['TP']} TP**\n"
                elif table == 'rit':
                    infoString += f"{alphaEmojis[i]}: {records[i]['Name']} (Tier {records[i]['Tier']} {records[i]['Minor/Major']})\n"
                # base spell scroll db entry should not be searched
                elif table == 'shop' and records[i]['Type'] == "Spell Scroll":
                    pass
                else:
                    infoString += f"{alphaEmojis[i]}: {records[i]['Name']}\n"
            #inform the user of the current information and ask for their selection of an item
            apiEmbed.add_field(name=f"There seems to be multiple results for \"**{query}**\"! Please choose the correct one.\nThe maximum number of results shown is {queryLimit}. If the result you are looking for is not here, please react with ❌ and be more specific.", value=infoString, inline=False)
            if not apiEmbedmsg or apiEmbedmsg == "Fail":
                apiEmbedmsg = await channel.send(embed=apiEmbed)
            else:
                await apiEmbedmsg.edit(embed=apiEmbed)
            choice = await disambiguate(min(len(records), queryLimit), apiEmbedmsg, author)
            
            if choice is None or choice == -1:
                await apiEmbedmsg.edit(embed=None, content=f"Command cancelled. Try again using the same command!")
                ctx.command.reset_cooldown(ctx)
                return None, apiEmbed, "Fail"
            apiEmbed.clear_fields()
            return records[choice], apiEmbed, apiEmbedmsg

        else:
            #if only 1 item was left, simply return it
            return records[0], apiEmbed, apiEmbedmsg

async def checkForChar(ctx, char, charEmbed="", authorOverride=None,  mod=False, customError=False, authorCheck=None):
    channel = ctx.channel
    author = ctx.author
    guild = ctx.guild
    if authorOverride != None:
        author = authorOverride
        mod=False
    search_author = author
    if authorCheck != None:
        search_author = authorCheck
        mod=False
    playersCollection = db.players

    query = char.strip()
    query = query.replace('(', '\\(')
    query = query.replace(')', '\\)')
    query = query.replace('.', '\\.')
    query_data =  {"$regex": query,
                    "$options": "i"
                  }
    filterDic = {"$or": [
                            {
                              "Name": query_data
                            },
                            {
                              "Nickname": query_data
                            }
                        ]
                    } 
    if mod == True:
        charRecords = list(playersCollection.find(filterDic)) 
    else:
        filterDic["User ID"] = str(search_author.id)
        charRecords = list(playersCollection.find(filterDic))

    if charRecords == list():
        if not mod and not customError:
            await channel.send(content=f'I was not able to find your character named "**{char}**". Please check your spelling and try again.')
        ctx.command.reset_cooldown(ctx)
        return None, None

    else:
        if len(charRecords) > 1:
            infoString = ""
            
            charRecords = sorted(list(charRecords), key = lambda i : i ['Name'])
            for i in range(0, min(len(charRecords), 20)):
                infoString += f"{alphaEmojis[i]}: {charRecords[i]['Name']} ({guild.get_member(int(charRecords[i]['User ID']))})\n"
            
            
            charEmbed.add_field(name=f"There seems to be multiple results for \"`{char}`\"! Please choose the correct character. If you do not see your character here, please react with ❌ and be more specific with your query.", value=infoString, inline=False)
            charEmbedmsg = await channel.send(embed=charEmbed)
            choice = await disambiguate(min(len(charRecords), 20), charEmbedmsg, author)
            
            if choice is None or choice == -1:
                await charEmbedmsg.edit(embed=None, content=f"Character information cancelled. Try again using the same command!")
                ctx.command.reset_cooldown(ctx)
                return None, None
            charEmbed.clear_fields()
            return charRecords[choice], charEmbedmsg

    return charRecords[0], None

async def checkForGuild(ctx, name, guildEmbed="" ):
    channel = ctx.channel
    author = ctx.author
    guild = ctx.guild

    name = name.strip()

    collection = db.guilds
    guildRecords = list(collection.find({"Name": {"$regex": name, '$options': 'i' }}))


    if guildRecords == list():
        await channel.send(content=f'I was not able to find a guild named "**{name}**". Please check your spelling and try again.')
        ctx.command.reset_cooldown(ctx)
        return None, None
    else:
        if len(guildRecords) > 1:
            infoString = ""
            guildRecords = sorted(list(guildRecords), key = lambda i : i ['Name'])
            for i in range(0, min(len(guildRecords), 20)):
                infoString += f"{alphaEmojis[i]}: {guildRecords[i]['Name']}\n"
            
            guildEmbed.add_field(name=f"There seems to be multiple results for \"`{name}`\"! Please choose the correct character. If you do not see your character here, please react with ❌ and be more specific with your query.", value=infoString, inline=False)
            guildEmbedmsg = await channel.send(embed=guildEmbed)
            choice = await disambiguate(min(len(records), 20), guildEmbedmsg, author)
            
            if choice is None or choice == -1:
                await guildEmbedmsg.edit(embed=None, content=f"Command cancelled. Try again using the same command!")
                ctx.command.reset_cooldown(ctx)
                return None, None
            guildEmbed.clear_fields()
            return guildRecords[choice], guildEmbedmsg

    return guildRecords[0], None
class Misc(commands.Cog):
    def __init__ (self, bot):
    
        self.bot = bot
        self.current_message= None
        #0: No message search so far, 1: Message searched, but no new message made so far, 2: New message made
        self.past_message_check= 0

    @commands.cooldown(1, 5, type=commands.BucketType.member)
    @admin_or_owner()
    @commands.command()
    async def uwu(self,ctx):
        channel = ctx.channel
        vowels = ['a','e','i','o','u']
        faces = ['rawr XD', 'OwO', 'owo', 'UwU', 'uwu']
        async with channel.typing():
            async for message in channel.history(before=ctx.message, limit=1, oldest_first=False):
                uwuMessage = message.content.replace('r', 'w')
                uwuMessage = uwuMessage.replace('l', 'w')
                uwuMessage = uwuMessage.replace('ove', 'uv')
                uwuMessage = uwuMessage.replace('.', '!')
                uwuMessage = uwuMessage.replace(' th', ' d')
                uwuMessage = uwuMessage.replace('th', 'f')
                uwuMessage = uwuMessage.replace('mom', 'yeshh')

                for v in vowels:
                  uwuMessage = uwuMessage.replace('n'+ v, 'ny'+v)

        i = 0
        while i < len(uwuMessage):
            if uwuMessage[i] == '!':
                randomFace = random.choice(faces)
                if i == len(uwuMessage):
                    uwuMessage = uwuMessage + ' ' + randomFace
                    break
                else:
                  uwuList = list(uwuMessage)
                  uwuList.insert(i+1, " " + randomFace)
                  uwuMessage = ''.join(uwuList)
                  i += len(randomFace)
            i += 1
            

        await channel.send(content=message.author.display_name + ":\n" +  uwuMessage)
        await ctx.message.delete()
        
    #this function is passed in with the channel which has been created/moved
    #relies on there being a message to use
    async def printCampaigns(self,chan):
        
        ch =self.bot.get_channel(382027251618938880) #382027251618938880 728476108940640297
        #find the message in the Campaign Board
        
        message = await discord.utils.get(ch.history(), author__id = self.bot.user.id)
        #Go through all categories with Campaign in the name and Grab all channels in the Campaign category and their ids
        campaign_channels = []
        for cat in chan.guild.categories:
            if("campaigns" in cat.name.lower()):
                campaign_channels+=cat.text_channels
        excluded = [787161189767577640, 382027251618938880, 1003501229588107386] 
        text = "Number of currently-running campaigns: "
        filtered = []
        #filter the list of channels to be just viewable and not in the specific excluded list
        for channel in campaign_channels:
            if(channel.permissions_for(chan.guild.me).view_channel and channel.id not in excluded):
                filtered.append(channel)
        #sort alphebetical ignoring the 'the'
        def sortChannel(elem):
            name = elem.name
            if(name.startswith("the-")):
                name = name.split("-", 1)[1]
            return name
        #generate the string
        filtered.sort(key = sortChannel)
        text += "**"+str(len(filtered))+"**!\n\n"
        text += (" | ").join(map(lambda c: c.mention, filtered))
        if(not message):
            message = await ch.send(content=text)
            return
        await message.edit(content=text)
                
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if("campaigns" in channel.category.name.lower()):   
            await self.printCampaigns(channel)
            
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if("campaigns" in channel.category.name.lower()):   
            await self.printCampaigns(channel)
            
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if("campaigns" in before.category.name.lower()   and  before.category.name != after.category.name):   
            await self.printCampaigns(before)
    #searches for the last message sent by the bot in case a restart was made
    #Allows it to use it to remove the last post
    async def find_message(self, channel_id):
        #block any check but the first one
        if(not self.past_message_check):
            self.past_message_check= 1
            
            self.current_message = await discord.utils.get(self.bot.get_channel(channel_id).history(), author__id = self.bot.user.id)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self,payload):
        await self.role_management_kernel(payload)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        await self.role_management_kernel(payload)
    
    async def role_management_kernel(self, payload):
        if not str(payload.channel_id) in settingsRecord["Role Channel List"].keys(): 
            return
        guild_id = settingsRecord["Role Channel List"][str(payload.channel_id)]
        guild = self.bot.get_guild(int(guild_id))

        if (str(payload.message_id) in settingsRecord[guild_id]["Messages"].keys()
            and payload.emoji.name in settingsRecord[guild_id]["Messages"][str(payload.message_id)].keys()):
            
            name = settingsRecord[guild_id]["Messages"][str(payload.message_id)][payload.emoji.name]
            role = get(guild.roles, name = name)
            if role is not None:
                member = guild.get_member(payload.user_id)
                if member is not None:
                    has_role = role in member.roles
                    if has_role:
                        action = "remove_roles"
                        extra_text = "You will no longer be pinged for quests of this tier. React with the same emoji if you would like to be pinged for quests of this tier again!"
                        if "Campaign" in role.name:
                            extra_text = "You will no longer be pinged for campaigns on the `#campaign-board` channel. React to the same emoji if you want to be pinged for campaigns!"
                    
                        text = f":tada: ***{member.display_name}***, I have removed the ***{name}*** role from you! {extra_text}"
                    else:
                        action = "add_roles"
                        extra_text = "You will be pinged for quests of this tier. React to the same emoji if you no longer want to be pinged for quests of this tier!"
                        if "Campaign" in role.name:
                            extra_text = "You will be pinged for campaigns on the `#campaign-board` channel. React to the same emoji if you no longer want to be pinged for campaigns!"
                    
                        text = f":tada: ***{member.display_name}***, I have given you the ***{name}*** role! {extra_text}"
                        
                    await getattr(member, action)(role, atomic=True)
                    successMsg = await getattr(member, "send")(text)
                else:
                    print('member not found')
            else:
                print('role not found')

    #A function that grabs all messages in the quest board and compiles a list of availablities
    async def generateMessageText(self, channel_id):
        tChannel = channel_id
        channel= self.bot.get_channel(tChannel)
        #get all game channel ids
        game_channel_category =self.bot.get_channel(settingsRecord[str(channel.guild.id)]["Game Rooms"])
        game_channel_ids = set(map(lambda c: c.id, game_channel_category.text_channels))
        build_message = "**It is Double DM Rewards Weekend (DDMRW)!** Get out there and host some one-shots!\n"*settingsRecord['ddmrw']+ "The current status of the game channels is:\n"
        #create a dictonary to store the room/user pairs
        tierMap = {"Tier 0" : "T0", "Tier 1" : "T1", "Tier 2" : "T2", "Tier 3" : "T3", "Tier 4" : "T4", "Tier 5" : "T5"}
        emoteMap = settingsRecord[str(channel.guild.id)]["Emotes"]
        channel_dm_dic = {}
        for c in game_channel_category.text_channels:
            channel_dm_dic[c.mention]= ["✅ "+c.mention+": Clear", []]
        #get all posts in the channel
        all_posts = [post async for post in channel.history(oldest_first=True)]
        for elem in all_posts:
            content = elem.content
            #ignore self and Ghost example post
            if(elem.author.id==self.bot.user.id 
                or elem.id == 800644241189503026
                or not isinstance(elem.author, discord.Member)):
                continue
            #loop in order to avoid guild channels blocking the check
            for mention in elem.channel_mentions:
                if mention.id in game_channel_ids:
                    username = elem.author.name
                    if(elem.author.nick):
                        username = elem.author.nick
                    channel_dm_dic[mention.mention][0] = "❌ "+mention.mention+": "+username
                    tier_list = []
                    for tierMention in elem.role_mentions:
                        name_split = tierMention.name.split(" ",1)
                        if tierMention.name.split(" ",1)[1] in tierMap:
                            tier_list.append(emoteMap[tierMention.name.split(" ",1)[0]]+" "+tierMap[tierMention.name.split(" ",1)[1]])
                    time_text = ""
                    hammer_times = re.findall("<t:(\\d+)(?::.)?>", content)
                    if hammer_times:
                        time_text = f" - <t:{hammer_times[0]}>"
                    else:
                        timing = re.findall("When.*?:.*? (.*?)\n", content)
                        if timing:
                            time_text = f" - {timing[0]}"
                    if tier_list or time_text:
                        channel_dm_dic[mention.mention][1].append("/".join(sorted(tier_list))+ time_text)
        #build the message using the pairs built above
        for c in game_channel_category.text_channels:
            if(c.permissions_for(channel.guild.me).view_channel and c.id != 820394366278697020): 
                tierAddendum = ""
                if(len(channel_dm_dic[c.mention][1])> 0):
                    tierAddendum = "\n       "+"\n       ".join(channel_dm_dic[c.mention][1])
                build_message+=""+channel_dm_dic[c.mention][0]+tierAddendum+"\n"
        return build_message
    
        
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        #if in the correct channel and the message deleted was not the last QBAP
        if(str(payload.channel_id) in settingsRecord["QB List"].keys() and (not self.current_message or payload.message_id != self.current_message.id)):
            await self.find_message(payload.channel_id)
            #Since we dont know whose post was deleted we need to cover all the posts to find availablities
            #Also protects against people misposting
            new_text = await self.generateMessageText(payload.channel_id)
            #if we created the last message during current runtime we can just edit
            if(self.current_message and self.past_message_check != 1):
                await self.current_message.edit(content=new_text)
            else:
                #otherwise delete latest message if possible and resend to get back to the bottom
                if(self.current_message):
                    await self.current_message.delete()
                self.past_message_check = 2
                self.current_message = await self.bot.get_channel(payload.channel_id).send(content=new_text)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
    
        if(str(payload.channel_id) in settingsRecord["QB List"].keys() and (not self.current_message or payload.message_id != self.current_message.id)):
            await self.find_message(payload.channel_id)
            new_text = await self.generateMessageText(payload.channel_id)
            if(self.current_message and self.past_message_check != 1):
                #in case a message is posted without a game channel which is then edited in we need to this extra check
                msgAfter = False
                async for message in self.bot.get_channel(payload.channel_id).history(after=self.current_message, limit=1):
                    msgAfter = True
                if( not msgAfter):
                    await self.current_message.edit(content=new_text)
                else:
                    await self.current_message.delete()
                    self.current_message = await self.current_message.channel.send(content=new_text)
            else:
                self.past_message_check = 2
                if(self.current_message):                
                    msgAfter = False
                    async for message in self.bot.get_channel(payload.channel_id).history(after=self.current_message, limit=1):
                        msgAfter = True
                    if(not msgAfter):
                        await self.current_message.edit(content=new_text)
                        return
                    else:
                        await self.current_message.delete()
                self.current_message = await self.bot.get_channel(payload.channel_id).send(content=new_text)

    @commands.Cog.listener()
    async def on_message(self,msg):
        if msg.guild == None: 
            return
        tChannel = settingsRecord[str(msg.guild.id)]["QB"]
        if any(word in msg.content.lower() for word in ['thank', 'thanks', 'thank you', 'thx', 'gracias', 'danke', 'arigato', 'xie xie', 'merci']) and 'bot' in msg.content.lower():
            await msg.add_reaction('❤️')
            await msg.channel.send("You're welcome friend!")
        elif msg.channel.id == tChannel and msg.author.id != self.bot.user.id:

            await self.find_message(msg.channel.id)
            server = msg.guild
            channel = msg.channel
            game_channel_category = server.get_channel(settingsRecord[str(server.id)]["Game Rooms"])
            cMentionArray = msg.channel_mentions
            game_channel_ids = list(map(lambda c: c.id, game_channel_category.text_channels))
            for mention in cMentionArray:
                if mention.id in game_channel_ids:
                    new_text = await self.generateMessageText(channel.id)
                    if(self.past_message_check == 2):
                        await self.current_message.delete()
                        self.current_message = await msg.channel.send(content=new_text)
                        return
                    #if there is an old message our record could be out of date so we need to regather info and go to the bottom
                    elif(self.past_message_check == 1 and self.current_message):
                        await self.current_message.delete()
                    self.past_message_check = 2
                    self.current_message = await msg.channel.send(content=new_text)
                    return
            return
    @commands.command()
    async def help(self, ctx, *, pageString=''):
        if ctx.channel.type == discord.ChannelType.private:
            await ctx.channel.send("Sorry, the `$help` command cannot be used in the DMs of the bot. Use one of the log channels on the D&D Friends Server")
            return
        def helpCheck(r,u):
            sameMessage = False
            if helpMsg.id == r.message.id:
                sameMessage = True
            return (r.emoji in alphaEmojis[:numPages]) and u == ctx.author and sameMessage
        bot = self.bot
        helpEmbedMenu = discord.Embed()
        helpEmbedGen = discord.Embed()
        helpEmbedChar = discord.Embed()
        helpEmbedItems = discord.Embed() 
        helpEmbedTimerOne = discord.Embed()
        helpEmbedTimerTwo = discord.Embed()
        helpEmbedTimerThree = discord.Embed()
        helpEmbedShop = discord.Embed()
        helpEmbedTp = discord.Embed()
        helpEmbedGuild = discord.Embed()
        helpEmbedCampaign = discord.Embed()

        page = 0
        if 'gen' in pageString:
            page = 1
        elif 'char' in pageString:
            page = 2
        elif 'tp' in pageString:
            page = 3
        elif 'shop' in pageString:
            page = 4
        elif 'guild' in pageString:
            page = 5
        elif 'timer2' in pageString:
            page = 7
        elif 'timer3' in pageString:
            page = 8
        elif 'timer1' in pageString or 'timer' in pageString:
            page = 6
        elif 'campaign' in pageString:
            page = 9


    # MAIN HELP MENU ($help)


        helpList = [helpEmbedMenu, helpEmbedGen, helpEmbedChar, helpEmbedTp, helpEmbedShop, helpEmbedGuild, helpEmbedTimerOne, helpEmbedTimerTwo, helpEmbedTimerThree, helpEmbedCampaign]

        helpEmbedMenu.title = 'Bot Friend Commands - Table of Contents'
        helpEmbedMenu.description = 'Please react to the group of commands you would like to see and gain more knowledge about.'
        helpEmbedMenu.add_field(name=f"{alphaEmojis[0]} General Commands\n{commandPrefix}help gen", value="Various commands which don't fit into any other section.", inline=False)
        helpEmbedMenu.add_field(name=f"{alphaEmojis[1]} Character Commands\n{commandPrefix}help char", value="How to manage your character(s).", inline=False)
        helpEmbedMenu.add_field(name=f"{alphaEmojis[2]} TP Commands\n{commandPrefix}help tp", value="How to spend TP to acquire magic items.", inline=False)
        helpEmbedMenu.add_field(name=f"{alphaEmojis[3]} Shop Commands\n{commandPrefix}help shop", value="How to spend GP to purchase various things or sell mundane items.", inline=False)
        helpEmbedMenu.add_field(name=f"{alphaEmojis[4]} Guild Commands\n{commandPrefix}help guild", value="How to be a member of a guild or manage one.", inline=False)
        helpEmbedMenu.add_field(name=f"{alphaEmojis[5]} Pre-Quest Timer Commands\n{commandPrefix}help timer1", value="How to prepare and sign up to a timer for a one-shot.", inline=False)
        helpEmbedMenu.add_field(name=f"{alphaEmojis[6]} Running Timer Commands\n{commandPrefix}help timer2", value="How to do various things while hosting or participating in a one-shot.", inline=False)
        helpEmbedMenu.add_field(name=f"{alphaEmojis[7]} Post-Quest Timer Commands\n{commandPrefix}help timer3", value="How to do various things after the completion of a one-shot.", inline=False)
        helpEmbedMenu.add_field(name=f"{alphaEmojis[8]} Campaign Commands\n{commandPrefix}help campaign", value="How to create, host, and participate in a campaign.", inline=False)



    # DM HELP MENU ($help dm)

    # THIS HELP MENU WOULD ONLY BE NECESSARY IF WE COULD SPLIT UP THE HELP MENU IN TWO BRANCHES: ONE FOR PLAYERS AND ONE FOR DMs.
    #    helpList = [helpEmbedMenuDM, helpEmbedTimerOne, helpEmbedTimerTwo, helpEmbedTimerThree, helpEmbedCampaign]

    #    helpEmbedMenu.title = 'Bot Friend DM Commands - Table of Contents'
    #    helpEmbedMenu.description = 'Please react to the group of commands you would like to see and gain more knowledge about.'
    #    helpEmbedMenu.add_field(name=f"1️⃣ Pre-Quest Timer Commands\n{commandPrefix}help dm timer1", value="", inline=False)
    #    helpEmbedMenu.add_field(name=f"2️⃣ Running Timer Commands\n{commandPrefix}help dm timer2", value="", inline=False)
    #    helpEmbedMenu.add_field(name=f"3️⃣ Post-Quest Timer Commands\n{commandPrefix}help dm timer3", value="", inline=False)
    #    helpEmbedMenu.add_field(name=f"4️⃣ Campaign Commands\n{commandPrefix}help dm campaign", value="", inline=False)



    # GENERAL COMMANDS ($help general)

        helpEmbedGen.title = 'General Commands'
        
        helpEmbedGen.add_field(name=f'▫️ Applying for Membership (only available in Direct Messages to Bot Friend)', value=f'{commandPrefix}membership', inline=False)

        helpEmbedGen.add_field(name=f'▫️ Creating and Viewing Your User Profile', value=f'{commandPrefix}user', inline=False)

        helpEmbedGen.add_field(name=f'▫️ Viewing the List of Allowed Races', value=f'{commandPrefix}printRaces', inline=False)

        helpEmbedGen.add_field(name=f'▫️ Calculating Rewards', value=f'{commandPrefix}reward XhYm tier', inline=False)

        helpEmbedGen.add_field(name=f'▫️ Rolling a Random Reward Item', value=f'{commandPrefix}random tier major/minor #', inline=False)

        helpEmbedGen.add_field(name=f'▫️ Viewing Server Stats', value=f'{commandPrefix}stats', inline=False)

        helpEmbedGen.add_field(name=f'▫️ Viewing Highest-CP Characters', value=f'{commandPrefix}top x', inline=False)

        helpEmbedGen.add_field(name=f'▫️ Viewing Fanatic Competition Stats', value=f'{commandPrefix}fanatic', inline=False)

        helpEmbedGen.add_field(name=f'▫️ Submitting a Suggestion (only available in Direct Messages with Bot Friend)', value=f'{commandPrefix}inbox', inline=False)



    # CHARACTER COMMANDS MENU ($help char)

        helpEmbedChar.title = 'Character Commands'

        helpEmbedChar.add_field(name=f'▫️ Creating a Character', value=f'{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"', inline=False)

        helpEmbedChar.add_field(name=f'▫️ Viewing a Character\'s Information', value=f'{commandPrefix}info "character name"\n[{commandPrefix}char, {commandPrefix}i]', inline=False)

        helpEmbedChar.add_field(name=f'▫️ Viewing a Character\'s Inventory', value=f'{commandPrefix}inventory "character name"\n[{commandPrefix}inv, {commandPrefix}bag]', inline=False)

        helpEmbedChar.add_field(name=f'▫️ Adding an Image to a Character', value=f'{commandPrefix}image "character name" "URL"\n[{commandPrefix}img]', inline=False)

        helpEmbedChar.add_field(name=f'▫️ Leveling Up', value=f'{commandPrefix}levelup "character name"\n[{commandPrefix}lvlup, {commandPrefix}lvl, {commandPrefix}lv]', inline=False)

        helpEmbedChar.add_field(name=f'▫️ Creating a Multiclass Character', value=f'{commandPrefix}create "character name" total level "race" "class1 level / class2 level, [...]" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"', inline=False)

        helpEmbedChar.add_field(name=f'▫️ Respecing a Character', value=f'{commandPrefix}respec "character name" "new character name" "race" "class" "background" STR DEX CON INT WIS CHA', inline=False)

        helpEmbedChar.add_field(name=f'▫️ Respecing a Character into a Multiclass', value=f'{commandPrefix}respec "character name" "new character name" "race" "class1 level / class2 level / class3 level / class4 level" "background" STR DEX CON INT WIS CHA', inline=False)

        helpEmbedChar.add_field(name=f'▫️ Re-flavoring a Character', value=f'{commandPrefix}reflavor race "character name" race name\n{commandPrefix}reflavor class "character name" class name\n{commandPrefix}reflavor background "character name" background name\n[{commandPrefix}rf]', inline=False)

        helpEmbedChar.add_field(name=f'▫️ Adding Extra Names', value=f'{commandPrefix}alias "character name" "surname, nickname1, nickname2, othername, [...]\n[{commandPrefix}aka]', inline=False)
        
        helpEmbedChar.add_field(name=f'▫️ Renaming', value=f'{commandPrefix}rename "character name" "new name"\n[{commandPrefix}rn]', inline=False)

        helpEmbedChar.add_field(name=f'▫️ Adding Alignment', value=f'{commandPrefix}align "character name" alignment', inline=False)

        helpEmbedChar.add_field(name=f'▫️ Retiring a Character', value=f'{commandPrefix}retire "character name"', inline=False)

        helpEmbedChar.add_field(name=f'▫️ Attuning to a Magic Item', value=f'{commandPrefix}attune "character name" "magic item"\n[{commandPrefix}att]', inline=False)

        helpEmbedChar.add_field(name=f'▫️ Unattuning from a Magic Item', value=f'{commandPrefix}unattune "character name" "magic item"\n[{commandPrefix}unatt, {commandPrefix}uatt]', inline=False)

        helpEmbedChar.add_field(name=f'▫️ Death Options', value=f'{commandPrefix}death "character name"', inline=False)
        
        helpEmbedChar.add_field(name=f'▫️ Adding Campaign Time', value=f'{commandPrefix}applyTime "character name" #channel XhYm', inline=False)
        
        helpEmbedChar.add_field(name=f'▫️ Pause Game Rewards', value=f'{commandPrefix}pause "character name"', inline=False)

        helpEmbedChar.add_field(name=f'▫️ Unpause Game Rewards', value=f'{commandPrefix}unpause "character name"', inline=False)



    # PRE-QUEST TIMER COMMANDS MENU ($help timer1)

    # PLAYER COMMANDS

        helpEmbedTimerOne.title = f"Pre-Quest Timer Commands\n{commandPrefix}timer, {commandPrefix}t"

        helpEmbedTimerOne.add_field(name=f'▫️ Applying to a One-shot', value=f'{commandPrefix}apply "character name" "consumable1, consumable2, [...]" "magic item1, magic item2, [...]"', inline=False)

        helpEmbedTimerOne.add_field(name=f'▫️ Signing Up (Player)', value=f'{commandPrefix}timer signup "character name" "consumable1, consumable2, [...]"', inline=False)

    # DM COMMANDS

        helpEmbedTimerOne.add_field(name=f'▫️ Preparing the Timer (DM)', value=f'{commandPrefix}timer prep "@player1, @player2, [...]" "quest name" #guild-channel-1 #guild-channel-2', inline=False)

        helpEmbedTimerOne.add_field(name=f'▫️ Adding Players to the Roster (DM)', value=f'{commandPrefix}timer add @player', inline=False)

        helpEmbedTimerOne.add_field(name=f'▫️ Removing Players from the Roster (DM)', value=f'{commandPrefix}timer remove @player', inline=False)

        helpEmbedTimerOne.add_field(name=f'▫️ Adding Guilds (DM)', value=f'{commandPrefix}timer guild #guild1, #guild2, #guild3', inline=False)

        helpEmbedTimerOne.add_field(name=f'▫️ Cancelling the Timer (DM)', value=f'{commandPrefix}timer cancel', inline=False)

        helpEmbedTimerOne.add_field(name=f'▫️ Starting the Timer (DM)', value=f'{commandPrefix}timer start', inline=False)


    # RUNNING TIMER COMMANDS MENU ($help timer2)

    # PLAYER COMMANDS

        helpEmbedTimerTwo.title = f"Running Timer Commands\n{commandPrefix}timer, {commandPrefix}t"

        helpEmbedTimerTwo.add_field(name=f'▫️ Adding Yourself (Player)', value=f'{commandPrefix}timer addme "character name" "consumable1, consumable2, [...]"', inline=False)

        helpEmbedTimerTwo.add_field(name=f'▫️ Using Items (Player)', value='- item', inline=False)

        helpEmbedTimerTwo.add_field(name=f'▫️ Removing Yourself (Player)', value=f'{commandPrefix}timer removeme', inline=False)

        helpEmbedTimerTwo.add_field(name=f'▫️ Checking the Timestamp (Player)', value=f'{commandPrefix}timer stamp', inline=False)

    # DM COMMANDS

        helpEmbedTimerTwo.add_field(name=f'▫️ Adding Players During a Quest (DM)', value=f'{commandPrefix}timer add @player "character name" "consumable1, consumable2, [...]"', inline=False)

        helpEmbedTimerTwo.add_field(name=f'▫️ Removing Players During a Quest (DM)', value=f'{commandPrefix}timer remove @player', inline=False)

        helpEmbedTimerTwo.add_field(name=f'▫️ Awarding a Random Reward Item (DM)', value=f'{commandPrefix}timer major/minor @player', inline=False)

        helpEmbedTimerTwo.add_field(name=f'▫️ Awarding Reward Items (DM)', value=f'{commandPrefix}timer reward @player "reward item1, reward item2, [...]"', inline=False)

        helpEmbedTimerTwo.add_field(name=f'▫️ Revoking Reward Items (DM)', value=f'{commandPrefix}timer undo rewards [@player1 @player2 ...]', inline=False)

        helpEmbedTimerTwo.add_field(name=f'▫️ Character Death (DM)', value=f'{commandPrefix}timer death @player', inline=False)

        helpEmbedTimerTwo.add_field(name=f'▫️ Stopping the Timer (DM)', value=f'{commandPrefix}timer stop', inline=False)


    # POST-QUEST TIMER COMMANDS MENU ($help timer3)

    # PLAYER COMMANDS

        helpEmbedTimerThree.title = f"Post-Quest Timer Commands\n{commandPrefix}timer, {commandPrefix}t"

    #    helpEmbedTimerThree.add_field(name=f'▫️ Opting Out of Guild 2x Rewards (Player)', value=f'{commandPrefix}session optout2xR gameID', inline=False)

    #    helpEmbedTimerThree.add_field(name=f'▫️ Opting Into of Guild 2x Rewards (Player)', value=f'{commandPrefix}session optin2xR gameID', inline=False)

    #    helpEmbedTimerThree.add_field(name=f'▫️ Opting Out of Guild 2x Items (Player)', value=f'{commandPrefix}session optout2xI gameID', inline=False)

    #    helpEmbedTimerThree.add_field(name=f'▫️ Opting Into of Guild 2x Items (Player)', value=f'{commandPrefix}session optin2xI gameID', inline=False)

    # DM COMMANDS

        helpEmbedTimerThree.add_field(name=f'▫️ Submitting a Session Log (DM)', value=f'{commandPrefix}session log gameID summary', inline=False)
        helpEmbedTimerThree.add_field(name=f'▫️ Set Gold Modifier (DM)', value=f'{commandPrefix}session setGuild gameID percentage', inline=False)

    #    helpEmbedTimerThree.add_field(name=f'▫️ Approve Guild 2x Rewards (DM)', value=f'{commandPrefix}session approveRewards gameID #guild-channel', inline=False)

    #    helpEmbedTimerThree.add_field(name=f'▫️ Deny Guild 2x Rewards (DM)', value=f'{commandPrefix}session denyRewards gameID #guild-channel', inline=False)

    #    helpEmbedTimerThree.add_field(name=f'▫️ Approve Guild 2x Items (DM)', value=f'{commandPrefix}session approveItems gameID #guild-channel', inline=False)

    #    helpEmbedTimerThree.add_field(name=f'▫️ Deny Guild 2x Items (DM)', value=f'{commandPrefix}session denyItems gameID #guild-channel', inline=False)

    #    helpEmbedTimerThree.add_field(name=f'▫️ Approve Recruitment Drive (DM)', value=f'{commandPrefix}approveDrive gameID #guild-channel', inline=False)

    #    helpEmbedTimerThree.add_field(name=f'▫️ Deny Recruitment Drive (DM)', value=f'{commandPrefix}session denyDrive gameID #guild-channel', inline=False)

        helpEmbedTimerThree.add_field(name=f'▫️ Opting Out of DDMRW (DM)', value=f'{commandPrefix}session ddmrw optout gameID', inline=False)

        helpEmbedTimerThree.add_field(name=f'▫️ Opting Into DDMRW (DM)', value=f'{commandPrefix}session ddmrw optin gameID', inline=False)


    # ITEM TABLE COMMANDS MENU ($help itemtable)

    ############### THIS IS OBSOLETE UNTIL YOU MAKE A NEW SYSTEM.

    #    helpEmbedItems.title = 'Item Table Commands'
    #    helpEmbedItems.add_field(name=f'▫️ Magic Item Table Lookup\n{commandPrefix}mit [optional name search]', value=f"Look up items from the Magic Item Table, sorted by tier and TP cost. React to the lists to change pages or view items. You can also search by name, for example: {commandPrefix}mit Folding Boat", inline=False)
    #    helpEmbedItems.add_field(name=f'▫️ Reward Item Table Lookup\n{commandPrefix}rit [optional name search]', value=f"Look up items from the Reward Item Table, sorted by tier and Minor/Major. React to the lists to change pages or view items. You can also search by name, for example: {commandPrefix}rit Clockwork Dog", inline=False)
    #    helpEmbedItems.add_field(name=f'▫️ Random Reward Item\n{commandPrefix}rit random', value=f"Display a random reward item based on the tier and sub-tier you selected.", inline=False)


    # TP COMMANDS MENU ($help tp)

        helpEmbedTp.title = 'TP Commands'

        helpEmbedTp.add_field(name=f'▫️ Finding a Magic Item', value=f'{commandPrefix}tp find "character name" "magic item"', inline=False)

        helpEmbedTp.add_field(name=f'▫️ Crafting a Magic Item', value=f'{commandPrefix}tp craft "character name" "magic item"', inline=False)

        helpEmbedTp.add_field(name=f'▫️ Memeing a Magic Item', value=f'{commandPrefix}tp meme "character name" "magic item"', inline=False)

        helpEmbedTp.add_field(name=f'▫️ Discarding an Incomplete Magic Item', value=f'{commandPrefix}tp discard "character name"', inline=False)

        helpEmbedTp.add_field(name=f'▫️ Abandoning Leftover TP', value=f'{commandPrefix}tp abandon "character name" tier', inline=False)

        helpEmbedTp.add_field(name=f'▫️ Upgrading a Vestige of Divergence or Arm of the Betrayer', value=f'{commandPrefix}tp upgrade "character name" "item name"', inline=False)


    # SHOP COMMANDS MENU ($help shop)

        helpEmbedShop.title = 'Shop Commands'

        helpEmbedShop.add_field(name=f'▫️ Buying a Shop Item', value=f'{commandPrefix}shop buy "character name" "item" #', inline=False)

        helpEmbedShop.add_field(name=f'▫️ Buying a Miscellaneous Item', value=f'{commandPrefix}shop buy "character name" Miscellaneous #', inline=False)

        helpEmbedShop.add_field(name=f'▫️ Selling a Mundane Item', value=f'{commandPrefix}shop sell "character name" "item" #', inline=False)

        helpEmbedShop.add_field(name=f'▫️ Tossing a Consumable or Mundane Item', value=f'{commandPrefix}shop toss "character name" "item"', inline=False)

        helpEmbedShop.add_field(name=f'▫️ Copying a Spell Scroll', value=f'{commandPrefix}shop copy "character name" "spell name"', inline=False)

        helpEmbedShop.add_field(name=f'▫️ Coating a Weapon in Silver or Adamantine', value=f'{commandPrefix}shop silver "character name" "weapon name" #\n{commandPrefix}shop adamantine', inline=False)

        helpEmbedShop.add_field(name=f'▫️ Downtime Friend Training', value=f'{commandPrefix}downtime training "character name"\n[{commandPrefix}dt training]', inline=False)

        helpEmbedShop.add_field(name=f'▫️ Downtime Noodle Training', value=f'{commandPrefix}downtime noodle "character name"\n[{commandPrefix}dt noodle]', inline=False)


    # GUILD COMMANDS MENU ($help guild)

        helpEmbedGuild.title = 'Guild Commands'

        helpEmbedGuild.add_field(name=f'▫️ Viewing a Guild’s Information', value=f'{commandPrefix}guild info #guild-channel', inline=False)

        helpEmbedGuild.add_field(name=f'▫️ Joining a Guild', value=f'{commandPrefix}guild join "character name" #guild-channel', inline=False)

        helpEmbedGuild.add_field(name=f'▫️ Increasing Your Rank', value=f'{commandPrefix}guild rankup "character name"', inline=False)

        helpEmbedGuild.add_field(name=f'▫️ Leaving a Guild', value=f'{commandPrefix}guild leave "character name"', inline=False)

        helpEmbedGuild.add_field(name=f'▫️ Creating a Guild', value=f'{commandPrefix}guild create "character name" "guild name" @guildrole #guild-channel', inline=False)

        helpEmbedGuild.add_field(name=f'▫️ Funding a Guild', value=f'{commandPrefix}guild fund "character name" #guild-channel GP', inline=False)

        helpEmbedGuild.add_field(name=f'▫️ Pinning a Message (Guildmaster only)', value=f'{commandPrefix}guild pin', inline=False)

        helpEmbedGuild.add_field(name=f'▫️ Unpinning a Message (Guildmaster only)', value=f'{commandPrefix}guild unpin', inline=False)

        helpEmbedGuild.add_field(name=f'▫️ Changing the Channel Topic (Guildmaster only)', value=f'{commandPrefix}guild topic text', inline=False)


    # CAMPAIGN COMMANDS MENU ($help campaign)

    # PLAYER CAMPAIGN COMMANDS

        helpEmbedCampaign.title = f"Campaign Commands\n{commandPrefix}c"

        helpEmbedCampaign.add_field(name=f'▫️ Viewing a Campaign’s Information', value=f'{commandPrefix}campaign info #campaign-channel', inline=False)

        helpEmbedCampaign.add_field(name=f'▫️ Signing Up (Player)', value=f'{commandPrefix}campaign timer signup', inline=False)

        helpEmbedCampaign.add_field(name=f'▫️ Adding Yourself (Player)', value=f'{commandPrefix}campaign timer addme', inline=False)

        helpEmbedCampaign.add_field(name=f'▫️ Removing Yourself (Player)', value=f'{commandPrefix}campaign timer removeme', inline=False)

        helpEmbedCampaign.add_field(name=f'▫️ Checking the Timestamp (Player)', value=f'{commandPrefix}campaign timer stamp', inline=False)

        helpEmbedCampaign.add_field(name=f'▫️ Creating a Character with a Campaign Transfer', value=f'{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]" #campaign-channel XhYm', inline=False)

        helpEmbedCampaign.add_field(name=f'▫️ Creating a Multiclass Character with a Campaign Transfer', value=f'{commandPrefix}create "character name" starting level "race" "class1 final level / class2 final level / [...]" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]" #campaign-channel XhYm', inline=False)


    # DM CAMPAIGN COMMANDS

        helpEmbedCampaign.add_field(name=f'▫️ Creating a Campaign (DM)', value=f'{commandPrefix}campaign create @campaignrole #campaign-channel', inline=False)

        helpEmbedCampaign.add_field(name=f'▫️ Adding Players to a Campaign Roster (DM)', value=f'{commandPrefix}campaign add @player #campaign-channel', inline=False)

        helpEmbedCampaign.add_field(name=f'▫️ Removing Players from a Campaign Roster (DM)', value=f'{commandPrefix}campaign remove @player #campaign-channel', inline=False)

        helpEmbedCampaign.add_field(name=f'▫️ Preparing the Timer (DM)', value=f'{commandPrefix}campaign timer prep "@player1, @player2, [...]" "session name"', inline=False)

        helpEmbedCampaign.add_field(name=f'▫️ Adding Players During a Session (DM)', value=f'{commandPrefix}campaign timer add @player', inline=False)

        helpEmbedCampaign.add_field(name=f'▫️ Removing Players During a Session (DM)', value=f'{commandPrefix}campaign timer remove @player', inline=False)

        helpEmbedCampaign.add_field(name=f'▫️ Cancelling the Timer (DM)', value=f'{commandPrefix}campaign timer cancel', inline=False)

        helpEmbedCampaign.add_field(name=f'▫️ Starting the Timer (DM)', value=f'{commandPrefix}campaign timer start', inline=False)

        helpEmbedCampaign.add_field(name=f'▫️ Stopping the Timer (DM)', value=f'{commandPrefix}campaign timer stop', inline=False)

        helpEmbedCampaign.add_field(name=f'▫️ Submitting a Campaign Log (DM)', value=f'{commandPrefix}campaign log gameID summary', inline=False)

        helpEmbedGuild.add_field(name=f'▫️ Pinning a Message', value=f'{commandPrefix}campaign pin', inline=False)

        helpEmbedGuild.add_field(name=f'▫️ Unpinning a Message', value=f'{commandPrefix}campaign unpin', inline=False)

        helpEmbedGuild.add_field(name=f'▫️ Changing the Channel Topic', value=f'{commandPrefix}campaign topic text', inline=False)




        numPages = len(helpList)
        for i in range(0, len(helpList)):
            helpList[i].set_footer(text= f"Page {i+1} of {numPages}")
        
        view = None
        
        if page == 0:
            view = AlphaView(numPages-1, ctx.author)
            
            helpMsg = await ctx.channel.send(embed=helpList[page], view = view)
            # Wait for the View to stop listening for input...
            await view.wait()
            if view.state is None:
                await helpMsg.edit(content=f"Your help menu has timed out! I'll leave this page open for you. Use the first command if you need to cycle through help menu again or use any of the other commands to view a specific help menu:\n```yaml\n{commandPrefix}help gen\n{commandPrefix}help char\n{commandPrefix}help timer1\n{commandPrefix}help timer2\n{commandPrefix}help timer3\n{commandPrefix}help shop\n{commandPrefix}help tp\n{commandPrefix}help guild\n{commandPrefix}help campaign```", view=None)
            else:
                await helpMsg.edit(embed=helpList[view.state+1], view = None)
        else:
            helpMsg = await ctx.channel.send(embed=helpList[page], view = view)
        
async def setup(bot):
    await bot.add_cog(Misc(bot))