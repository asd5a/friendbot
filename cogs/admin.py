import discord
import asyncio
import requests
import re
from discord.utils import get        
from discord.ext import commands
import sys
import traceback
from math import ceil, floor
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError
from bfunc import db, callAPI, traceBack, settingsRecord, checkForChar


def admin_or_owner():
    async def predicate(ctx):
        
        role = get(ctx.message.guild.roles, name = "A d m i n")
        output = (role in ctx.message.author.roles) or ctx.message.author.id in [220742049631174656, 203948352973438995]
        return  output
    return commands.check(predicate)

class Admin(commands.Cog, name="Admin"):
    def __init__ (self, bot):
        self.bot = bot
    async def cog_command_error(self, ctx, error):
        msg = None
        
        
        if isinstance(error, commands.BadArgument):
            # convert string to int failed
            msg = "Your parameter types were off."
        
        elif isinstance(error, commands.CheckFailure):
            msg = ""
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            msg = "You missed a parameter"

        if msg:
            
            await ctx.channel.send(msg)
        # bot.py handles this, so we don't get traceback called.
        elif isinstance(error, commands.CommandOnCooldown):
            return
        elif isinstance(error, commands.UnexpectedQuoteError) or isinstance(error, commands.ExpectedClosingQuoteError) or isinstance(error, commands.InvalidEndOfQuotedStringError):
             return

        # Whenever there's an error with the parameters that bot cannot deduce
        elif isinstance(error, commands.CommandInvokeError):
            msg = f'The command is not working correctly. Please try again and make sure the format is correct.'
            ctx.command.reset_cooldown(ctx)
            await ctx.channel.send(msg)
            await traceBack(ctx,error, False)
        else:
            ctx.command.reset_cooldown(ctx)
            await traceBack(ctx,error)
    @commands.group(case_insensitive=True)
    async def react(self, ctx):	
        pass
    
    def is_log_channel():
        async def predicate(ctx):
            return ctx.channel.category_id == settingsRecord[str(ctx.guild.id)]["Player Logs"]
        return commands.check(predicate)
    
    @react.command()
    @admin_or_owner()
    async def printGuilds(self, ctx):
        out = "All guild channels:\n"
        ch = ctx.guild.get_channel(452704598440804375)
        for channel in ch.text_channels:
            out+="  "+channel.mention+"\n"
        await ctx.channel.send(content=out)
    
    #this function allows you to specify a channel and message and have the bot react with a given emote
    #Not tested with emotes the bot might not have access to
    @react.command()
    @admin_or_owner()
    async def add(self, ctx, channel: int, msg: int, emote: str):
        ch = ctx.guild.get_channel(channel)
        message = await ch.fetch_message(msg)
        await message.add_reaction(emote)
        await ctx.message.delete()
    
    #Allows the sending of messages
    @commands.command()
    @admin_or_owner()
    async def send(self, ctx, channel: int, *, msg: str):
        ch = ctx.guild.get_channel(channel)
        await ch.send(content=msg)
    
    #this function allows you to specify a channel and message and have the bot remove its reaction with a given emote
    #Not tested with emotes the bot might not have access to
    @react.command()
    @admin_or_owner()
    async def remove(self, ctx, channel: int, msg: int, emote: str):
        ch = ctx.guild.get_channel(channel)
        message = await ch.fetch_message(msg)
        await message.remove_reaction(emote, self.bot.user)
        await ctx.message.delete()

    settingsRecord["ddmrw"]
        
    @commands.command()
    async def startDDMRW(self, ctx):
        if "Mod Friend" in [r.name for r in ctx.author.roles]:
            global settingsRecord
            settingsRecord["ddmrw"] = True
            await ctx.channel.send("Let the games begin!")

    @commands.command()
    async def endDDMRW(self, ctx):
        if "Mod Friend" in [r.name for r in ctx.author.roles]:
            global settingsRecord
            settingsRecord["ddmrw"] = False        
            await ctx.channel.send("Until next month!")
    
    
    @commands.command()
    @admin_or_owner()
    async def goldUpdate(self, ctx, tier: int, tp: int, gp: int):
        try:
            db.mit.update_many(
               {"Tier": tier, "TP": tp},
               {"$set" : {"GP" : gp}},
            )
            await ctx.channel.send(content=f"Successfully updated the GP cost of all T{tier} items costing {tp} TP to {gp} GP.")
    
        except Exception as e:
            traceback.print_exc()
            
    @commands.command()
    @admin_or_owner()
    async def tpUpdate(self, ctx, tier: int, tp: int, tp2: int):
        try:
            db.mit.update_many(
               {"Tier": tier, "TP": tp},
               {"$set" : {"TP" : tp2}},
            )
            await ctx.channel.send(content=f"Successfully updated the TP cost of all T{tier} items costing {tp} TP to {tp2} TP.")
    
        except Exception as e:
            traceback.print_exc()
            
    @commands.command()
    @admin_or_owner()
    async def printTierItems(self, ctx, tier: int, tp: int):
        try:
            items = list(db.mit.find(
               {"Tier": tier, "TP": tp},
            ))
            
            out = f"Items in Tier {tier} costing TP {tp}:\n"
            def alphaSort(item):
                if "Grouped" in item:
                    return item["Grouped"]
                else:
                    return item["Name"]
            
            items.sort(key = alphaSort)
            for i in items:
                if "Grouped" in i:
                    out += i["Grouped"]
                else:
                    out += i["Name"]
                out += f" GP {i['GP']}\n"
            length = len(out)
            while(length>2000):
                x = out[:2000]
                x = x.rsplit("\n", 1)[0]
                await ctx.channel.send(content=x)
                out = out[len(x):]
                length -= len(x)
            await ctx.channel.send(content=out)
    
        except Exception as e:
            traceback.print_exc()        
      
    @commands.command()
    @admin_or_owner()
    async def printRewardItems(self, ctx, tier: int):
        try:
            items = list(db.rit.find(
               {"Tier": tier},
            ))
            
            out = f"Reward Items in Tier {tier}:\n"
            def alphaSort(item):
                if "Grouped" in item:
                    return (item['Minor/Major'], item["Grouped"])
                else:
                    return (item['Minor/Major'], item["Name"])
            
            items.sort(key = alphaSort)
            majors = filter(lambda x: x['Minor/Major'] == "Major", items)
            minors = filter(lambda x: x['Minor/Major'] == "Minor", items)
            groups =  [[majors, "Majors"], [minors, "Minors"]]
            for g in groups:
                out += f"\n**{g[1]}**\n"
                for i in g[0]:
                    if "Grouped" in i:
                        out += i["Grouped"]
                    else:
                        out += i["Name"]
                    print(i)
                    out += f"\n"
            length = len(out)
            while(length>2000):
                x = out[:2000]
                x = x.rsplit("\n", 1)[0]
                await ctx.channel.send(content=x)
                out = out[len(x):]
                length -= len(x)
            await ctx.channel.send(content=out)
    
        except Exception as e:
            traceback.print_exc()        
    
    @commands.command()
    @commands.has_any_role('Mod Friend', 'A d m i n')
    async def removeImage(self, ctx, charName):
        charEmbed = discord.Embed()
        cRecord, charEmbedmsg = await checkForChar(ctx, charName, charEmbed, mod=True)
        channel = ctx.channel
        if not cRecord:
            await channel.send(content=f'I was not able to find the character ***"{charName}"***!')
            return False

        if charEmbedmsg:
            await charEmbedmsg.delete()
            
        try:
            db.players.update_one(
               {"Name": cRecord["Name"], "User ID": cRecord["User ID"]},
                {"$unset" : {"Image": 1}}
            )
            await channel.send(content=f"Successfully deleted the image.")
    
        except Exception as e:
            traceback.print_exc()@commands.command()
            
    @commands.command()
    @commands.has_any_role('A d m i n')
    async def removeCharacter(self, ctx, charName):
        charEmbed = discord.Embed()
        cRecord, charEmbedmsg = await checkForChar(ctx, charName, charEmbed, mod=True)
        channel = ctx.channel
        if not cRecord:
            await channel.send(content=f'I was not able to find the character ***"{charName}"***!')
            return False

        if charEmbedmsg:
            await charEmbedmsg.delete()
            
        try:
            db.players.delete_one(
               {"Name": cRecord["Name"], "User ID": cRecord["User ID"]}
            )
            await channel.send(content=f"Successfully deleted {cRecord['Name']}.")
    
        except Exception as e:
            traceback.print_exc()
            
    @commands.command()
    @admin_or_owner()
    async def ritRework(self, ctx):
        try:
            db.rit.update_many(
               {"Type": {"$exists" : False}},
                {"$set" : {"Type": "Magic Items"}}
            )
            await ctx.channel.send(content=f"Successfully updated the rit.")
    
        except Exception as e:
            traceback.print_exc()
            
    @commands.command()
    @admin_or_owner()
    async def removeAllGID(self, ctx):
        msg = await ctx.channel.send("Are you sure you want to remove every GID entry from characters in the database?\n No: ❌\n Yes: ✅")
        author = ctx.author
        
        # if( not await self.doubleVerify(ctx, msg)):
            # return
        try:
            db.players.update_many(
               {"GID": {"$exists": True}},
               {"$unset" : {"GID" : 1}},
            )
            await msg.edit(content=f"Successfully remove the GID entry from all characters.")
    
        except Exception as e:
            traceback.print_exc()
    
    
    @commands.command()
    @admin_or_owner()
    async def removeAllPlayers(self, ctx):
        msg = ctx.channel.send("Are you sure you want to remove every character in the database?\n No: ❌\n Yes: ✅")
        author = ctx.author
        
        if(not self.doubleVerify(ctx, msg)):
            return
        try:
            count = db.players.delete_many(
               {}
            )
            await msg.edit(content=f"Successfully deleted {count.deleted_count} characters.")
    
        except Exception as e:
            traceback.print_exc()
      
    @commands.command()      
    @admin_or_owner()
    async def removeUserCharacters(self, ctx, userID):
        msg = await ctx.channel.send("Are you sure you want to remove every character in the database?\n No: ❌\n Yes: ✅")
        author = ctx.author
        
        if(not await self.doubleVerify(ctx, msg)):
            return
        
        try:
            count = db.players.delete_many(
               {"User ID": userID}
            )
            print(count)
            await msg.edit(content=f"Successfully deleted {count.deleted_count} characters.")
    
        except Exception as e:
            traceback.print_exc()        
    
            
    @commands.command()
    @admin_or_owner()
    async def moveItem(self, ctx, item, tier: int, tp: int):
        
        moveEmbed = discord.Embed()
        moveEmbedmsg = None
        
        rRecord, moveEmbed, moveEmbedmsg = await callAPI(ctx, moveEmbed, moveEmbedmsg, 'mit', item)
        if(moveEmbedmsg):
            await moveEmbedmsg.edit(embed=None, content=f"Are you sure you want to move and refund {rRecord['Name']}?\n No: ❌\n Yes: ✅")
        else:
            moveEmbedmsg = await  ctx.channel.send(content=f"Are you sure you want to move and refund {rRecord['Name']}?\n No: ❌\n Yes: ✅")
        author = ctx.author
        refundTier = f'T{rRecord["Tier"]} TP'
        
        if(not await self.doubleVerify(ctx, moveEmbedmsg)):
            return
        
        try:
            targetTierInfoItem = db.mit.find_one( {"TP": tp, "Tier": tier})
            print(targetTierInfoItem)
            updatedGP = rRecord["GP"]
            if(targetTierInfoItem):
                updatedGP = targetTierInfoItem["GP"]
                
            returnData = self.characterEntryItemRemovalUpdate(ctx, rRecord, "Current Item", refundTier, tp)
                                                        
            db.mit.update_one( {"_id": rRecord["_id"]},
                                {"$set" : {"Tier" : tier, "TP" : tp, "GP": updatedGP}})
        except Exception as e:
            print("ERRORpr", e)
            traceback.print_exc()
            await traceBack(ctx,e)
            return
        
        print(returnData)
        
        refundData = list(map(lambda item: UpdateOne({'_id': item['_id']}, item['fields']), returnData))
        
        try:
            if(len(refundData)>0):
                db.players.bulk_write(refundData)
        except BulkWriteError as bwe:
            print(bwe.details)
            # if it fails, we need to cancel and use the error details
            return
        await moveEmbedmsg.edit(content="Completed")
    
    def characterEntryItemRemovalUpdate(self, ctx, rRecord, category, refundTier, tp):
        characters = list( db.players.find({"Current Item": {"$regex": f".*?{rRecord['Name']}"}}))
        returnData = []
        print(rRecord)
        for char in characters:
            print(char["Name"])
            items = char[category].split(", ")
            removeItem = None
            refundTP = 0
            for item in items:
                print(item)
                nameSplit = item.split("(")
                if(nameSplit[0].strip() == rRecord["Name"]):
                    removeItem = item
                    refundTP = float(nameSplit[1].split("/")[0])
                    
            print("Remove: ", removeItem)
            
            if(refundTier in char):
                refundTP += char[refundTier]
            if not removeItem:
                continue
                
            items.remove(removeItem)
            if(len(items)==0):
                items.append("None")
            
            entry = {'_id': char["_id"],  
                                "fields": {"$set": {refundTier: refundTP, 
                                                    category: ", ".join(items)}}}

            if("Grouped" in rRecord):
                groupedPair = rRecord["Grouped"]+" : "+rRecord["Name"]
                print(list(char["Grouped"]))
                print(groupedPair)
                updatedGrouped = list(char["Grouped"])
                updatedGrouped.remove(groupedPair)
                entry["fields"]["$set"]["Grouped"] = updatedGrouped
            
            returnData.append(entry)
        return returnData
        
    async def doubleVerify(self, ctx, embedMsg):
        def apiEmbedCheck(r, u):
            sameMessage = False
            if embedMsg.id == r.message.id:
                sameMessage = True
            return ((str(r.emoji) == '❌') or (str(r.emoji) == '✅')) and u == ctx.author and sameMessage
            
        await embedMsg.add_reaction('❌')
        try:
            tReaction, tUser = await self.bot.wait_for("reaction_add", check=apiEmbedCheck, timeout=60)
        except asyncio.TimeoutError:
            #stop if no response was given within the timeframe
            await embedMsg.edit(conten='Timed out! Try using the command again.')
            return False
        else:
            #stop if the cancel emoji was given
            if tReaction.emoji == '❌':
                await embedMsg.edit(embed=None, content=f"Command cancelled.")
                await embedMsg.clear_reactions()
                return False
            elif tReaction.emoji == '✅':
                await embedMsg.clear_reactions()
            else:
                await embedMsg.edit(embed=None, content=f"Command cancelled. Unexpected reaction given.")
                return False
        await embedMsg.edit(content=f"Since this process is irreversible, ARE YOU SURE?\n No: ❌\n Yes: ✅")
        
        await embedMsg.add_reaction('❌')
        try:
            tReaction, tUser = await self.bot.wait_for("reaction_add", check=apiEmbedCheck, timeout=60)
        except asyncio.TimeoutError:
            #stop if no response was given within the timeframe
            await embedMsg.edit(conten='Timed out! Try using the command again.')
            return False
        else:
            #stop if the cancel emoji was given
            if tReaction.emoji == '❌':
                await embedMsg.edit(embed=None, content=f"Command cancelled.")
                await embedMsg.clear_reactions()
                return False
            elif tReaction.emoji == '✅':
                await embedMsg.clear_reactions()
            else:
                await embedMsg.edit(embed=None, content=f"Command cancelled. Unexpected reaction given.")
                return False
        return True
    
    @commands.group()
    async def react(self, ctx):	
        pass
    
    
    #this function allows you to specify a channel and message and have the bot react with a given emote
    #Not tested with emotes the bot might not have access to
    @react.command()
    @admin_or_owner()
    async def add(self, ctx, channel: int, msg: int, emote: str):
        ch = ctx.guild.get_channel(channel)
        message = await ch.fetch_message(msg)
        await message.add_reaction(emote)
        await ctx.message.delete()
    
    @commands.command()
    @admin_or_owner()
    async def makeItClean(self, ctx):
        msg = await ctx.channel.send("Are you sure you want to delete basically everything?\n No: ❌\n Yes: ✅")
        author = ctx.author
        
        if( not await self.doubleVerify(ctx, msg)):
            return
        try:
            obj = db.players.delete_many(
               {}
            )
            obj2 = db.campaigns.delete_many(
               {}
            )
            obj3 = db.guilds.delete_many(
               {}
            )
            obj4 = db.users.delete_many(
               {}
            )
            obj5 = db.dead.delete_many(
               {}
            )
            obj6 = db.logdata.delete_many(
               {}
            )
            count = obj.deleted_count + obj2.deleted_count + obj3.deleted_count + obj4.deleted_count +obj5.deleted_count + obj6.deleted_count
            
            await msg.edit(content=f"Successfully deleted {count} entries.")
    
        except Exception as e:
            traceback.print_exc()
    
    @commands.command()
    @admin_or_owner()
    async def deleteStats(self, ctx):
        # if(not self.doubleVerify(ctx, msg)):
            # return
        try:
            count = db.stats.delete_many(
               {}
            )
            db.stats.insert_one({"Life": 1, "Games": 0,  "Class":{}, "Race" : {}, "Background" : {}, "Feats":{}, "Unique Players" : [], "DM":{}, "Magic Items" : {}})
            await ctx.channel.send(content=f"Successfully deleted {count.deleted_count} stat entries.")
    
        except Exception as e:
            traceback.print_exc()
    
    @commands.command()
    @admin_or_owner()
    async def updateSettings(self, ctx):
        try:
            settingsRecord.update(list(db.settings.find())[0])
            await ctx.channel.send(content=f"Settings have been updated from the DB.")
    
        except Exception as e:
            traceback.print_exc()
            
            
    
    @commands.command()
    @commands.has_any_role("Mod Friend")
    async def xfer(self, ctx, charName, level : int, cp :float, user, items = ""):
        msg = ctx.message
        rewardList = msg.raw_mentions
        rewardUser = ""
        # create an embed text object
        charEmbed = discord.Embed()
        charEmbedmsg = None
        guild = ctx.guild
        
        # if nobody was listed, inform the user
        if rewardList == list():
            await ctx.channel.send(content=f"I could not find any mention of a user to hand out a reward item.") 
            #return the unchanged parameters
            return
        else:
            rewardUser = rewardList[0]
            
            levelCP = (((level - 5) * 8) + 16)
            if level < 5:
                levelCP = ((level - 1) * 4)
            cp += levelCP
            level = 1
            maxCP = 4
            while(cp >= maxCP and level <20):
                cp -= maxCP
                level += 1
                if level > 4:
                  maxCP = 10
            
            charDict = {
              'User ID': str(rewardUser),
              'Name': charName,
              'Level': level,
              'HP': 0,
              'Class': "Friend",
              'Race': "Friend",
              'Background': "D&D Friend",
              'STR': 0,
              'DEX': 0,
              'CON': 0,
              'INT': 0,
              'WIS': 0,
              'CHA': 0,
              'CP' : cp,
              'Current Item': 'None',
              'GP': 0,
              'Magic Items': 'None',
              'Consumables': 'None',
              'Feats': 'None',
              'Inventory': {},
              'Predecessor': {},
              'Games': 0,
              'Respecc' : "Transfer"
            }
            
            
            # character level
            # since this checks for multiple things, this cannot be avoided
            tierNum=5
            # calculate the tier of the rewards
            if level < 5:
                tierNum = 1
            elif level < 11:
                tierNum = 2
            elif level < 17:
                tierNum = 3
            elif level < 20:
                tierNum = 4
                    
            items = items.strip()
            consumablesList = []
            if items != "":
                consumablesList = items.split(',')
            rewardList = {"Magic Items": [], "Consumables": [], "Inventory": []}
            for query in consumablesList:
                query = query.strip()
                # if the player is getting a spell scoll then we need to determine which spell they are going for
                # we do this by searching in the spell table instead
                if 'spell scroll' in query.lower():
                    # extract the spell
                    spellItem = query.lower().replace("spell scroll", "").replace('(', '').replace(')', '')
                    # use the callAPI function from bfunc to search the spells table in the DB for the spell being rewarded
                    sRecord, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg, 'spells', spellItem)
                    
                    # if no spell was found then we inform the user of the failure and stop the command
                    if not sRecord:
                        await ctx.channel.send(f'''**{query}** belongs to a tier which you do not have access to or it doesn't exist! Check to see if it's on the Reward Item Table, what tier it is, and your spelling.''')
                        return 

                    else:
                        # Converts number to ordinal - 1:1st, 2:2nd, 3:3rd...
                        # floor(n/10)%10!=1, this acts as an if statement to check if the number is in the teens
                        # (n%10<4), this acts as an if statement to check if the number is below 4
                        # n%10 get the last digit of the number
                        # by multiplying these number together we end up with calculation that will be 0 unless both conditions have been met, otherwise it is the digit
                        # this number x is then used as the starting point of the selection and ::4 will then select the second letter by getting the x+4 element
                        # technically it will get more, but since the string is only 8 characters it will return 2 characters always
                        # th, st, nd, rd are spread out by 4 characters in the string 
                        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(floor(n/10)%10!=1)*(n%10<4)*n%10::4])
                        # change the query to be an accurate representation
                        query = f"Spell Scroll ({ordinal(sRecord['Level'])} Level)"
                

                # search for the item in the DB with the function from bfunc
                # this does disambiguation already so if there are multiple results for the item they will have already selected which one specifically they want
                rewardConsumable, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg ,'rit',query, tier=tierNum) 
            
                #if no item could be found, return the unchanged parameters and inform the user
                if not rewardConsumable:
                    await ctx.channel.send(f'**{query}** does not seem to be a valid reward item.')
                    return 
                else:
                    if 'spell scroll' in query.lower():
                        rewardConsumable['Name'] = f"Spell Scroll ({sRecord['Name']})"
                    rewardList[rewardConsumable["Type"]].append(rewardConsumable["Name"])
            
            # turn the list of added items into the new string
            consumablesString = ", ".join(rewardList["Consumables"])
               
            # if the string is empty, turn it into none
            consumablesString += "None"*(consumablesString=="")
            
            # magic items cannot be removed so we only care about addtions
            # if we have no items and no additions, string is None
            magicItemString = ", ".join(rewardList["Magic Items"])

            # if the string is empty, turn it into none
            magicItemString += "None"*(magicItemString=="")
                
            
            # increase the relevant inventory entries and create them if necessary
            for i in rewardList["Inventory"]:
                if i in charDict["Inventory"]:
                    charDict["Inventory"][i] += 1
                else:
                    charDict["Inventory"][i] = 1
            out = {"Magic Items":magicItemString, "Consumables":consumablesString, "Inventory":charDict["Inventory"]}
            charDict["Transfer Set"] = out
            print(charDict)
        try:
            db.players.insert_one(charDict)
            await ctx.channel.send(content=f"Transfer Character has been created.")
    
        except Exception as e:
            traceback.print_exc()
    
    @commands.has_any_role("Mod Friend")
    @commands.command()
    async def setNoodles(self,ctx, user, noodles: int):
        msg = ctx.message
        rewardList = msg.raw_mentions
        channel = ctx.channel
        guild = ctx.guild
        charEmbed = discord.Embed()
        charEmbedmsg = None
        # if nobody was listed, inform the user
        if rewardList == list():
            await ctx.channel.send(content=f"I could not find any mention of a user to hand out a reward item.") 
            #return the unchanged parameters
            return 
        usersCollection = db.users
        userRecords = usersCollection.update_one({"User ID": str(rewardList[0])}, {"$set" : {"Noodles" : noodles}, "$inc" : {"Games" : 0}}, upsert= True)
        await channel.send(f"Noodles set for <@!{rewardList[0]}>")
        

    
    @commands.command()
    @admin_or_owner()
    async def giveRewards(self, ctx, charName, user, items):
        msg = ctx.message
        rewardList = msg.raw_mentions
        rewardUser = ""
        # create an embed text object
        charEmbed = discord.Embed()
        charEmbedmsg = None
        guild = ctx.guild
        
        # if nobody was listed, inform the user
        if rewardList == list():
            await ctx.channel.send(content=f"I could not find any mention of a user to hand out a reward item.") 
            #return the unchanged parameters
            return 
        else:
            rewardUser = guild.get_member(rewardList[0])
            cRecord, charEmbedmsg = await checkForChar(ctx, charName, charEmbed, rewardUser, customError=True)
            # get the first user mentioned
            
            
            
            if cRecord:
                # character level
                charLevel = int(cRecord['Level'])
                # since this checks for multiple things, this cannot be avoided
                tierNum=5
                # calculate the tier of the rewards
                if charLevel < 5:
                    tierNum = 1
                elif charLevel < 11:
                    tierNum = 2
                elif charLevel < 17:
                    tierNum = 3
                elif charLevel < 20:
                    tierNum = 4
                        
                consumablesList = items.split(',')
                rewardList = {"Magic Items": [], "Consumables": [], "Inventory": []}
                 
                for query in consumablesList:
                    query = query.strip()
                    # if the player is getting a spell scoll then we need to determine which spell they are going for
                    # we do this by searching in the spell table instead
                    if 'spell scroll' in query.lower():
                        # extract the spell
                        spellItem = query.lower().replace("spell scroll", "").replace('(', '').replace(')', '')
                        # use the callAPI function from bfunc to search the spells table in the DB for the spell being rewarded
                        sRecord, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg, 'spells', spellItem)
                        
                        # if no spell was found then we inform the user of the failure and stop the command
                        if not sRecord and not resume:
                            await ctx.channel.send(f'''**{query}** belongs to a tier which you do not have access to or it doesn't exist! Check to see if it's on the Reward Item Table, what tier it is, and your spelling.''')
                            return start, dmChar

                        else:
                            # Converts number to ordinal - 1:1st, 2:2nd, 3:3rd...
                            # floor(n/10)%10!=1, this acts as an if statement to check if the number is in the teens
                            # (n%10<4), this acts as an if statement to check if the number is below 4
                            # n%10 get the last digit of the number
                            # by multiplying these number together we end up with calculation that will be 0 unless both conditions have been met, otherwise it is the digit
                            # this number x is then used as the starting point of the selection and ::4 will then select the second letter by getting the x+4 element
                            # technically it will get more, but since the string is only 8 characters it will return 2 characters always
                            # th, st, nd, rd are spread out by 4 characters in the string 
                            ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(floor(n/10)%10!=1)*(n%10<4)*n%10::4])
                            # change the query to be an accurate representation
                            query = f"Spell Scroll ({ordinal(sRecord['Level'])} Level)"
                    

                    # search for the item in the DB with the function from bfunc
                    # this does disambiguation already so if there are multiple results for the item they will have already selected which one specifically they want
                    rewardConsumable, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg ,'rit',query, tier=tierNum) 
                
                    #if no item could be found, return the unchanged parameters and inform the user
                    if not rewardConsumable:
                        await ctx.channel.send(f'**{query}** does not seem to be a valid reward item.')
                        return 
                    else:
                       
                        if 'spell scroll' in query.lower():
                            rewardConsumable['Name'] = f"Spell Scroll ({sRecord['Name']})"
                        rewardList[rewardConsumable["Type"]].append(rewardConsumable["Name"])
                
                #if we know they didnt have any items, we know that changes could only be additions
                if(cRecord["Consumables"]=="None"):
                    # turn the list of added items into the new string
                    consumablesString = ", ".join(rewardList["Consumables"])
                else:
                    consumablesString = cRecord["Consumables"]+(", ".join(rewardList["Consumables"]))
                    
                # if the string is empty, turn it into none
                consumablesString += "None"*(consumablesString=="")
                
                # magic items cannot be removed so we only care about addtions
                # if we have no items and no additions, string is None
                if(cRecord["Magic Items"]=="None"):
                    # turn the list of added items into the new string
                    magicItemString = ", ".join(rewardList["Magic Items"])
                else:
                    magicItemString = cRecord["Magic Items"]+(", ".join(rewardList["Magic Items"]))
                    
                # if the string is empty, turn it into none
                magicItemString += "None"*(magicItemString=="")
                    
                
                # increase the relevant inventory entries and create them if necessary
                for i in rewardList["Inventory"]:
                    if i in cRecord["Inventory"]:
                        cRecord["Inventory"][i] += 1
                    else:
                        cRecord["Inventory"][i] = 1
                
                player_set = {"Consumables": consumablesString, 
                                "Magic Items": magicItemString, 
                                "Inventory" : cRecord["Inventory"]}
                     
                    
            else:
                await ctx.channel.send(content=f"I could not find {charName} in the DB.")        
                return
        try:
            db.players.update_one({"_id": cRecord["_id"]}, {"$set": player_set})
            await ctx.channel.send(content=f"Rewards items have been given.")
    
        except Exception as e:
            traceback.print_exc()
    
    @commands.command()
    @admin_or_owner()
    async def uploadSettings(self, ctx):
        try:
            settings = {
            "ddmrw" : False,
            "Test Channel IDs" : ["663454980140695553", "577611798442803205", "697974883140894780", "698220733259841656"],
            "QB List" : {"781021043778781195" : "382025597041246210", "728476108940640297" : "259732415319244800"},
            "Role Channel List" : {"777046003832193034" : "382025597041246210", "781360717101400084" : "259732415319244800"},
                    "382025597041246210": 
                    {"Sessions" : 737076677238063125, "QB" : 781021043778781195, 
                        "CB" : 382027251618938880,
                        "Player Logs" : 788158884329422848 ,
                        "Game Rooms" : 575798293913796619, 
                        "Guild Rooms" :452704598440804375,
                        "Campaign Rooms" : 698784680488730666, 
                        "Messages" : {"777051070110498846": "Roll20"," 777051209299132456": "Foundry"},
                        "Emotes" : {"Roll20" : "<:roll20:777767592684421130>" , "Foundry": "<:foundry:777767632471719956>"}}, 
                  "259732415319244800" : 
                    {"Sessions" : 728456783466725427, "QB" : 728476108940640297, 
                        "CB" : 781360342483075113,
                        "Player Logs" : 728729922205647019 ,
                        "Game Rooms" : 728456686024523810, 
                        "Guild Rooms" : 734586911901089832,
                        "Campaign Rooms" : 734276389322096700, 
                        "Messages" : {"781360780162760765": "Roll20", "781360787854852106": "Foundry"},
                        "Emotes" : {"Roll20" : "<:adorabat:733763021008273588>" , "Foundry": "🗡️"}}}

            db.settings.insert_one(settings)
            await ctx.channel.send(content=f"Settings have been updated in the DB.")
    
        except Exception as e:
            traceback.print_exc()
    #Allows the sending of messages
    @commands.command()
    @admin_or_owner()
    async def send(self, ctx, channel: int, *, msg: str):
        ch = ctx.guild.get_channel(channel)
        await ch.send(content=msg)

    #this function allows you to specify a channel and message and have the bot remove its reaction with a given emote
    #Not tested with emotes the bot might not have access to
    @react.command()
    @admin_or_owner()
    async def remove(self, ctx, channel: int, msg: int, emote: str):
        ch = ctx.guild.get_channel(channel)
        message = await ch.fetch_message(msg)
        await message.remove_reaction(emote, self.bot.user)
        await ctx.message.delete()
    
    
    @commands.command()
    @admin_or_owner()
    async def removeItem(self, ctx, item):
        
        removeEmbed = discord.Embed()
        removeEmbedmsg = None
        
        rRecord, removeEmbed, removeEmbedmsg = await callAPI(ctx, removeEmbed, removeEmbedmsg, 'mit', item)
        if(removeEmbedmsg):
            await removeEmbedmsg.edit(embed=None, content=f"Are you sure you want to remove and refund {rRecord['Name']}?\n No: ❌\n Yes: ✅")
        else:
            removeEmbedmsg = await  ctx.channel.send(content=f"Are you sure you want to move and refund {rRecord['Name']}?\n No: ❌\n Yes: ✅")
        author = ctx.author
        refundTier = f'TP {rRecord["Tier"]}'
        
        if(not await self.doubleVerify(ctx, removeEmbedmsg)):
            return
        
        try:
            returnData = self.characterEntryItemRemovalUpdate(ctx, rRecord, "Magic Items")
                                                        
            db.mit.remove_one( {"_id": rRecord["_id"]})
        except Exception as e:
            print("ERRORpr", e)
            traceback.print_exc()
            await traceBack(ctx,e)
            return
        
        print(returnData)
        
        refundData = list(map(lambda item: UpdateOne({'_id': item['_id']}, item['fields']), returnData))
        
        try:
            if(len(refundData)>0):
                db.players.bulk_write(refundData)
        except BulkWriteError as bwe:
            print(bwe.details)
            # if it fails, we need to cancel and use the error details
            return
        await removeEmbedmsg.edit(content="Completed")
        
    @commands.command()
    @admin_or_owner()
    async def killbot(self, ctx):
        await self.bot.logout()
    
    @commands.command()
    @admin_or_owner()
    async def reload(self, ctx, cog: str):
        
        try:
            self.bot.reload_extension('cogs.'+cog)
            print(f"{cog} has been reloaded.")
            await ctx.channel.send(cog+" has been reloaded")
        except commands.ExtensionNotLoaded as e:
            try:
                self.bot.load_extension("cogs." + cog)
                print(f"{cog} has been added.")
                await ctx.channel.send(cog+" has been reloaded")
            except (discord.ClientException, ModuleNotFoundError, commands.ExtensionNotFound):
                await ctx.channel.send(f'Failed to load extension {cog}.')
                traceback.print_exc()
        except Exception as e:
            await ctx.channel.send(f'Failed to load extension {cog}.')
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Admin(bot))



# Secret Admin/Dev-only Commands


# $removeCharacter "character name"
    # Deletes a character from the database.

# $reload <file name> | $reload misc
    # Hot reloads the specific cog file and updates the commands of the cog to the latest local version while resetting cooldowns and variables. This allows you to change anything in the cog folder without requiring a restart.

# $updateSettings
    # Updates the "settingsRecord" variable with the current dnd.settings collection database entry without requiring a restart.

# $genLod ID
    # Updates the specified session log with the corresponding dnd.logdata collection database entry.

# $printTierItems tier TP
    # Prints a list of magic items in the specified tier and TP.

# $printrewarditems tier
    # Prints a list of reward items in the specified tier.

# $tpupdate tier TP newTP
    # Updates all magic items in the specified tier and TP to the new TP value.

# $goldupdate tier TP newGP
    # Updates all magic items int he specified tier and TP to the new GP value.

# $moveItem "item" tier TP
    # Moves the specified magic item to the specified tier and TP and refunds all characters with partial TP towards it. It does not refund completed items and is mostly non-functional.

# $send channelID message
    # Forces Bot Friend to send a message in the specified channel.

# $react add/remove channelID messageID :emoji:
    # Forces Bot Friend to add or remove a Unicode emoji as a reaction to the specified message within a channel.

# $uwuize
    # Translates the previous message into uwu-speak.

# $killbot
    # Forcefully shuts down Bot Friend.
