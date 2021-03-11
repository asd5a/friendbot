import discord
import decimal
import pytz
import re
import random
import requests
import asyncio
import collections
from discord.utils import get        
from math import floor
from datetime import datetime, timezone, timedelta 
from discord.ext import commands
from urllib.parse import urlparse 
from bfunc import numberEmojis, alphaEmojis, commandPrefix, left,right,back, db, callAPI, checkForChar, timeConversion, traceBack, tier_reward_dictionary, cp_bound_array, calculateTreasure, settingsRecord

class Character(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        
    def is_log_channel():
        async def predicate(ctx):
            return ctx.channel.category_id == settingsRecord[str(ctx.guild.id)]["Player Logs"]
        return commands.check(predicate)
   
    def is_log_channel_or_game():
        async def predicate(ctx):
            return (ctx.channel.category_id == settingsRecord[str(ctx.guild.id)]["Player Logs"] or 
                    ctx.channel.category_id == settingsRecord[str(ctx.guild.id)]["Game Rooms"])
        return commands.check(predicate) 
        
    def stats_special():
        async def predicate(ctx):
            return (ctx.channel.category_id == settingsRecord[str(ctx.guild.id)]["Player Logs"] or 
                    ctx.channel.category_id == settingsRecord[str(ctx.guild.id)]["Mod Rooms"] or
                    ctx.channel.id == 564994370416410624)
        return commands.check(predicate) 
    async def cog_command_error(self, ctx, error):
        msg = None
        
        
        if isinstance(error, commands.BadArgument):
            # convert string to int failed
            msg = "Your stats and level need to be numbers. "
        elif isinstance(error, commands.UnexpectedQuoteError) or isinstance(error, commands.ExpectedClosingQuoteError) or isinstance(error, commands.InvalidEndOfQuotedStringError):

             return
        elif isinstance(error, commands.CheckFailure):
            msg = "This channel or user does not have permission for this command. "
        elif isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'char':
                msg = ":warning: You're missing the character name in the command.\n"
            elif error.param.name == 'new_race':
                msg = ":warning: You're missing the new race in the command.\n"
            elif error.param.name == "name":
                msg = ":warning: You're missing the name for the character you want to create or respec.\n"
            elif error.param.name == "newname":
                msg = ":warning: You're missing a new name for the character you want to respec.\n"
            elif error.param.name == "level":
                msg = ":warning: You're missing a level for the character you want to create.\n"
            elif error.param.name == "race":
                msg = ":warning: You're missing a race for the character you want to create.\n"
            elif error.param.name == "cclass":
                msg = ":warning: You're missing a class for the character you want to create.\n"
            elif error.param.name == 'bg':
                msg = ":warning: You're missing a background for the character you want to create.\n"
            elif error.param.name == 'sStr' or  error.param.name == 'sDex' or error.param.name == 'sCon' or error.param.name == 'sInt' or error.param.name == 'sWis' or error.param.name == 'sCha':
                msg = ":warning: You're missing a stat (STR, DEX, CON, INT, WIS, or CHA) for the character you want to create.\n"
            elif error.param.name == 'url':
                msg = ":warning: You're missing a URL to add an image to your character's information window.\n"
            elif error.param.name == 'm':
                msg = ":warning: You're missing a magic item to attune to, or unattune from, your character.\n"

            msg += "**Note: if this error seems incorrect, something else may be incorrect.**\n\n"

        if msg:
            if ctx.command.name == "create":
                msg += f'Please follow this format:\n```yaml\n{commandPrefix}create "name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```\n'
            elif ctx.command.name == "respec":
                msg += f'Please follow this format:\n```yaml\n{commandPrefix}respec "name" "new name" "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```\n'
            elif ctx.command.name == "retire":
                msg += f'Please follow this format:\n```yaml\n{commandPrefix}retire "character name"```\n'
            elif ctx.command.name == "reflavor":
                msg += f'Please follow this format:\n```yaml\n{commandPrefix}reflavor "character name"```\n'
            elif ctx.command.name == "death":
                msg += f'Please follow this format:\n```yaml\n{commandPrefix}death "character name"```\n'
            elif ctx.command.name == "inventory":
                msg += f'Please follow this format:\n```yaml\n{commandPrefix}inventory "character name"```\n'
            elif ctx.command.name == "info":
                msg += f'Please follow this format:\n```yaml\n{commandPrefix}info "character name"```\n'
            elif ctx.command.name == "image":
                msg += f'Please follow this format:\n```yaml\n{commandPrefix}image "character name" "URL"```\n'
            elif ctx.command.name == "levelup":
                msg += f'Please follow this format:\n```yaml\n{commandPrefix}levelup "character name"```\n'
            elif ctx.command.name == "attune":
                msg += f'Please follow this format:\n```yaml\n{commandPrefix}attune "character name" "magic item"```\n'
            elif ctx.command.name == "unattune":
                msg += f'Please follow this format:\n```yaml\n{commandPrefix}unattune "character name" "magic item"```\n'
            ctx.command.reset_cooldown(ctx)
            await ctx.channel.send(msg)
        # bot.py handles this, so we don't get traceback called.
        elif isinstance(error, commands.CommandOnCooldown):
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

    @commands.command()
    @commands.cooldown(1, 60, type=commands.BucketType.user)
    @is_log_channel()
    async def printRaces(self, ctx):
        try:
            items = list(db.races.find(
               {},
            ))
            raceEmbed = discord.Embed()
            raceEmbed.title = f"All Valid Races:\n"
            
            items.sort(key = lambda x: x["Name"])
            character = ""
            out_strings = []
            collector_string = ""
            for race in items:
                race = race["Name"]
                if race[0] == character:
                    collector_string += f"{race}\n"
                else:
                    if collector_string:
                        out_strings.append(collector_string)
                    collector_string = f"{race}\n"
                    character = race[0]
            if collector_string:
                out_strings.append(collector_string)
            for i in out_strings:
                raceEmbed.add_field(name=i[0], value= i, inline = True)
            await ctx.channel.send(embed=raceEmbed)
    
        except Exception as e:
            traceback.print_exc()   
    @is_log_channel()
    @commands.cooldown(1, float('inf'), type=commands.BucketType.user)
    @commands.command()
    async def create(self,ctx, name, level: int, race, cclass, bg, sStr : int, sDex :int, sCon:int, sInt:int, sWis:int, sCha :int, consumes="", campaignName = None, timeTransfer = None):
        name = name.strip()
        characterCog = self.bot.get_cog('Character')
        roleCreationDict = {
            'Journeyfriend':[3],
            'Elite Friend':[3],
            'True Friend':[3],
            'Ascended Friend':[3],
            'Good Noodle':[4],
            'Elite Noodle':[4,5],
            'True Noodle':[4,5,6],
            'Ascended Noodle':[4,5,6,7],
            'Immortal Noodle':[4,5,6,7,8],
            'Eternal Noodle':[4,5,6,7,8,9]
            #'Friend Fanatic': [11,10,9],
            #'Guild Fanatic':[11,10,9]
        }
        roles = [r.name for r in ctx.author.roles]
        author = ctx.author
        guild = ctx.guild
        channel = ctx.channel
        charEmbed = discord.Embed ()
        charEmbed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        charEmbed.set_footer(text= "React with ❌ to cancel.\nPlease react with a choice even if no reactions appear.")
        charEmbedmsg = None
        statNames = ['STR','DEX','CON','INT','WIS','CHA']

        charDict = {
          'User ID': str(author.id),
          'Name': name,
          'Level': int(level),
          'HP': 0,
          'Class': cclass,
          'Background': bg,
          'STR': int(sStr),
          'DEX': int(sDex),
          'CON': int(sCon),
          'INT': int(sInt),
          'WIS': int(sWis),
          'CHA': int(sCha),
          'CP' : 0,
          'Current Item': 'None',
          'GP': 0,
          'Magic Items': 'None',
          'Consumables': 'None',
          'Feats': 'None',
          'Inventory': {},
          'Predecessor': {},
          'Games': 0
        }

        # Prevents name, level, race, class, background from being blank. Resets infinite cooldown and prompts
        if not name:
            await channel.send(content=":warning: The name of your character cannot be blank! Please try again.\n")
            self.bot.get_command('create').reset_cooldown(ctx)
            return

        if not level:
            await channel.send(content=":warning: The level of your character cannot be blank! Please try again.\n")

            self.bot.get_command('create').reset_cooldown(ctx)
            return

        if not race:
            await channel.send(content=":warning: The race of your character cannot be blank! Please try again.\n")
            self.bot.get_command('create').reset_cooldown(ctx)
            return

        if not cclass:
            await channel.send(content=":warning: The class of your character cannot be blank! Please try again.\n")
            self.bot.get_command('create').reset_cooldown(ctx)
            return
        
        if not bg:
            await channel.send(content=":warning: The background of your character cannot be blank! Please try again.\n")
            self.bot.get_command('create').reset_cooldown(ctx)
            return


        lvl = int(level)
        # Provides an error message at the end. If there are more than one, it will join msg.
        msg = ""

        
        # Name should be less then 65 chars
        if len(name) > 64:
            msg += ":warning: Your character's name is too long! The limit is 64 characters.\n"

        # Reserved for regex, lets not use these for character names please
        invalidChars = ["[", "]", "?", '"', "\\", "*", "$", "{", "+", "}", "^", ">", "<", "|"]

        for i in invalidChars:
            if i in name:
                msg += f":warning: Your character's name cannot contain `{i}`. Please revise your character name.\n"


        if msg == "":
            query = name
            query = query.replace('(', '\\(')
            query = query.replace(')', '\\)')
            query = query.replace('.', '\\.')
            playersCollection = db.players
            userRecords = list(playersCollection.find({"User ID": str(author.id), "Name": {"$regex": f"^{query}$", '$options': 'i' } }))

            if userRecords != list():
                msg += f":warning: You already have a character by the name of ***{name}***! Please use a different name.\n"
        
        # ██████╗░░█████╗░██╗░░░░░███████╗  ░░░░██╗  ██╗░░░░░███████╗██╗░░░██╗███████╗██╗░░░░░
        # ██╔══██╗██╔══██╗██║░░░░░██╔════╝  ░░░██╔╝  ██║░░░░░██╔════╝██║░░░██║██╔════╝██║░░░░░
        # ██████╔╝██║░░██║██║░░░░░█████╗░░  ░░██╔╝░  ██║░░░░░█████╗░░╚██╗░██╔╝█████╗░░██║░░░░░
        # ██╔══██╗██║░░██║██║░░░░░██╔══╝░░  ░██╔╝░░  ██║░░░░░██╔══╝░░░╚████╔╝░██╔══╝░░██║░░░░░
        # ██║░░██║╚█████╔╝███████╗███████╗  ██╔╝░░░  ███████╗███████╗░░╚██╔╝░░███████╗███████╗
        # ╚═╝░░╚═╝░╚════╝░╚══════╝╚══════╝  ╚═╝░░░░  ╚══════╝╚══════╝░░░╚═╝░░░╚══════╝╚══════╝

        # Check if level or roles are vaild
        # A set that filters valid levels depending on user's roles
        roleSet = [1]
        for d in roleCreationDict.keys():
            if d in roles:
                roleSet += roleCreationDict[d]

        roleSet = set(roleSet)

        # If roles are present, add base levels + 1 for extra levels for these special roles.
        if ("Nitro Booster" in roles):
            roleSet = roleSet.union(set(map(lambda x: x+1,roleSet.copy())))

        if ("Bean Friend" in roles):
            roleSet = roleSet.union(set(map(lambda x: x+1,roleSet.copy())))
            roleSet = roleSet.union(set(map(lambda x: x+1,roleSet.copy())))
          
        if lvl not in roleSet:
            msg += f":warning: You cannot create a character of **{lvl}**! You do not have the correct role!\n"
        
        # Checks CP
        if lvl < 5:
            maxCP = 4
        else:
            maxCP = 10
        cp = 0
        cpTransfered = 0
        campaignTransferSuccess = False
        if campaignName:
            campaignChannels = ctx.message.channel_mentions
            if len(campaignChannels) > 1 or campaignChannels == list():
                msg += f":warning: I could not find which campaign channel you want!\n"
            else:
                userRecords = db.users.find_one({"User ID" : str(author.id)})
                campaignFind = False
                if not userRecords:
                    msg += f":warning: I could not find you in the database!\n"
                elif "Campaigns" not in userRecords.keys():
                    pass
                else:
                    for key in userRecords["Campaigns"].keys():
                        if key.lower() == (campaignChannels[0].name.replace('-', ' ')):
                            campaignFind = True
                            campaignKey = key
                            break
                    if not campaignFind:
                        msg += f":warning: I could not find {campaignChannels[0].mention} in your records!\n"
                    else:
                        def convert_to_seconds(s):
                            return int(s[:-1]) * seconds_per_unit[s[-1]]

                        seconds_per_unit = { "m": 60, "h": 3600 }
                        lowerTimeString = timeTransfer.lower()
                        l = list((re.findall('.*?[hm]', lowerTimeString)))
                        totalTime = 0
                        for timeItem in l:
                            totalTime += convert_to_seconds(timeItem)
                        if userRecords["Campaigns"][campaignKey]["Time"]< 3600*4 or totalTime > userRecords["Campaigns"][campaignKey]["Time"]:
                            msg += f":warning: You do not have enough hours to transfer from {campaignChannels[0].mention}!\n"
                        else:
                            cp = ((totalTime) // 1800) / 2
                            cpTransfered = cp
                            while(cp >= maxCP and lvl <20):
                                cp -= maxCP
                                lvl += 1
                                if lvl > 4:
                                    maxCP = 10
                            campaignTransferSuccess = True
                            charDict["Level"] = lvl
                            
        charDict['CP'] = cp
        
        levelCP = (((lvl-5) * 10) + 16)
        if lvl < 5:
            levelCP = ((lvl -1) * 4)
        cp_tp_gp_array = calculateTreasure(1, 0, 1, (levelCP+cp)*3600)
        totalGP = cp_tp_gp_array[2]
        bankTP = []
        bankTP = cp_tp_gp_array[1]
        tpBank = [0,0,0,0,0]
        #grab the available TP of the character
        for x in range(1,6):
            if f'T{x} TP' in bankTP.keys():
                tpBank[x-1] = (float(bankTP[f'T{x} TP']))
        
        tierNum = 5
        # calculate the tier of the rewards
        if lvl < 5:
            tierNum = 1
        elif lvl < 11:
            tierNum = 2
        elif lvl < 17:
            tierNum = 3
        elif lvl < 20:
            tierNum = 4
        
        # Stats - Point Buy
        if msg == "":
            statsArray = [int(sStr), int(sDex), int(sCon), int(sInt), int(sWis), int(sCha)]
            
            totalPoints = 0
            for s in statsArray:
                if (13-s) < 0:
                    totalPoints += ((s - 13) * 2) + 5
                else:
                    totalPoints += (s - 8)
                    
            if any([s < 8 for s in statsArray]):
                msg += f":warning: You have at least one stat below the minimum of 8.\n"
            if totalPoints != 27:
                msg += f":warning: Your stats do not add up to 27 using point buy ({totalPoints}/27). Remember that you must list your stats before applying racial modifiers! Please check your point allocation using this calculator: <https://chicken-dinner.com/5e/5e-point-buy.html>\n"
            
        
        
        # ███╗░░░███╗░█████╗░░██████╗░██╗░█████╗░  ██╗████████╗███████╗███╗░░░███╗  ░░░░██╗  ████████╗██████╗░
        # ████╗░████║██╔══██╗██╔════╝░██║██╔══██╗  ██║╚══██╔══╝██╔════╝████╗░████║  ░░░██╔╝  ╚══██╔══╝██╔══██╗
        # ██╔████╔██║███████║██║░░██╗░██║██║░░╚═╝  ██║░░░██║░░░█████╗░░██╔████╔██║  ░░██╔╝░  ░░░██║░░░██████╔╝
        # ██║╚██╔╝██║██╔══██║██║░░╚██╗██║██║░░██╗  ██║░░░██║░░░██╔══╝░░██║╚██╔╝██║  ░██╔╝░░  ░░░██║░░░██╔═══╝░
        # ██║░╚═╝░██║██║░░██║╚██████╔╝██║╚█████╔╝  ██║░░░██║░░░███████╗██║░╚═╝░██║  ██╔╝░░░  ░░░██║░░░██║░░░░░
        # ╚═╝░░░░░╚═╝╚═╝░░╚═╝░╚═════╝░╚═╝░╚════╝░  ╚═╝░░░╚═╝░░░╚══════╝╚═╝░░░░░╚═╝  ╚═╝░░░░  ░░░╚═╝░░░╚═╝░░░░░
        # Magic Item / TP
        # Check if magic items exist, and calculates the TP cost of each magic item.
        mItems = ""
        magicItems = mItems.strip().split(',')
        allMagicItemsString = []


        # ██████╗░███████╗░██╗░░░░░░░██╗░█████╗░██████╗░██████╗░  ██╗████████╗███████╗███╗░░░███╗░██████╗
        # ██╔══██╗██╔════╝░██║░░██╗░░██║██╔══██╗██╔══██╗██╔══██╗  ██║╚══██╔══╝██╔════╝████╗░████║██╔════╝
        # ██████╔╝█████╗░░░╚██╗████╗██╔╝███████║██████╔╝██║░░██║  ██║░░░██║░░░█████╗░░██╔████╔██║╚█████╗░
        # ██╔══██╗██╔══╝░░░░████╔═████║░██╔══██║██╔══██╗██║░░██║  ██║░░░██║░░░██╔══╝░░██║╚██╔╝██║░╚═══██╗
        # ██║░░██║███████╗░░╚██╔╝░╚██╔╝░██║░░██║██║░░██║██████╔╝  ██║░░░██║░░░███████╗██║░╚═╝░██║██████╔╝
        # ╚═╝░░╚═╝╚══════╝░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝╚═╝░░╚═╝╚═════╝░  ╚═╝░░░╚═╝░░░╚══════╝╚═╝░░░░░╚═╝╚═════╝░
        # Reward Items
        if msg == "":
            rewardItems = consumes.strip().split(',')
            allRewardItemsString = []
            if rewardItems != ['']:
                for r in rewardItems:
                    if "spell scroll" in r.lower():
                        if "spell scroll" == r.lower().strip():
                            msg += f"""Please be more specific with the type of spell scroll which you're purchasing. You must format spell scrolls as follows: "Spell Scroll (spell name)".\n"""
                            break 
                            
                        spellItem = r.lower().replace("spell scroll", "").replace('(', '').replace(')', '')
                        sRecord, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg, 'spells', spellItem) 
                        
                        if not sRecord :
                            msg += f'''**{r}** belongs to a tier which you do not have access to or it doesn't exist! Check to see if it's on the Reward Item Table, what tier it is, and your spelling.'''
                            

                        else:
                            
                            ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(floor(n/10)%10!=1)*(n%10<4)*n%10::4])
                            # change the query to be an accurate representation
                            r = f"Spell Scroll ({ordinal(sRecord['Level'])} Level)"

                    reRecord, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg, 'rit',r, tier = tierNum) 

                    if charEmbedmsg == "Fail":
                        return
                    if not reRecord:
                        msg += f" {r} belongs to a tier which you do not have access to or it doesn't exist! Check to see if it's on the Reward Item Table, what tier it is, and your spelling.\n"
                        break
                    else:
                        
                        if 'spell scroll' in r.lower():
                            reRecord['Name'] = f"Spell Scroll ({sRecord['Name']})"
                        allRewardItemsString.append(reRecord)
                allRewardItemsString.sort(key=lambda x: x["Tier"])
                tier1CountMNC = 0
                rewardConsumables = []
                rewardMagics = []
                rewardInv = []
                tierRewards = [[], [], [], [], []]
                tierConsumableCounts = [0,0,0,0,0]
                if 'Good Noodle' in roles:
                    tierConsumableCounts[0] = 1
                elif 'Elite Noodle' in roles:
                    tierConsumableCounts[0] = 1
                    tierConsumableCounts[1] = 1
                elif 'True Noodle' in roles:
                    tierConsumableCounts[0] = 1
                    tierConsumableCounts[2] = 1
                elif 'Ascended Noodle' in roles:
                    tierConsumableCounts[0] = 1
                    tierConsumableCounts[1] = 1
                    tierConsumableCounts[2] = 1
                elif 'Immortal Noodle' in roles:
                    tierConsumableCounts[0] = 1
                    tierConsumableCounts[1] = 2
                    tierConsumableCounts[2] = 1
                elif 'Eternal Noodle' in roles:
                    tierConsumableCounts[0] = 1
                    tierConsumableCounts[1] = 2
                    tierConsumableCounts[2] = 2

                if 'Nitro Booster' in roles:
                    tierConsumableCounts[0] += 2

                if 'Bean Friend' in roles:
                    tierConsumableCounts[0] += 2
                    tierConsumableCounts[tierNum] += 2
                startCounts = tierConsumableCounts.copy()
                startCounts[0] = 0
                startt1MNC = tierConsumableCounts[0]

                for item in allRewardItemsString:
                    
                    if item['Minor/Major'] == 'Minor' and item["Type"] == 'Magic Items':
                        item['Tier'] -= 1
                    i = item["Tier"]
                    while i < len(tierConsumableCounts):
                        if tierConsumableCounts[i] > 0 or i == len(tierConsumableCounts)-1:
                            tierConsumableCounts[i] -= 1
                            break
                        i += 1
                    
                    if item["Tier"] > tierNum:
                        msg += ":warning: One or more of these reward items cannot be acquired at Level " + str(lvl) + ".\n"
                        break
                    elif item["Type"] == 'Consumables':
                      rewardConsumables.append(item)
                    elif item["Type"] == 'Magic Items':
                      rewardMagics.append(item)
                    else:
                        rewardInv.append(item)


                if tier1CountMNC < 0 or any([count < 0 for count in tierConsumableCounts]):
                    msg += f":warning: You do not have the right roles for these reward items. You can only choose **{startt1MNC}** Tier 1 (Non-Consumable) item(s)"
                    z = 0
                    for amount in startCounts:
                        if amount > 0:
                            msg += f", and **{amount}** Tier {z} (or lower) item(s)"
                        z += 1
                    msg += "\n"
                else:
                    for r in rewardConsumables:
                        if charDict['Consumables'] != "None":
                            charDict['Consumables'] += ', ' + r['Name']
                        else:
                            charDict['Consumables'] = r['Name']
                    for r in rewardMagics:
                        if charDict['Magic Items'] != "None":
                            charDict['Magic Items'] += ', ' + r['Name']
                        else:
                            charDict['Magic Items'] = r['Name']
                    for r in rewardInv:
                        if r["Name"] in charDict['Inventory'].keys():
                            charDict['Inventory'][r['Name']] +=1
                        else:
                            charDict['Inventory'][r['Name']] =1
                      
        # ██████╗░░█████╗░░█████╗░███████╗░░░  ░█████╗░██╗░░░░░░█████╗░░██████╗░██████╗
        # ██╔══██╗██╔══██╗██╔══██╗██╔════╝░░░  ██╔══██╗██║░░░░░██╔══██╗██╔════╝██╔════╝
        # ██████╔╝███████║██║░░╚═╝█████╗░░░░░  ██║░░╚═╝██║░░░░░███████║╚█████╗░╚█████╗░
        # ██╔══██╗██╔══██║██║░░██╗██╔══╝░░██╗  ██║░░██╗██║░░░░░██╔══██║░╚═══██╗░╚═══██╗
        # ██║░░██║██║░░██║╚█████╔╝███████╗╚█║  ╚█████╔╝███████╗██║░░██║██████╔╝██████╔╝
        # ╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚══════╝░╚╝  ░╚════╝░╚══════╝╚═╝░░╚═╝╚═════╝░╚═════╝░
        # check race
        
        if msg == "":
            rRecord, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg, 'races',race)
            if charEmbedmsg == "Fail":
                return
            if not rRecord:
                msg += f'• {race} isn\'t on the list or it is banned! Check #allowed-and-banned-content and check your spelling.\n'
            else:
                charDict['Race'] = rRecord['Name']

        
        # Check Character's class
        classStat = []
        cRecord = []
        totalLevel = 0
        mLevel = 0
        broke = []
        # If there's a /, character is creating a multiclass character
        if '/' in cclass:
            multiclassList = cclass.replace(' ', '').split('/')
            # Iterates through the multiclass list 
            
            for m in multiclassList:
                # Separate level and class
                mLevel = re.search('\d+', m)
                if not mLevel:
                    msg += ":warning: You are missing the level for your multiclass class. Please check your format.\n"

                    break
                mLevel = mLevel.group()
                mClass, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg,'classes',m[:len(m) - len(mLevel)])
                if not mClass:
                    cRecord = None
                    broke.append(m[:len(m) - len(mLevel)])

                # Check for class duplicates (ex. Paladin 1 / Paladin 2 = Paladin 3)
                classDupe = False
                if(cRecord or cRecord==list()):
                    for c in cRecord:
                        if c['Class'] == mClass:
                            c['Level'] = str(int(c['Level']) + int(mLevel))
                            classDupe = True                    
                            break

                    if not classDupe:
                        cRecord.append({'Class': mClass, 'Level':mLevel})
                    totalLevel += int(mLevel)

        else:
            singleClass, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg, 'classes',cclass)
            if singleClass:
                cRecord.append({'Class':singleClass, 'Level':lvl, 'Subclass': 'None'})
            else:
                cRecord = None
                broke.append(cclass)

        charDict['Class'] = ""
        if not mLevel and '/' in cclass:
            pass
        elif len(broke)>0:
            msg += f':warning: **{broke}** isn\'t on the list or it is banned! Check #allowed-and-banned-content and check your spelling.\n'
        elif totalLevel != lvl and len(cRecord) > 1:
            msg += ':warning: Your classes do not add up to the total level. Please double-check your multiclasses.\n'
        elif msg == "":
            #cRecord = sorted(cRecord, key = lambda i: i['Level'], reverse=True) 

            # starting equipment
            def alphaEmbedCheck(r, u):
                sameMessage = False
                if charEmbedmsg.id == r.message.id:
                    sameMessage = True
                return sameMessage and ((r.emoji in alphaEmojis[:alphaIndex]) or (str(r.emoji) == '❌')) and u == author

            if 'Starting Equipment' in cRecord[0]['Class'] and msg == "":
                startEquipmentLength = 0
                if not charEmbedmsg:
                    charEmbedmsg = await channel.send(embed=charEmbed)
                elif charEmbedmsg == "Fail":
                    msg += ":warning: You have either cancelled the command or a value was not found."
                else:
                    await charEmbedmsg.edit(embed=charEmbed)

                for item in cRecord[0]['Class']['Starting Equipment']:
                    seTotalString = ""
                    alphaIndex = 0
                    for seList in item:
                        seString = []
                        for elk, elv in seList.items():
                            if 'Pack' in elk:
                                seString.append(f"{elk} x1")
                            else:
                                seString.append(f"{elk} x{elv}")
                                
                        seTotalString += f"{alphaEmojis[alphaIndex]}: {', '.join(seString)}\n"
                        alphaIndex += 1

                    await charEmbedmsg.clear_reactions()
                    charEmbed.add_field(name=f"Starting Equipment: {startEquipmentLength+ 1} of {len(cRecord[0]['Class']['Starting Equipment'])}", value=seTotalString, inline=False)
                    await charEmbedmsg.edit(embed=charEmbed)
                    if len(item) > 1:
                        for num in range(0,alphaIndex): await charEmbedmsg.add_reaction(alphaEmojis[num])
                        await charEmbedmsg.add_reaction('❌')
                        try:
                            tReaction, tUser = await self.bot.wait_for("reaction_add", check=alphaEmbedCheck, timeout=60)
                        except asyncio.TimeoutError:
                            await charEmbedmsg.delete()
                            await channel.send(f'Character creation timed out! Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                            self.bot.get_command('create').reset_cooldown(ctx)
                            return 
                        else:
                            if tReaction.emoji == '❌':
                                await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                                await charEmbedmsg.clear_reactions()
                                self.bot.get_command('create').reset_cooldown(ctx)
                                return 
                        startEquipmentItem = item[alphaEmojis.index(tReaction.emoji)]
                    else:
                        startEquipmentItem = item[0]

                    await charEmbedmsg.clear_reactions()

                    seiString = ""
                    for seik, seiv in startEquipmentItem.items():
                        seiString += f"{seik} x{seiv}\n"
                        if "Pack" in seik:
                            seiString = f"{seik}:\n"
                            for pk, pv in seiv.items():
                                charDict['Inventory'][pk] = pv
                                seiString += f"+ {pk} x{pv}\n"

                    charEmbed.set_field_at(startEquipmentLength, name=f"Starting Equipment: {startEquipmentLength + 1} of {len(cRecord[0]['Class']['Starting Equipment'])}", value=seiString, inline=False)
                    
                    for k,v in startEquipmentItem.items():
                        if '[' in k and ']' in k:
                            iType = k.split('[')
                            invCollection = db.shop
                            if 'Instrument' in iType[1]:
                                charInv = list(invCollection.find({"Type": {'$all': [re.compile(f".*{iType[1].replace(']','')}.*")]}}))
                            else:
                                charInv = list(invCollection.find({"Type": {'$all': [re.compile(f".*{iType[0]}.*"),re.compile(f".*{iType[1].replace(']','')}.*")]}}))

                            charInv = sorted(charInv, key = lambda i: i['Name']) 

                            typeEquipmentList = []
                            for i in range (0,int(v)):
                                charInvString = f"Please choose from the choices below for {iType[0]} {i+1}:\n"
                                alphaIndex = 0
                                charInv = list(filter(lambda c: 'Yklwa' not in c['Name'] and 'Light Repeating Crossbow' not in c['Name'] and 'Double-Bladed Scimitar' not in c['Name'] and 'Oversized Longbow' not in c['Name'], charInv))
                                for c in charInv:
                                    charInvString += f"{alphaEmojis[alphaIndex]}: {c['Name']}\n"
                                    alphaIndex += 1

                                charEmbed.set_field_at(startEquipmentLength, name=f"Starting Equipment: {startEquipmentLength+1} of {len(cRecord[0]['Class']['Starting Equipment'])}", value=charInvString, inline=False)
                                await charEmbedmsg.clear_reactions()
                                await charEmbedmsg.add_reaction('❌')
                                await charEmbedmsg.edit(embed=charEmbed)

                                try:
                                    tReaction, tUser = await self.bot.wait_for("reaction_add", check=alphaEmbedCheck, timeout=60)
                                except asyncio.TimeoutError:
                                    await charEmbedmsg.delete()
                                    await channel.send(f'Character creation timed out! Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                                    self.bot.get_command('create').reset_cooldown(ctx)
                                    return 
                                else:
                                    if tReaction.emoji == '❌':
                                        await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                                        await charEmbedmsg.clear_reactions()
                                        self.bot.get_command('create').reset_cooldown(ctx)
                                        return 
                                
                                
                                p = 0
                                for a in charInv:
                                    p+=1
                                typeEquipmentList.append(charInv[alphaEmojis.index(tReaction.emoji)]['Name'])
                            typeCount = collections.Counter(typeEquipmentList)
                            typeString = ""
                            for tk, tv in typeCount.items():
                                if tk in charDict['Inventory']:
                                    charDict['Inventory'][tk] += tv
                                else:
                                    charDict['Inventory'][tk] = tv
                                
                                typeString += f"{tk} x{charDict['Inventory'][tk]}\n"

                            charEmbed.set_field_at(startEquipmentLength, name=f"Starting Equipment: {startEquipmentLength+1} of {len(cRecord[0]['Class']['Starting Equipment'])}", value=seiString.replace(f"{k} x{v}\n", typeString), inline=False)

                        elif 'Pack' not in k:
                            
                            if k in charDict['Inventory']:
                                charDict['Inventory'][k] += v
                            else:
                                charDict['Inventory'][k] = v
                                
                    startEquipmentLength += 1
                await charEmbedmsg.clear_reactions()
                charEmbed.clear_fields()

            # Subclass
            for m in cRecord:
                m['Subclass'] = 'None'
                if int(m['Level']) < lvl:
                    className = f'{m["Class"]["Name"]} {m["Level"]}'
                else:
                    className = f'{m["Class"]["Name"]}'

                classStatName = f'{m["Class"]["Name"]}'

                if int(m['Class']['Subclass Level']) <= int(m['Level']) and msg == "":
                    subclassesList = m['Class']['Subclasses'].split(',')
                    subclass, charEmbedmsg = await characterCog.chooseSubclass(ctx, subclassesList, m['Class']['Name'], charEmbed, charEmbedmsg)
                    if not subclass:
                        return

                    m['Subclass'] = f'{className} ({subclass})' 
                    classStat.append(f'{classStatName}-{subclass}')


                    if charDict['Class'] == "": 
                        charDict['Class'] = f'{className} ({subclass})'
                    else:
                        charDict['Class'] += f' / {className} ({subclass})'
                else:
                    classStat.append(classStatName)
                    if charDict['Class'] == "": 
                        charDict['Class'] = className
                    else:
                        charDict['Class'] += f' / {className}'
        # check bg and gp

        def bgTopItemCheck(r, u):
            sameMessage = False
            if charEmbedmsg.id == r.message.id:
                sameMessage = True
            return ((r.emoji in alphaEmojis[:alphaIndexTop]) or (str(r.emoji) == '❌')) and u == author and sameMessage

        def bgItemCheck(r, u):
            sameMessage = False
            if charEmbedmsg.id == r.message.id:
                sameMessage = True
            return ((r.emoji in alphaEmojis[:alphaIndex]) or (str(r.emoji) == '❌')) and u == author and sameMessage


        if msg == "":
            bRecord, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg, 'backgrounds',bg)

            if charEmbedmsg == "Fail":
                self.bot.get_command('create').reset_cooldown(ctx)
                return
            if not bRecord:
                msg += f':warning: **{bg}** isn\'t on the list or it is banned! Check #allowed-and-banned-content and check your spelling.\n'
            else:
                charDict['Background'] = bRecord['Name']

                # TODO: make function for inputing in inventory
                # Background items: goes through each background and give extra items for inventory.
                
                for e in bRecord['Equipment']:
                    beTopChoiceList = []
                    beTopChoiceKeys = []
                    alphaIndexTop = 0
                    beTopChoiceString = ""
                    for ek, ev in e.items():
                        if type(ev) == dict:
                            beTopChoiceKeys.append(ek)
                            beTopChoiceList.append(ev)
                            beTopChoiceString += f"{alphaEmojis[alphaIndexTop]}: {ek}\n"
                            alphaIndexTop += 1
                        else:
                            if charDict['Inventory'] == "None":
                                charDict['Inventory'] = {ek : int(ev)}
                            else:
                                if ek not in charDict['Inventory']:
                                    charDict['Inventory'][ek] = int(ev)
                                else:
                                    charDict['Inventory'][ek] += int(ev)

                    if len(beTopChoiceList) > 0:
                        # Lets user pick between top choices (ex. Game set or Musical Instrument. Then a followup choice.)
                        if len(beTopChoiceList) > 1:
                            charEmbed.add_field(name=f"Your {bRecord['Name']} background lets you choose one type.", value=beTopChoiceString, inline=False)
                            if not charEmbedmsg:
                                charEmbedmsg = await channel.send(embed=charEmbed)
                            else:
                                await charEmbedmsg.edit(embed=charEmbed)

                            await charEmbedmsg.add_reaction('❌')
                            try:
                                tReaction, tUser = await self.bot.wait_for("reaction_add", check=bgTopItemCheck , timeout=60)
                            except asyncio.TimeoutError:
                                await charEmbedmsg.delete()
                                await channel.send(f'Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                                self.bot.get_command('create').reset_cooldown(ctx)
                                return
                            else:
                                await charEmbedmsg.clear_reactions()
                                if tReaction.emoji == '❌':
                                    await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                                    await charEmbedmsg.clear_reactions()
                                    self.bot.get_command('create').reset_cooldown(ctx)
                                    return

                            beTopValues = beTopChoiceList[alphaEmojis.index(tReaction.emoji)]
                            beTopKey = beTopChoiceKeys[alphaEmojis.index(tReaction.emoji)]
                        elif len(beTopChoiceList) == 1:
                            beTopValues = beTopChoiceList[0]
                            beTopKey = beTopChoiceKeys[0]

                        beChoiceString = ""
                        alphaIndex = 0
                        beList = []

                        if 'Pack' in beTopKey:
                          for c in beTopValues:
                              if charDict['Inventory'] == "None":
                                  charDict['Inventory'] = {c : 1}
                              else:
                                  if c not in charDict['Inventory']:
                                      charDict['Inventory'][c] = 1
                                  else:
                                      charDict['Inventory'][c] += 1
                        else:
                            for c in beTopValues:
                                beChoiceString += f"{alphaEmojis[alphaIndex]}: {c}\n"
                                beList.append(c)
                                alphaIndex += 1

                            charEmbed.add_field(name=f"Your {bRecord['Name']} background lets you choose one {beTopKey}.", value=beChoiceString, inline=False)
                            if not charEmbedmsg:
                                charEmbedmsg = await channel.send(embed=charEmbed)
                            else:
                                await charEmbedmsg.edit(embed=charEmbed)

                            await charEmbedmsg.add_reaction('❌')
                            try:
                                tReaction, tUser = await self.bot.wait_for("reaction_add", check=bgItemCheck , timeout=60)
                            except asyncio.TimeoutError:
                                await charEmbedmsg.delete()
                                await channel.send(f'Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                                self.bot.get_command('create').reset_cooldown(ctx)
                                return
                            else:
                                await charEmbedmsg.clear_reactions()
                                if tReaction.emoji == '❌':
                                    await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                                    await charEmbedmsg.clear_reactions()
                                    self.bot.get_command('create').reset_cooldown(ctx)
                                    return
                                beKey = beList[alphaEmojis.index(tReaction.emoji)]
                                if charDict['Inventory'] == "None":
                                    charDict['Inventory'] = {beKey : 1}
                                else:
                                    if beKey not in charDict['Inventory']:
                                        charDict['Inventory'][beKey] = 1
                                    else:
                                        charDict['Inventory'][beKey] += 1

                        charEmbed.clear_fields()
                
                charDict['GP'] = int(bRecord['GP']) + totalGP
        
        # ░██████╗████████╗░█████╗░████████╗░██████╗░░░  ███████╗███████╗░█████╗░████████╗░██████╗
        # ██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██╔════╝░░░  ██╔════╝██╔════╝██╔══██╗╚══██╔══╝██╔════╝
        # ╚█████╗░░░░██║░░░███████║░░░██║░░░╚█████╗░░░░  █████╗░░█████╗░░███████║░░░██║░░░╚█████╗░
        # ░╚═══██╗░░░██║░░░██╔══██║░░░██║░░░░╚═══██╗██╗  ██╔══╝░░██╔══╝░░██╔══██║░░░██║░░░░╚═══██╗
        # ██████╔╝░░░██║░░░██║░░██║░░░██║░░░██████╔╝╚█║  ██║░░░░░███████╗██║░░██║░░░██║░░░██████╔╝
        # ╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝░░░╚═╝░░░╚═════╝░░╚╝  ╚═╝░░░░░╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚═════╝░
        # Stats - Point Buy
        
        if msg == "":
            statsArray, charEmbedmsg = await characterCog.pointBuy(ctx, statsArray, rRecord, charEmbed, charEmbedmsg)

            
            if not statsArray:
                return
            charDict["STR"] = statsArray[0]
            charDict["DEX"] = statsArray[1]
            charDict["CON"] = statsArray[2]
            charDict["INT"] = statsArray[3]
            charDict["WIS"] = statsArray[4]
            charDict["CHA"] = statsArray[5]
        #Stats - Feats
        if msg == "":
            featLevels = []
            featChoices = []
            featsChosen = []
            if "Feat" in rRecord:
                featLevels.append('Extra Feat')

            for c in cRecord:
                if int(c['Level']) > 3:
                    featLevels.append(4)
                if 'Fighter' in c['Class']['Name'] and int(c['Level']) > 5:
                    featLevels.append(6)
                if int(c['Level']) > 7:
                    featLevels.append(8)
                if 'Rogue' in c['Class']['Name'] and int(c['Level']) > 9:
                    featLevels.append(10)
                if int(c['Level']) > 11:
                    featLevels.append(12)
                if 'Fighter' in c['Class']['Name'] and int(c['Level']) > 13:
                    featLevels.append(14)
                if int(c['Level']) > 15:
                    featLevels.append(16)
                if int(c['Level']) > 18:
                    featLevels.append(19)
            featsChosen, statsFeats, charEmbedmsg = await characterCog.chooseFeat(ctx, rRecord['Name'], charDict['Class'], cRecord, featLevels, charEmbed, charEmbedmsg, charDict, "")

            if not featsChosen and not statsFeats and not charEmbedmsg:
                self.bot.get_command('create').reset_cooldown(ctx)
                return

            if featsChosen:
                charDict['Feats'] = featsChosen 
            else: 
                charDict['Feats'] = "None" 
            
            for key, value in statsFeats.items():
                charDict[key] = value

            #HP
            hpRecords = []
            for cc in cRecord:
                # Wizards get 2 free spells per wizard level
                if cc['Class']['Name'] == "Wizard":
                    charDict['Free Spells'] = [6,0,0,0,0,0,0,0,0]
                    fsIndex = 0
                    for i in range (2, int(cc['Level']) + 1 ):
                        if i % 2 != 0:
                            fsIndex += 1
                        charDict['Free Spells'][fsIndex] += 2

                hpRecords.append({'Level':cc['Level'], 'Subclass': cc['Subclass'], 'Name': cc['Class']['Name'], 'Hit Die Max': cc['Class']['Hit Die Max'], 'Hit Die Average':cc['Class']['Hit Die Average']})

            if hpRecords:
                charDict['HP'] = await characterCog.calcHP(ctx,hpRecords,charDict,lvl)

            # Multiclass Requirements
            if '/' in cclass and len(cRecord) > 1:
                for m in cRecord:
                    reqFufillList = []
                    statReq = m['Class']['Multiclass'].split(' ')
                    if m['Class']['Multiclass'] != 'None':
                        if '/' not in m['Class']['Multiclass'] and '+' not in m['Class']['Multiclass']:
                            if int(charDict[statReq[0]]) < int(statReq[1]):
                                msg += f":warning: In order to multiclass to or from **{m['Class']['Name']}** you need at least **{m['Class']['Multiclass']}**. Your character only has **{statReq[0]} {charDict[statReq[0]]}**!\n"

                        elif '/' in m['Class']['Multiclass']:
                            statReq[0] = statReq[0].split('/')
                            reqFufill = False
                            for s in statReq[0]:
                                if int(charDict[s]) >= int(statReq[1]):
                                  reqFufill = True
                                else:
                                  reqFufillList.append(f"{s} {charDict[s]}")
                            if not reqFufill:
                                msg += f":warning: In order to multiclass to or from **{m['Class']['Name']}** you need at least **{m['Class']['Multiclass']}**. Your character only has **{' and '.join(reqFufillList)}**!\n"

                        elif '+' in m['Class']['Multiclass']:
                            statReq[0] = statReq[0].split('+')
                            reqFufill = True
                            for s in statReq[0]:
                                if int(charDict[s]) < int(statReq[1]):
                                  reqFufill = False
                                  reqFufillList.append(f"{s} {charDict[s]}")
                            if not reqFufill:
                                msg += f":warning: In order to multiclass to or from **{m['Class']['Name']}** you need at least **{m['Class']['Multiclass']}**. Your character only has **{' and '.join(reqFufillList)}**!\n"

        if msg:
            if charEmbedmsg and charEmbedmsg != "Fail":
                await charEmbedmsg.delete()
            elif charEmbedmsg == "Fail":
                msg = ":warning: You have either cancelled the command or a value was not found."
            await ctx.channel.send(f'There were error(s) when creating your character:\n{msg}')

            self.bot.get_command('create').reset_cooldown(ctx)
            return 
        
        charLevel = charDict['Level']
        tierNum = 5
        # calculate the tier of the rewards
        if charLevel < 5:
            tierNum = 1
        elif charLevel < 11:
            tierNum = 2
        elif charLevel < 17:
            tierNum = 3
        elif charLevel < 20:
            tierNum = 4
        charEmbed.clear_fields()    
        charEmbed.title = f"{charDict['Name']} (Lv {charDict['Level']}): {charDict['CP']}/{cp_bound_array[tierNum-1][1]} CP"
        charEmbed.description = f"**Race**: {charDict['Race']}\n**Class**: {charDict['Class']}\n**Background**: {charDict['Background']}\n**Max HP**: {charDict['HP']}\n**GP**: {charDict['GP']} "

        charEmbed.add_field(name='Current TP Item', value=charDict['Current Item'], inline=True)
        
        for x in range(1,6):
            if tpBank[x-1]>0:
              charDict[f'T{x} TP'] = tpBank[x-1]
              charEmbed.add_field(name=f':warning: Unused T{x} TP', value=charDict[f'T{x} TP'], inline=True)
        if charDict['Magic Items'] != 'None':
            charEmbed.add_field(name='Magic Items', value=charDict['Magic Items'], inline=False)
        if charDict['Consumables'] != 'None':
            charEmbed.add_field(name='Consumables', value=charDict['Consumables'], inline=False)
        charEmbed.add_field(name='Feats', value=charDict['Feats'], inline=True)
        charEmbed.add_field(name='Stats', value=f"**STR**: {charDict['STR']} **DEX**: {charDict['DEX']} **CON**: {charDict['CON']} **INT**: {charDict['INT']} **WIS**: {charDict['WIS']} **CHA**: {charDict['CHA']}", inline=False)

        if 'Wizard' in charDict['Class']:
            charEmbed.add_field(name='Spellbook (Wizard)', value=f"At 1st level, you have a spellbook containing six 1st-level Wizard spells of your choice (+2 free spells for each wizard level). Please use the `{commandPrefix}shop copy` command." , inline=False)

            fsString = ""
            fsIndex = 0
            for el in charDict['Free Spells']:
                if el > 0:
                    fsString += f"Level {fsIndex+1}: {el} free spells\n"
                fsIndex += 1

            if fsString:
                charEmbed.add_field(name='Free Spellbook Copies Available', value=fsString , inline=False)

        
        charDictInvString = ""
        if charDict['Inventory'] != "None":
            for k,v in charDict['Inventory'].items():
                charDictInvString += f"• {k} x{v}\n"
            charEmbed.add_field(name='Starting Equipment', value=charDictInvString, inline=False)
            charEmbed.set_footer(text= charEmbed.Empty)


        def charCreateCheck(r, u):
            sameMessage = False
            if charEmbedmsg.id == r.message.id:
                sameMessage = True
            return sameMessage and ((str(r.emoji) == '✅') or (str(r.emoji) == '❌')) and u == author


        if not charEmbedmsg:
            charEmbedmsg = await channel.send(embed=charEmbed, content="**Double-check** your character information.\nIf this is correct, please react with one of the following:\n✅ to finish creating your character.\n❌ to cancel. ")
        else:
            await charEmbedmsg.edit(embed=charEmbed, content="**Double-check** your character information.\nIf this is correct please react with one of the following:\n✅ to finish creating your character.\n❌ to cancel. ")

        await charEmbedmsg.add_reaction('✅')
        await charEmbedmsg.add_reaction('❌')
        try:
            tReaction, tUser = await self.bot.wait_for("reaction_add", check=charCreateCheck , timeout=60)
        except asyncio.TimeoutError:
            await charEmbedmsg.delete()
            await channel.send(f'Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
            self.bot.get_command('create').reset_cooldown(ctx)
            return
        else:
            await charEmbedmsg.clear_reactions()
            if tReaction.emoji == '❌':
                await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                await charEmbedmsg.clear_reactions()
                self.bot.get_command('create').reset_cooldown(ctx)
                return

        statsCollection = db.stats
        statsRecord  = statsCollection.find_one({'Life': 1})

        for c in classStat:
            char = c.split('-')
            if char[0] in statsRecord['Class']:
                statsRecord['Class'][char[0]]['Count'] += 1
            else:
                statsRecord['Class'][char[0]] = {'Count': 1}

            if len(char) > 1:
                if char[1] in statsRecord['Class'][char[0]]:
                    statsRecord['Class'][char[0]][char[1]] += 1
                else:
                    statsRecord['Class'][char[0]][char[1]] = 1

        if charDict['Race'] in statsRecord['Race']:
            statsRecord['Race'][charDict['Race']] += 1
        else:
            statsRecord['Race'][charDict['Race']] = 1

        if charDict['Background'] in statsRecord['Background']:
            statsRecord['Background'][charDict['Background']] += 1
        else:
            statsRecord['Background'][charDict['Background']] = 1
                
        if featsChosen != "":
            feat_split = featsChosen.split(", ")
            for feat_key in feat_split:
                if not feat_key in statsRecord['Feats']:
                    statsRecord['Feats'][feat_key] = 1
                else:
                    statsRecord['Feats'][feat_key] += 1
        try:
            playersCollection.insert_one(charDict)
            if campaignTransferSuccess:
                target = f"Campaigns.{campaignKey}.Time"
                db.users.update_one({"User ID": str(author.id)}, {"$inc" : {target: -cpTransfered *3600}})
                await self.levelCheck(ctx, charDict["Level"], charDict["Name"])
            statsCollection.update_one({'Life':1}, {"$set": statsRecord}, upsert=True)
            
        except Exception as e:
            print ('MONGO ERROR: ' + str(e))
            charEmbedmsg = await channel.send(embed=None, content="Uh oh, looks like something went wrong. Please try creating your character again.")
        else:
            print('Success')
            if charEmbedmsg:
                await charEmbedmsg.clear_reactions()
                await charEmbedmsg.edit(embed=charEmbed, content =f"Congratulations! :tada: You have created ***{charDict['Name']}***!")
            else: 
                charEmbedmsg = await channel.send(embed=charEmbed, content=f"Congratulations! You have created your ***{charDict['Name']}***!")

        self.bot.get_command('create').reset_cooldown(ctx)


    @commands.cooldown(1, float('inf'), type=commands.BucketType.user)
    @is_log_channel()
    @commands.command(aliases=['rs'])
    async def respec(self,ctx, name, newname, race, cclass, bg, sStr:int, sDex:int, sCon:int, sInt:int, sWis:int, sCha:int):
        newname = newname.strip()
        characterCog = self.bot.get_cog('Character')
        author = ctx.author
        guild = ctx.guild
        channel = ctx.channel
        charEmbed = discord.Embed ()
        charEmbed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        charEmbed.set_footer(text= "React with ❌ to cancel.\nPlease react with a choice even if no reactions appear.")

        statNames = ['STR','DEX','CON','INT','WIS','CHA']
        roles = [r.name for r in ctx.author.roles]
        charDict, charEmbedmsg = await checkForChar(ctx, name, charEmbed)

        if not charDict:
            return

        # Reset  values here
        charNoneKeyList = ['Magic Items', 'Inventory', 'Current Item', 'Consumables']

        charRemoveKeyList = ['Predecessor','Image', 'T1 TP', 'T2 TP', 'T3 TP', 'T4 TP', 'Attuned', 'Spellbook', 'Guild', 'Guild Rank', 'Grouped']
        
        guild_name = ""
        
        if "Guild" in charDict:
            guild_name = charDict["Guild"]
        
        m_save = charDict['Magic Items'].split(", ")
        # i_save = list(charDict['Inventory'].keys())
        check_list = m_save #+i_save
        
        searched_items = list(db.rit.find({"Name" : {"$in": check_list}}))
        searched_items_names = []
        
        for element in searched_items:
            if "Grouped" in element:
                searched_items_names += element["Name"]
            else:
                searched_items_names.append(element["Name"])
        
        m_saved_list = []
        for m_item in m_save:
            if m_item in searched_items_names:
                m_saved_list.append(m_item)
                
        # i_saved_list = []
        # for i_item in i_save:
            # if i_item in searched_items_names:
                # i_saved_list.append([i_item, charDict["Inventory"][i_item]])
        
        for c in charNoneKeyList:
            charDict[c] = "None"

        for c in charRemoveKeyList:
            if c in charDict:
                del charDict[c]
        name = charDict["Name"]
        charDict["Magic Items"] = ", ".join(m_saved_list) + ("None" * (len(m_saved_list) == 0))
        charDict["Inventory"] = {}
        
        # for i_item in i_saved_list:
            # charDict["Inventory"][i_item[0]] = i_item[1]
        charDict["Predecessor"]= {}
        
        charID = charDict['_id']
        charDict['STR'] = int(sStr)
        charDict['DEX'] = int(sDex)
        charDict['CON'] = int(sCon)
        charDict['INT'] = int(sInt)
        charDict['WIS'] = int(sWis)
        charDict['CHA'] = int(sCha)
        charDict['GP'] = 0

        charDict['Max Stats'] = {'STR':20, 'DEX':20, 'CON':20, 'INT':20, 'WIS':20, 'CHA':20}

        lvl = charDict['Level']
        msg = ""

        if 'Death' in charDict.keys():
            await channel.send(content=f"You cannot respec a dead character. Use the following command to decide their fate:\n```yaml\n$death \"{charRecords['Name']}\"```")
            return
        
        # level check
        if lvl > 4 and "Respecc" not in charDict:
            msg += "• Your character's level is way too high to respec.\n"
            await ctx.channel.send(msg)
            self.bot.get_command('respec').reset_cooldown(ctx) 
            return
        
        # new name should be less then 64 chars
        if len(newname) > 64:
            msg += ":warning: Your character's new name is too long! The limit is 64 characters.\n"
        # Reserved for regex, lets not use these for character names please
        invalidChars = ["[", "]", "?", '"', "\\", "*", "$", "{", "+", "}", "^", ">", "<", "|"]
        for i in invalidChars:
            if i in newname:
                msg += f":warning: Your character's name cannot contain `{i}`. Please revise your character name.\n"


        # Prevents name, level, race, class, background from being blank. Resets infinite cooldown and prompts
        if not newname:
            await channel.send(content=":warning: The new name of your character cannot be blank! Please try again.\n")
            self.bot.get_command('respec').reset_cooldown(ctx)
            return
        
        
        query = newname
        query = query.replace('(', '\\(')
        query = query.replace(')', '\\)')
        query = query.replace('.', '\\.')
        playersCollection = db.players
        userRecords = list(playersCollection.find({"User ID": str(author.id), "Name": {"$regex": f"^{query}$", '$options': 'i' }}))

        if userRecords != list() and newname.lower() != name.lower():
            msg += f":warning: You already have a character by the name ***{newname}***. Please use a different name.\n"

        oldName = charDict['Name']
        charDict['Name'] = newname

        if not race:
            await channel.send(content=":warning: The race of your character cannot be blank! Please try again.\n")
            self.bot.get_command('respec').reset_cooldown(ctx)
            return

        if not cclass:
            await channel.send(content=":warning: The class of your character cannot be blank! Please try again.\n")
            self.bot.get_command('respec').reset_cooldown(ctx)
            return
        
        if not bg:
            await channel.send(content=":warning: The background of your character cannot be blank! Please try again.\n")
            self.bot.get_command('respec').reset_cooldown(ctx)
            return


        allMagicItemsString = []

        # Because we are respeccing we are also adding extra TP based on CP.
        # no needed to to bankTP2 now because limit is lvl 4 to respec
        extraCp = charDict['CP']
        charLevel = charDict['Level']
        if "Respecc" in charDict:
            maxCP = 10
            if charLevel < 5:
                maxCP = 4
            while(extraCp >= maxCP and charLevel <20):
                extraCp -= maxCP
                charLevel += 1
                if charLevel > 4:
                    maxCP = 10
            charDict["Level"] = charLevel
            charDict['CP'] = extraCp
            lvl = charLevel
        tierNum = 5
        # calculate the tier of the rewards
        if charLevel < 5:
            tierNum = 1
        elif charLevel < 11:
            tierNum = 2
        elif charLevel < 17:
            tierNum = 3
        elif charLevel < 20:
            tierNum = 4
        if extraCp > cp_bound_array[tierNum-1][0] and "Respecc" not in charDict:
            msg += f":warning: {oldName} needs to level up before they can respec into a new character!"
        
        levelCP = (((charLevel-5) * 10) + 16)
        if charLevel < 5:
            levelCP = ((charLevel -1) * 4)
            
        cp_tp_gp_array = calculateTreasure(1, 0, 1, (levelCP+extraCp)*3600)
        totalGP = cp_tp_gp_array[2]
        bankTP = cp_tp_gp_array[1]
        # Stats - Point Buy
        if msg == "":
            statsArray = [int(sStr), int(sDex), int(sCon), int(sInt), int(sWis), int(sCha)]
            
            totalPoints = 0
            for s in statsArray:
                if (13-s) < 0:
                    totalPoints += ((s - 13) * 2) + 5
                else:
                    totalPoints += (s - 8)
                    
            if any([s < 8 for s in statsArray]):
                msg += f":warning: You have at least one stat below the minimum of 8.\n"
            if totalPoints != 27:
                msg += f":warning: Your stats do not add up to 27 using point buy ({totalPoints}/27). Remember that you must list your stats before applying racial modifiers! Please check your point allocation using this calculator: <https://chicken-dinner.com/5e/5e-point-buy.html>\n"
            
        
        
        # ██████╗░░█████╗░░█████╗░███████╗░░░  ░█████╗░██╗░░░░░░█████╗░░██████╗░██████╗
        # ██╔══██╗██╔══██╗██╔══██╗██╔════╝░░░  ██╔══██╗██║░░░░░██╔══██╗██╔════╝██╔════╝
        # ██████╔╝███████║██║░░╚═╝█████╗░░░░░  ██║░░╚═╝██║░░░░░███████║╚█████╗░╚█████╗░
        # ██╔══██╗██╔══██║██║░░██╗██╔══╝░░██╗  ██║░░██╗██║░░░░░██╔══██║░╚═══██╗░╚═══██╗
        # ██║░░██║██║░░██║╚█████╔╝███████╗╚█║  ╚█████╔╝███████╗██║░░██║██████╔╝██████╔╝
        # ╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░╚══════╝░╚╝  ░╚════╝░╚══════╝╚═╝░░╚═╝╚═════╝░╚═════╝░
        # check race
        rRecord, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg,'races',race)
        if not rRecord:
            msg += f':warning: **{race}** isn\'t on the list or it is banned! Check #allowed-and-banned-content and check your spelling.\n'
        else:
            charDict['Race'] = rRecord['Name']
        
        # Check Character's class
        classStat = []
        cRecord = []
        totalLevel = 0
        mLevel = 0
        broke = []
        # If there's a /, character is creating a multiclass character
        if '/' in cclass:
            multiclassList = cclass.replace(' ', '').split('/')
            # Iterates through the multiclass list 
            
            for m in multiclassList:
                # Separate level and class
                mLevel = re.search('\d+', m)
                if not mLevel:
                    msg += ":warning: You are missing the level for your multiclass class. Please check your format.\n"

                    break
                mLevel = mLevel.group()
                mClass, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg,'classes',m[:len(m) - len(mLevel)])
                if not mClass:
                    cRecord = None
                    broke.append(m[:len(m) - len(mLevel)])

                # Check for class duplicates (ex. Paladin 1 / Paladin 2 = Paladin 3)
                classDupe = False
                
                if(cRecord or cRecord==list()):
                    for c in cRecord:
                        if c['Class'] == mClass:
                            c['Level'] = str(int(c['Level']) + int(mLevel))
                            classDupe = True                    
                            break

                    if not classDupe:
                        cRecord.append({'Class': mClass, 'Level':mLevel})
                    totalLevel += int(mLevel)

        else:
            singleClass, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg, 'classes',cclass)
            if singleClass:
                cRecord.append({'Class':singleClass, 'Level':lvl, 'Subclass': 'None'})
            else:
                cRecord = None
                broke.append(cclass)

        charDict['Class'] = ""
        if not mLevel and '/' in cclass:
            pass
        elif len(broke)>0:
            msg += f':warning: **{broke}** isn\'t on the list or it is banned! Check #allowed-and-banned-content and check your spelling.\n'
        
        elif len(broke)>0:
            msg += f':warning: **{broke}** isn\'t on the list or it is banned! Check #allowed-and-banned-content and check your spelling.\n'
        elif totalLevel != lvl and len(cRecord) > 1:
            msg += ':warning: Your classes do not add up to the total level. Please double-check your multiclasses.\n'
        elif msg == "":

            # starting equipment
            def alphaEmbedCheck(r, u):
                sameMessage = False
                if charEmbedmsg.id == r.message.id:
                    sameMessage = True
                return sameMessage and ((r.emoji in alphaEmojis[:alphaIndex]) or (str(r.emoji) == '❌')) and u == author

            if 'Starting Equipment' in cRecord[0]['Class'] and msg == "":
                if charDict['Inventory'] == "None":
                    charDict['Inventory'] = {}
                startEquipmentLength = 0
                if not charEmbedmsg:
                    charEmbedmsg = await channel.send(embed=charEmbed)
                elif charEmbedmsg == "Fail":
                    msg += ":warning: You have either cancelled the command or a value was not found."
                else:
                    await charEmbedmsg.edit(embed=charEmbed)

                for item in cRecord[0]['Class']['Starting Equipment']:
                    seTotalString = ""
                    alphaIndex = 0
                    for seList in item:
                        seString = []
                        for elk, elv in seList.items():
                            if 'Pack' in elk:
                                seString.append(f"{elk} x1")
                            else:
                                seString.append(f"{elk} x{elv}")
                                
                        seTotalString += f"{alphaEmojis[alphaIndex]}: {', '.join(seString)}\n"
                        alphaIndex += 1

                    await charEmbedmsg.clear_reactions()
                    charEmbed.add_field(name=f"Starting Equipment: {startEquipmentLength+ 1} of {len(cRecord[0]['Class']['Starting Equipment'])}", value=seTotalString, inline=False)
                    await charEmbedmsg.edit(embed=charEmbed)
                    if len(item) > 1:
                        for num in range(0,alphaIndex): await charEmbedmsg.add_reaction(alphaEmojis[num])
                        await charEmbedmsg.add_reaction('❌')
                        try:
                            tReaction, tUser = await self.bot.wait_for("reaction_add", check=alphaEmbedCheck, timeout=60)
                        except asyncio.TimeoutError:
                            await charEmbedmsg.delete()
                            await channel.send(f'Character creation timed out! Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                            self.bot.get_command('respec').reset_cooldown(ctx)
                            return 
                        else:
                            if tReaction.emoji == '❌':
                                await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                                await charEmbedmsg.clear_reactions()
                                self.bot.get_command('respec').reset_cooldown(ctx)
                                return 
                                
                        startEquipmentItem = item[alphaEmojis.index(tReaction.emoji)]
                    else:
                        startEquipmentItem = item[0]

                    await charEmbedmsg.clear_reactions()

                    seiString = ""
                    for seik, seiv in startEquipmentItem.items():
                        seiString += f"{seik} x{seiv}\n"
                        if "Pack" in seik:
                            seiString = f"{seik}:\n"
                            for pk, pv in seiv.items():
                                charDict['Inventory'][pk] = pv
                                seiString += f"+ {pk} x{pv}\n"

                    charEmbed.set_field_at(startEquipmentLength, name=f"Starting Equipment: {startEquipmentLength + 1} of {len(cRecord[0]['Class']['Starting Equipment'])}", value=seiString, inline=False)

                    for k,v in startEquipmentItem.items():
                        if '[' in k and ']' in k:
                            iType = k.split('[')
                            invCollection = db.shop
                            if 'Instrument' in iType[1]:
                                charInv = list(invCollection.find({"Type": {'$all': [re.compile(f".*{iType[1].replace(']','')}.*")]}}))
                            else:
                                charInv = list(invCollection.find({"Type": {'$all': [re.compile(f".*{iType[0]}.*"),re.compile(f".*{iType[1].replace(']','')}.*")]}}))

                            charInv = sorted(charInv, key = lambda i: i['Name']) 

                            typeEquipmentList = []
                            for i in range (0,int(v)):
                                charInvString = f"Please choose from the choices below for {iType[0]} {i+1}:\n"
                                alphaIndex = 0
                                
                                charInv = list(filter(lambda c: 'Yklwa' not in c['Name'] and 'Light Repeating Crossbow' not in c['Name'] and 'Double-Bladed Scimitar' not in c['Name'] and 'Oversized Longbow' not in c['Name'], charInv))
                                for c in charInv:
                                    charInvString += f"{alphaEmojis[alphaIndex]}: {c['Name']}\n"
                                    alphaIndex += 1

                                charEmbed.set_field_at(startEquipmentLength, name=f"Starting Equipment: {startEquipmentLength+1} of {len(cRecord[0]['Class']['Starting Equipment'])}", value=charInvString, inline=False)
                                await charEmbedmsg.clear_reactions()
                                await charEmbedmsg.add_reaction('❌')
                                await charEmbedmsg.edit(embed=charEmbed)

                                try:
                                    tReaction, tUser = await self.bot.wait_for("reaction_add", check=alphaEmbedCheck, timeout=60)
                                except asyncio.TimeoutError:
                                    await charEmbedmsg.delete()
                                    await channel.send(f'Character creation timed out! Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                                    self.bot.get_command('respec').reset_cooldown(ctx)
                                    return 
                                else:
                                    if tReaction.emoji == '❌':
                                        await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                                        await charEmbedmsg.clear_reactions()
                                        self.bot.get_command('respec').reset_cooldown(ctx)
                                        return 
                                typeEquipmentList.append(charInv[alphaEmojis.index(tReaction.emoji)]['Name'])
                            typeCount = collections.Counter(typeEquipmentList)
                            typeString = ""
                            for tk, tv in typeCount.items():
                                typeString += f"{tk} x{tv}\n"
                                if tk in charDict['Inventory']:
                                    charDict['Inventory'][tk] += tv
                                else:
                                    charDict['Inventory'][tk] = tv

                            charEmbed.set_field_at(startEquipmentLength, name=f"Starting Equipment: {startEquipmentLength+1} of {len(cRecord[0]['Class']['Starting Equipment'])}", value=seiString.replace(f"{k} x{v}\n", typeString), inline=False)

                        elif 'Pack' not in k:
                            if k in charDict['Inventory']:
                                charDict['Inventory'][k] += v
                            else:
                                charDict['Inventory'][k] = v
                    startEquipmentLength += 1
                await charEmbedmsg.clear_reactions()
                charEmbed.clear_fields()

            # Subclass
            for m in cRecord:
                m['Subclass'] = 'None'
                if int(m['Level']) < lvl:
                    className = f'{m["Class"]["Name"]} {m["Level"]}'
                else:
                    className = f'{m["Class"]["Name"]}'

                classStatName = f'{m["Class"]["Name"]}'

                if int(m['Class']['Subclass Level']) <= int(m['Level']) and msg == "":
                    subclassesList = m['Class']['Subclasses'].split(',')
                    subclass, charEmbedmsg = await characterCog.chooseSubclass(ctx, subclassesList, m['Class']['Name'], charEmbed, charEmbedmsg)
                    if not subclass:
                        return

                    m['Subclass'] = f'{className} ({subclass})' 
                    classStat.append(f'{classStatName}-{subclass}')


                    if charDict['Class'] == "": 
                        charDict['Class'] = f'{className} ({subclass})'
                    else:
                        charDict['Class'] += f' / {className} ({subclass})'
                else:
                    classStat.append(classStatName)
                    if charDict['Class'] == "": 
                        charDict['Class'] = className
                    else:
                        charDict['Class'] += f' / {className}'

        # check bg and gp

        def bgTopItemCheck(r, u):
            sameMessage = False
            if charEmbedmsg.id == r.message.id:
                sameMessage = True
            return ((r.emoji in alphaEmojis[:alphaIndexTop]) or (str(r.emoji) == '❌')) and u == author and sameMessage

        def bgItemCheck(r, u):
            sameMessage = False
            if charEmbedmsg.id == r.message.id:
                sameMessage = True
            return ((r.emoji in alphaEmojis[:alphaIndex]) or (str(r.emoji) == '❌')) and u == author and sameMessage


        if msg == "":
            bRecord, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg, 'backgrounds',bg)

            if charEmbedmsg == "Fail":
                self.bot.get_command('respec').reset_cooldown(ctx)
                return
            if not bRecord:
                msg += f':warning: **{bg}** isn\'t on the list or it is banned! Check #allowed-and-banned-content and check your spelling.\n'
            else:
                charDict['Background'] = bRecord['Name']

                # TODO: make function for inputing in inventory
                # Background items: goes through each background and give extra items for inventory.
                
                for e in bRecord['Equipment']:
                    beTopChoiceList = []
                    beTopChoiceKeys = []
                    alphaIndexTop = 0
                    beTopChoiceString = ""
                    for ek, ev in e.items():
                        if type(ev) == dict:
                            beTopChoiceKeys.append(ek)
                            beTopChoiceList.append(ev)
                            beTopChoiceString += f"{alphaEmojis[alphaIndexTop]}: {ek}\n"
                            alphaIndexTop += 1
                        else:
                            if charDict['Inventory'] == "None":
                                charDict['Inventory'] = {ek : int(ev)}
                            else:
                                if ek not in charDict['Inventory']:
                                    charDict['Inventory'][ek] = int(ev)
                                else:
                                    charDict['Inventory'][ek] += int(ev)

                    if len(beTopChoiceList) > 0:
                        # Lets user pick between top choices (ex. Game set or Musical Instrument. Then a followup choice.)
                        if len(beTopChoiceList) > 1:
                            charEmbed.add_field(name=f"Your {bRecord['Name']} background lets you choose one type.", value=beTopChoiceString, inline=False)
                            if not charEmbedmsg:
                                charEmbedmsg = await channel.send(embed=charEmbed)
                            else:
                                await charEmbedmsg.edit(embed=charEmbed)

                            await charEmbedmsg.add_reaction('❌')
                            try:
                                tReaction, tUser = await self.bot.wait_for("reaction_add", check=bgTopItemCheck , timeout=60)
                            except asyncio.TimeoutError:
                                await charEmbedmsg.delete()
                                await channel.send(f'Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                                self.bot.get_command('respec').reset_cooldown(ctx)
                                return
                            else:
                                await charEmbedmsg.clear_reactions()
                                if tReaction.emoji == '❌':
                                    await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                                    await charEmbedmsg.clear_reactions()
                                    self.bot.get_command('respec').reset_cooldown(ctx)
                                    return

                            beTopValues = beTopChoiceList[alphaEmojis.index(tReaction.emoji)]
                            beTopKey = beTopChoiceKeys[alphaEmojis.index(tReaction.emoji)]
                        elif len(beTopChoiceList) == 1:
                            beTopValues = beTopChoiceList[0]
                            beTopKey = beTopChoiceKeys[0]

                        beChoiceString = ""
                        alphaIndex = 0
                        beList = []

                        if 'Pack' in beTopKey:
                          for c in beTopValues:
                              if charDict['Inventory'] == "None":
                                  charDict['Inventory'] = {c : 1}
                              else:
                                  if c not in charDict['Inventory']:
                                      charDict['Inventory'][c] = 1
                                  else:
                                      charDict['Inventory'][c] += 1
                        else:
                            for c in beTopValues:
                                beChoiceString += f"{alphaEmojis[alphaIndex]}: {c}\n"
                                beList.append(c)
                                alphaIndex += 1

                            charEmbed.add_field(name=f"Your {bRecord['Name']} background lets you choose one {beTopKey}.", value=beChoiceString, inline=False)
                            if not charEmbedmsg:
                                charEmbedmsg = await channel.send(embed=charEmbed)
                            else:
                                await charEmbedmsg.edit(embed=charEmbed)

                            await charEmbedmsg.add_reaction('❌')
                            try:
                                tReaction, tUser = await self.bot.wait_for("reaction_add", check=bgItemCheck , timeout=60)
                            except asyncio.TimeoutError:
                                await charEmbedmsg.delete()
                                await channel.send(f'Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                                self.bot.get_command('respec').reset_cooldown(ctx)
                                return
                            else:
                                await charEmbedmsg.clear_reactions()
                                if tReaction.emoji == '❌':
                                    await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                                    await charEmbedmsg.clear_reactions()
                                    self.bot.get_command('respec').reset_cooldown(ctx)
                                    return
                                beKey = beList[alphaEmojis.index(tReaction.emoji)]
                                if charDict['Inventory'] == "None":
                                    charDict['Inventory'] = {beKey : 1}
                                else:
                                    if beKey not in charDict['Inventory']:
                                        charDict['Inventory'][beKey] = 1
                                    else:
                                        charDict['Inventory'][beKey] += 1

                        charEmbed.clear_fields()
                
                charDict['GP'] = int(bRecord['GP']) + totalGP
        
        # ░██████╗████████╗░█████╗░████████╗░██████╗░░░  ███████╗███████╗░█████╗░████████╗░██████╗
        # ██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██╔════╝░░░  ██╔════╝██╔════╝██╔══██╗╚══██╔══╝██╔════╝
        # ╚█████╗░░░░██║░░░███████║░░░██║░░░╚█████╗░░░░  █████╗░░█████╗░░███████║░░░██║░░░╚█████╗░
        # ░╚═══██╗░░░██║░░░██╔══██║░░░██║░░░░╚═══██╗██╗  ██╔══╝░░██╔══╝░░██╔══██║░░░██║░░░░╚═══██╗
        # ██████╔╝░░░██║░░░██║░░██║░░░██║░░░██████╔╝╚█║  ██║░░░░░███████╗██║░░██║░░░██║░░░██████╔╝
        # ╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝░░░╚═╝░░░╚═════╝░░╚╝  ╚═╝░░░░░╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚═════╝░
        # Stats - Point Buy
        if msg == "":
            statsArray, charEmbedmsg = await characterCog.pointBuy(ctx, statsArray, rRecord, charEmbed, charEmbedmsg)

            
            if not statsArray:
                return
            charDict["STR"] = statsArray[0]
            charDict["DEX"] = statsArray[1]
            charDict["CON"] = statsArray[2]
            charDict["INT"] = statsArray[3]
            charDict["WIS"] = statsArray[4]
            charDict["CHA"] = statsArray[5]

        #Stats - Feats
        if msg == "":
            featLevels = []
            featChoices = []
            featsChosen = []
            if "Feat" in rRecord:
                featLevels.append('Extra Feat')
            for c in cRecord:
                if int(c['Level']) > 3:
                    featLevels.append(4)
                if 'Fighter' in c['Class']['Name'] and int(c['Level']) > 5:
                    featLevels.append(6)
                if int(c['Level']) > 7:
                    featLevels.append(8)
                if 'Rogue' in c['Class']['Name'] and int(c['Level']) > 9:
                    featLevels.append(10)
                if int(c['Level']) > 11:
                    featLevels.append(12)
                if 'Fighter' in c['Class']['Name'] and int(c['Level']) > 13:
                    featLevels.append(14)
                if int(c['Level']) > 15:
                    featLevels.append(16)
                if int(c['Level']) > 18:
                    featLevels.append(19)

            featsChosen, statsFeats, charEmbedmsg = await characterCog.chooseFeat(ctx, rRecord['Name'], charDict['Class'], cRecord, featLevels, charEmbed, charEmbedmsg, charDict, "")

            if not featsChosen and not statsFeats and not charEmbedmsg:
                return

            if featsChosen:
                charDict['Feats'] = featsChosen 
            else: 
                charDict['Feats'] = "None" 
            
            for key, value in statsFeats.items():
                charDict[key] = value


            #HP
            hpRecords = []
            for cc in cRecord:
                # Wizards get 2 free spells per wizard level
                if cc['Class']['Name'] == "Wizard":
                    charDict['Free Spells'] = [6,0,0,0,0,0,0,0,0]
                    fsIndex = 0
                    for i in range (2, int(cc['Level']) + 1 ):
                        if i % 2 != 0:
                            fsIndex += 1
                        charDict['Free Spells'][min(fsIndex, 8)] += 2
                hpRecords.append({'Level':cc['Level'], 'Subclass': cc['Subclass'], 'Name': cc['Class']['Name'], 'Hit Die Max': cc['Class']['Hit Die Max'], 'Hit Die Average':cc['Class']['Hit Die Average']})
                
            
            # Multiclass Requirements
            if '/' in cclass and len(cRecord) > 1:
                for m in cRecord:
                    reqFufillList = []
                    statReq = m['Class']['Multiclass'].split(' ')
                    if m['Class']['Multiclass'] != 'None':
                        if '/' not in m['Class']['Multiclass'] and '+' not in m['Class']['Multiclass']:
                            if int(charDict[statReq[0]]) < int(statReq[1]):
                                msg += f":warning: In order to multiclass to or from **{m['Class']['Name']}** you need at least **{m['Class']['Multiclass']}**. Your character only has **{statReq[0]} {charDict[statReq[0]]}**\n"

                        elif '/' in m['Class']['Multiclass']:
                            statReq[0] = statReq[0].split('/')
                            reqFufill = False
                            for s in statReq[0]:
                                if int(charDict[s]) >= int(statReq[1]):
                                  reqFufill = True
                                else:
                                  reqFufillList.append(f"{s} {charDict[s]}")
                            if not reqFufill:
                                msg += f":warning: In order to multiclass to or from **{m['Class']['Name']}** you need at least **{m['Class']['Multiclass']}**. Your character only has **{' and '.join(reqFufillList)}**\n"

                        elif '+' in m['Class']['Multiclass']:
                            statReq[0] = statReq[0].split('+')
                            reqFufill = True
                            for s in statReq[0]:
                                if int(charDict[s]) < int(statReq[1]):
                                  reqFufill = False
                                  reqFufillList.append(f"{s} {charDict[s]}")
                            if not reqFufill:
                                msg += f":warning: In order to multiclass to or from **{m['Class']['Name']}** you need at least **{m['Class']['Multiclass']}**. Your character only has **{' and '.join(reqFufillList)}**\n"


        if msg:
            if charEmbedmsg and charEmbedmsg != "Fail":
                await charEmbedmsg.delete()
            elif charEmbedmsg == "Fail":
                msg = ":warning: You have either cancelled the command or a value was not found."
            await ctx.channel.send(f'There were error(s) when creating your character:\n{msg}')

            self.bot.get_command('respec').reset_cooldown(ctx)
            return 
        
        if 'Max Stats' not in charDict:
            charDict['Max Stats'] = {'STR':20, 'DEX':20, 'CON':20, 'INT':20, 'WIS':20, 'CHA':20}
        
        charClass = charDict["Class"]
        subclasses = []
        if '/' in charClass:
            tempClassList = charClass.split(' / ')
            for t in tempClassList:
                temp = t.split(' ')
                tempSub = ""
                if '(' and ')' in t:
                    tempSub = t[t.find("(")+1:t.find(")")]

                subclasses.append({'Name':temp[0], 'Subclass':tempSub, 'Level':int(temp[1])})
        else:
            tempSub = ""
            if '(' and ')' in charClass:
                tempSub = charClass[charClass.find("(")+1:charClass.find(")")]
            subclasses.append({'Name':charClass, 'Subclass':tempSub, 'Level':charLevel})
        #Special stat bonuses (Barbarian cap / giant soul sorc)
        specialCollection = db.special
        specialRecords = list(specialCollection.find())
        specialStatStr = ""
        for s in specialRecords:
            if 'Bonus Level' in s:
                for c in subclasses:
                    if s['Bonus Level'] <= c['Level'] and s['Name'] in f"{c['Name']} ({c['Subclass']})":
                        if 'MAX' in s['Stat Bonuses']:
                            statSplit = s['Stat Bonuses'].split('MAX ')[1].split(', ')
                            for stat in statSplit:
                                maxSplit = stat.split(' +')
                                charDict[maxSplit[0]] += int(maxSplit[1])
                                charDict['Max Stats'][maxSplit[0]] += int(maxSplit[1]) 

                            specialStatStr = f"Level {s['Bonus Level']} {c['Name']} stat bonus unlocked! {s['Stat Bonuses']}"


        maxStatStr = ""
        for sk in charDict['Max Stats'].keys():
            if charDict[sk] > charDict['Max Stats'][sk]:
                charDict[sk] = charDict['Max Stats'][sk]
        if hpRecords:
            charDict['HP'] = await characterCog.calcHP(ctx,hpRecords,charDict,lvl)

        
        charEmbed.clear_fields()    
        charEmbed.title = f"{charDict['Name']} (Lv {charDict['Level']}): {charDict['CP']}/{cp_bound_array[tierNum-1][1]} CP"
        charEmbed.description = f"**Race**: {charDict['Race']}\n**Class**: {charDict['Class']}\n**Background**: {charDict['Background']}\n**Max HP**: {charDict['HP']}\n**GP**: {charDict['GP']} "

        charEmbed.add_field(name='Current TP Item', value=charDict['Current Item'], inline=True)
        
        for key, amount in bankTP.items():
            if  amount > 0:
                charDict[key] = amount
                charEmbed.add_field(name=f':warning: Unused {key}:', value=amount, inline=True)
        if charDict['Magic Items'] != 'None':
            charEmbed.add_field(name='Magic Items', value=charDict['Magic Items'], inline=False)
        if charDict['Consumables'] != 'None':
            charEmbed.add_field(name='Consumables', value=charDict['Consumables'], inline=False)
        charEmbed.add_field(name='Feats', value=charDict['Feats'], inline=True)
        charEmbed.add_field(name='Stats', value=f"**STR**: {charDict['STR']} **DEX**: {charDict['DEX']} **CON**: {charDict['CON']} **INT**: {charDict['INT']} **WIS**: {charDict['WIS']} **CHA**: {charDict['CHA']}", inline=False)
        
        if 'Wizard' in charDict['Class']:
            charEmbed.add_field(name='Spellbook (Wizard)', value=f"At 1st level, you have a spellbook containing six 1st-level Wizard spells of your choice (+2 free spells for each Wizard level). Please use the `{commandPrefix}shop copy` command.", inline=False)

# Put the text below after the last sentence in the previous line if this breaks anything.
# **{charDict['Free Spells']} Free Spells Available**

            fsString = ""
            fsIndex = 0
            for el in charDict['Free Spells']:
                if el > 0:
                    fsString += f"Level {fsIndex+1}: {el} free spells\n"
                fsIndex += 1

            if fsString:
                charEmbed.add_field(name='Free Spellbook Copies Available', value=fsString , inline=False)

        charDictInvString = ""
        if charDict['Inventory'] != "None":
            for k,v in charDict['Inventory'].items():
                charDictInvString += f"• {k} x{v}\n"
            charEmbed.add_field(name='Starting Equipment', value=charDictInvString, inline=False)
            charEmbed.set_footer(text= charEmbed.Empty)
        
        def charCreateCheck(r, u):
            sameMessage = False
            if charEmbedmsg.id == r.message.id:
                sameMessage = True
            return sameMessage and ((str(r.emoji) == '✅') or (str(r.emoji) == '❌')) and u == author
        if not charEmbedmsg:
            charEmbedmsg = await channel.send(embed=charEmbed, content="**Double-check** your character information.\nIf this is correct, please react with one of the following:\n✅ to finish creating your character.\n❌ to cancel. ")
        else:
            await charEmbedmsg.edit(embed=charEmbed, content="**Double-check** your character information.\nIf this is correct please react with one of the following:\n✅ to finish creating your character.\n❌ to cancel. ")

        await charEmbedmsg.add_reaction('✅')
        await charEmbedmsg.add_reaction('❌')
        try:
            tReaction, tUser = await self.bot.wait_for("reaction_add", check=charCreateCheck , timeout=60)
        except asyncio.TimeoutError:
            await charEmbedmsg.delete()
            await channel.send(f'Character respec cancelled. Use the following command to try again:\n```yaml\n{commandPrefix}respec "character name" "new character name" level "race" "class" "background" STR DEX CON INT WIS CHA```')
            self.bot.get_command('respec').reset_cooldown(ctx)
            return
        else:
            await charEmbedmsg.clear_reactions()
            if tReaction.emoji == '❌':
                await charEmbedmsg.edit(embed=None, content=f"Character respec cancelled. Try again using the same command:\n```yaml\n{commandPrefix}respec \"character name\" \"new character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA```")
                await charEmbedmsg.clear_reactions()
                self.bot.get_command('respec').reset_cooldown(ctx)
                return


        try:
            
            if len(guild_name)>0:
                guildAmount = list(playersCollection.find({"User ID": str(author.id), "Guild": {"$regex": guild_name, '$options': 'i' }}))
                # If there is only one of user's character in the guild remove the role.
                if (len(guildAmount) <= 1):
                    await author.remove_roles(get(guild.roles, name = guild_name), reason=f" Respecced")

            if "Respecc" in charDict and charDict["Respecc"] == "Transfer":
                charDict["Inventory"].update(charDict["Transfer Set"]["Inventory"])
                charDict["Magic Items"] = charDict["Transfer Set"]["Magic Items"]
                charDict["Consumables"] = charDict["Transfer Set"]["Consumables"]
                del charDict["Transfer Set"]
                statsCollection = db.stats
                statsRecord  = statsCollection.find_one({'Life': 1})

                for c in classStat:
                    char = c.split('-')
                    if char[0] in statsRecord['Class']:
                        statsRecord['Class'][char[0]]['Count'] += 1
                    else:
                        statsRecord['Class'][char[0]] = {'Count': 1}

                    if len(char) > 1:
                        if char[1] in statsRecord['Class'][char[0]]:
                            statsRecord['Class'][char[0]][char[1]] += 1
                        else:
                            statsRecord['Class'][char[0]][char[1]] = 1

                if charDict['Race'] in statsRecord['Race']:
                    statsRecord['Race'][charDict['Race']] += 1
                else:
                    statsRecord['Race'][charDict['Race']] = 1

                if charDict['Background'] in statsRecord['Background']:
                    statsRecord['Background'][charDict['Background']] += 1
                else:
                    statsRecord['Background'][charDict['Background']] = 1
                if featsChosen != "":
                    feat_split = featsChosen.split(", ")
                    for feat_key in feat_split:
                        if not feat_key in statsRecord['Feats']:
                            statsRecord['Feats'][feat_key] = 1
                        else:
                            statsRecord['Feats'][feat_key] += 1
                statsCollection.update_one({'Life':1}, {"$set": statsRecord}, upsert=True)
                await self.levelCheck(ctx, charDict["Level"], charDict["Name"])
            # Extra to unset
            if "Respecc" in charDict:
                del charDict["Respecc"]
            charRemoveKeyList = {"Transfer Set" : 1, "Respecc" : 1, 'Image':1, 'Spellbook':1, 'Attuned':1, 'Guild':1, 'Guild Rank':1, 'Grouped':1}
            playersCollection.update_one({'_id': charID}, {"$set": charDict, "$unset": charRemoveKeyList }, upsert=True)
            
        except Exception as e:
            print ('MONGO ERROR: ' + str(e))
            charEmbedmsg = await channel.send(embed=None, content="Uh oh, looks like something went wrong. Please try creating your character again.")
        else:
            print('Success')
            if charEmbedmsg:
                await charEmbedmsg.clear_reactions()
                await charEmbedmsg.edit(embed=charEmbed, content =f"Congratulations! You have respecced your character!")
            else: 
                charEmbedmsg = await channel.send(embed=charEmbed, content=f"Congratulations! You have respecced your character!")

        self.bot.get_command('respec').reset_cooldown(ctx)
    
    @commands.cooldown(1, float('inf'), type=commands.BucketType.user)
    @commands.command()
    async def bemine(self, ctx, char):
        channel = ctx.channel
        author = ctx.author
        shopEmbed = discord.Embed()
        
        # Check if character exists
        charRecords, shopEmbedmsg = await checkForChar(ctx, char, shopEmbed)

        if charRecords:
            
            outcomes = [("Ghost Pepper Chocolate", "Ghost Pepper Chocolate"), 
                    ("Wand of Smiles", "Wand of Smiles"), 
                    ("Promise Rings", "Band of Loyalty"), 
                    ("Arcanaloth's Music Box", "Arcanaloth's Music Box"), 
                    ("Talking Teddy Bear", "Talking Doll"), 
                    ("Crown of Blind Love", "Crown of the Forest"), 
                    ("Pipe of Remembrance", "Pipe of Remembrance"), 
                    ("Chocolate of Nourishment", "Bead of Nourishment"), 
                    ("Love Note Bird", "Paper Bird"), 
                    ("Perfume of Bewitching", "Perfume of Bewitching"), 
                    ("Philter of Love", "Philter of Love"), 
                    ("Swan Boat", "Quaal's Feather Token \\(Swan Boat\\)")]
            selection = random.randrange(len(outcomes)) 
            
            show_name, selected_item = outcomes[selection]
            amount = 0
            if "Event Token" in charRecords:
                amount = charRecords["Event Token"]
            if amount <= 0:
                shopEmbed.description = f"You would have received {show_name} ({selected_item})"
                shopEmbedmsg = await channel.send(embed=shopEmbed)
                ctx.command.reset_cooldown(ctx)
                return
            bRecord = db.rit.find_one({"Name" : {"$regex" : f"{selected_item}", "$options": "i"}}) 
            out_text = f"You reach into the gift box and find a(n) **{show_name} ({selected_item})**\n\n*{amount-1} rolls remaining*"
            if bRecord:
                
                if shopEmbedmsg:
                    await shopEmbedmsg.edit(embed=shopEmbed)
                else:
                    shopEmbedmsg = await channel.send(embed=shopEmbed)
                if bRecord["Type"] != "Inventory":
                    if charRecords[bRecord["Type"]] != "None":
                        charRecords[bRecord["Type"]] += ', ' + selected_item
                    else:
                        charRecords[bRecord["Type"]] = selected_item
                else:
                    if charRecords['Inventory'] == "None":
                        charRecords['Inventory'] = {f"{selected_item}" : 1}
                    else:
                        if bRecord['Name'] not in charRecords['Inventory']:
                            charRecords['Inventory'][f"{selected_item}"] = 1 
                        else:
                            charRecords['Inventory'][f"{selected_item}"] += 1 
                try:
                    playersCollection = db.players
                    playersCollection.update_one({'_id': charRecords['_id']}, {"$set": {bRecord["Type"]:charRecords[bRecord["Type"]]}, "$inc": {"Event Token": -1}})
                except Exception as e:
                    print ('MONGO ERROR: ' + str(e))
                    shopEmbedmsg = await channel.send(embed=None, content="Uh oh, looks like something went wrong. Please try shop buy again.")
                else:
                    shopEmbed.description = out_text
                    await shopEmbedmsg.edit(embed=shopEmbed)

            else:
                try:
                    playersCollection = db.players
                    playersCollection.update_one({'_id': charRecords['_id']}, {"$inc": {f"Collectibles.{selected_item}": 1, "Event Token": -1}})
                except Exception as e:
                    print ('MONGO ERROR: ' + str(e))
                    shopEmbedmsg = await channel.send(embed=None, content="Uh oh, looks like something went wrong. Please try shop buy again.")
                else:
                    shopEmbed.description = out_text
                    await channel.send(embed=shopEmbed)
                
        ctx.command.reset_cooldown(ctx)

    @commands.cooldown(1, float('inf'), type=commands.BucketType.user)
    @is_log_channel()
    @commands.command()
    async def retire(self,ctx, char):
        channel = ctx.channel
        author = ctx.author
        guild = ctx.guild
        charEmbed = discord.Embed()
        charEmbedmsg = None

        charDict, charEmbedmsg = await checkForChar(ctx, char, charEmbed)

        def retireEmbedCheck(r, u):
            sameMessage = False
            if charEmbedmsg.id == r.message.id:
                sameMessage = True
            return sameMessage and ((str(r.emoji) == '✅') or (str(r.emoji) == '❌')) and u == author
        if charDict:
            charID = charDict['_id']

            charEmbed.title = f"Are you sure you want to retire {charDict['Name']}?"
            charEmbed.description = "✅: Yes\n\n❌: Cancel"
            if not charEmbedmsg:
                charEmbedmsg = await channel.send(embed=charEmbed)
            else:
                await charEmbedmsg.edit(embed=charEmbed)

            await charEmbedmsg.add_reaction('✅')
            await charEmbedmsg.add_reaction('❌')
            try:
                tReaction, tUser = await self.bot.wait_for("reaction_add", check=retireEmbedCheck , timeout=60)
            except asyncio.TimeoutError:
                await charEmbedmsg.delete()
                await channel.send(f'Retire cancelled. Try again using the same command:\n```yaml\n{commandPrefix}retire "character name"```')
                self.bot.get_command('retire').reset_cooldown(ctx)
                return
            else:
                await charEmbedmsg.clear_reactions()
                if tReaction.emoji == '❌':
                    await charEmbedmsg.edit(embed=None, content=f'Retire cancelled. Try again using the same command:\n```yaml\n{commandPrefix}retire "character name"```')
                    await charEmbedmsg.clear_reactions()
                    self.bot.get_command('retire').reset_cooldown(ctx)
                    return
                elif tReaction.emoji == '✅':
                    charEmbed.clear_fields()
                    try:
                        playersCollection = db.players
                        
                        deadCollection = db.dead
                        usersCollection = db.users
                        if "Guild" in charDict:
                            guildAmount = list(playersCollection.find({"User ID": str(author.id), "Guild": {"$regex": charDict['Guild'], '$options': 'i' }}))
                            # If there is only one of user's character in the guild remove the role.
                            if (len(guildAmount) <= 1):
                                await author.remove_roles(get(guild.roles, name = charDict['Guild']), reason=f"Left guild {charDict['Guild']}")

                        # usersRecord = list(usersCollection.find({"User ID": charDict['User ID']}))[0]
                        # if 'Games' not in usersRecord:
                            # usersRecord['Games'] = charDict['Games']
                        # else:
                            # usersRecord['Games'] += charDict['Games']
                        # usersCollection.update_one({'User ID': charDict['User ID']}, {"$set": {'Games': usersRecord['Games']}}, upsert=True)
                        playersCollection.delete_one({'_id': charID})
                        
                        deadCollection.insert_one(charDict)
                    except Exception as e:
                        print ('MONGO ERROR: ' + str(e))
                        charEmbedmsg = await channel.send(embed=None, content="Uh oh, looks like something went wrong. Please try retiring your character again.")
                    else:
                        print('Success')
                        if charEmbedmsg:
                            await charEmbedmsg.clear_reactions()
                            await charEmbedmsg.edit(embed=None, content =f"Congratulations! You have retired ***{charDict['Name']}***. ")
                        else: 
                            charEmbedmsg = await channel.send(embed=None, content=f"Congratulations! You have retired ***{charDict['Name']}***.")

        self.bot.get_command('retire').reset_cooldown(ctx)

    @commands.cooldown(1, float('inf'), type=commands.BucketType.user)
    @is_log_channel()
    @commands.command()
    async def death(self,ctx, char):
        channel = ctx.channel
        author = ctx.author
        guild = ctx.guild
        charEmbed = discord.Embed()
        charEmbedmsg = None
        charDict, charEmbedmsg = await checkForChar(ctx, char, charEmbed)


        def retireEmbedCheck(r, u):
            sameMessage = False
            if charEmbedmsg.id == r.message.id:
                sameMessage = True
            return sameMessage and ((str(r.emoji) == '✅') or (str(r.emoji) == '❌')) and u == author

        def deathEmbedCheck(r, u):
            sameMessage = False
            if charEmbedmsg.id == r.message.id:
                sameMessage = True
            return sameMessage and ((str(r.emoji) == '1️⃣') or (str(r.emoji) == '2️⃣') or (charDict['GP'] + deathDict["inc"]['GP']  >= gpNeeded and str(r.emoji) == '3️⃣') or (str(r.emoji) == '❌')) and u == author

        if charDict:
            if 'Death' not in charDict:
                await channel.send("Your character is not dead. You cannot use this command.")
                self.bot.get_command('death').reset_cooldown(ctx)
                return
            
            deathDict = charDict['Death']
            charID = charDict['_id']
            charLevel = charDict['Level']
            if charLevel < 5:
                gpNeeded = 100
                tierNum = 1
            elif charLevel < 11:
                gpNeeded = 500
                tierNum = 2
            elif charLevel < 17:
                gpNeeded = 750
                tierNum = 3
            elif charLevel < 21:
                gpNeeded = 1000
                tierNum = 4

            charEmbed.title = f"Character Death - {charDict['Name']}"
            charEmbed.set_footer(text= "React with ❌ to cancel.\nPlease react with a choice even if no reactions appear.")

            if charDict['GP'] + deathDict["inc"]['GP'] < gpNeeded:
                charEmbed.description = f"Please choose between these three options for {charDict['Name']}:\n\n1️⃣: Death - Retires your character.\n2️⃣: Survival - Forfeit rewards and survive.\n3️⃣: ~~Revival~~ - You currently have {charDict['GP'] + deathDict['inc']['GP']} GP but need {gpNeeded} GP to be revived."
            else:
                charEmbed.description = f"Please choose between these three options for {charDict['Name']}:\n\n1️⃣: Death - Retires your character.\n2️⃣: Survival - Forfeit rewards and survive.\n3️⃣: Revival - Revives your character for {gpNeeded} GP."
            if not charEmbedmsg:
                charEmbedmsg = await channel.send(embed=charEmbed)
            else:
                await charEmbedmsg.edit(embed=charEmbed)

            await charEmbedmsg.add_reaction('1️⃣')
            await charEmbedmsg.add_reaction('2️⃣')
            if charDict['GP'] + deathDict["inc"]['GP']  >= gpNeeded:
                await charEmbedmsg.add_reaction('3️⃣')
            await charEmbedmsg.add_reaction('❌')
            try:
                tReaction, tUser = await self.bot.wait_for("reaction_add", check=deathEmbedCheck , timeout=60)
            except asyncio.TimeoutError:
                await charEmbedmsg.delete()
                await channel.send(f'Death cancelled. Try again using the same command:\n```yaml\n{commandPrefix}death "character name"```')
                self.bot.get_command('death').reset_cooldown(ctx)
                return
            else:
                await charEmbedmsg.clear_reactions()
                if tReaction.emoji == '❌':
                    await charEmbedmsg.edit(embed=None, content=f'Death cancelled. Try again using the same command:\n```yaml\n{commandPrefix}death "character name"```')
                    await charEmbedmsg.clear_reactions()
                    self.bot.get_command('death').reset_cooldown(ctx)

                    return
                elif tReaction.emoji == '1️⃣':
                    charEmbed.title = f"Are you sure you want to retire {charDict['Name']}?"
                    charEmbed.description = "✅: Yes\n\n❌: Cancel"
                    charEmbed.set_footer(text=charEmbed.Empty)
                    await charEmbedmsg.edit(embed=charEmbed)
                    await charEmbedmsg.add_reaction('✅')
                    await charEmbedmsg.add_reaction('❌')
                    try:
                        tReaction, tUser = await self.bot.wait_for("reaction_add", check=retireEmbedCheck , timeout=60)
                    except asyncio.TimeoutError:
                        await charEmbedmsg.delete()
                        await channel.send(f'Death cancelled. Try again using the same command:\n```yaml\n{commandPrefix}death "character name"```')
                        self.bot.get_command('death').reset_cooldown(ctx)
                        return
                    else:
                        await charEmbedmsg.clear_reactions()
                        if tReaction.emoji == '❌':
                            await charEmbedmsg.edit(embed=None, content=f'Death cancelled. Try again using the same command:\n```yaml\n{commandPrefix}death "character name" "charactername"```')
                            await charEmbedmsg.clear_reactions()
                            self.bot.get_command('death').reset_cooldown(ctx)
                            return
                        elif tReaction.emoji == '✅':
                            charEmbed.clear_fields()
                            try:
                                playersCollection = db.players
                                deadCollection = db.dead
                                playersCollection.delete_one({'_id': charID})
                                guildAmount = list(playersCollection.find({"User ID": str(author.id), "Guild": {"$regex": charDict['Guild'], '$options': 'i' }}))
                                # If there is only one of user's character in the guild remove the role.
                                if (len(guildAmount) <= 1):
                                    await author.remove_roles(get(guild.roles, name = charDict['Guild']), reason=f"Left guild {charDict['Guild']}")

                                usersCollection = db.users
                                
                                deadCollection.insert_one(charDict)
                                pass
                                
                            except Exception as e:
                                print ('MONGO ERROR: ' + str(e))
                                charEmbedmsg = await channel.send(embed=None, content="Uh oh, looks like something went wrong. Please try retiring your character again.")
                            else:
                                print('Success')
                                if charEmbedmsg:
                                    await charEmbedmsg.clear_reactions()
                                    await charEmbedmsg.edit(embed=None, content ="Congratulations! You have retired your character.")

                                else: 
                                    charEmbedmsg = await channel.send(embed=None, content="Congratulations! You have retired your character.")
                    
                elif tReaction.emoji == '2️⃣' or tReaction.emoji == '3️⃣':
                    charEmbed.clear_fields()
                    surviveString = f"Congratulations! ***{charDict['Name']}*** has survived and has forfeited their rewards."
                    data ={}
                    if tReaction.emoji == '3️⃣':
                        for d in charDict["Death"].keys():
                            data["$"+d] = charDict["Death"][d]
                        data["$inc"]["GP"] -= gpNeeded
                        surviveString = f"Congratulations! ***{charDict['Name']}*** has been revived and has kept their rewards!"
                    data["$unset"] = {"Death":1}
                    
                    try:
                        playersCollection = db.players
                        playersCollection.update_one({'_id': charID}, data)
                        
                    except Exception as e:
                        print ('MONGO ERROR: ' + str(e))
                        charEmbedmsg = await channel.send(embed=None, content="Uh oh, looks like something went wrong. Please try the command again.")
                    else:
                        print("Success")
                        if charEmbedmsg:
                            await charEmbedmsg.clear_reactions()
                            await charEmbedmsg.edit(embed=None, content= surviveString)
                        else: 
                            charEmbedmsg = await channel.send(embed=None, content=surviveString)
        self.bot.get_command('death').reset_cooldown(ctx)


    @commands.cooldown(1, 5, type=commands.BucketType.member)
    @is_log_channel_or_game()
    @commands.command(aliases=['bag','inv'])
    async def inventory(self,ctx, char):
        channel = ctx.channel
        author = ctx.author
        guild = ctx.guild
        roleColors = {r.name:r.colour for r in guild.roles}
        charEmbed = discord.Embed()
        charEmbedmsg = None

        def userCheck(r,u):
            sameMessage = False
            if charEmbedmsg.id == r.message.id:
                sameMessage = True
            return sameMessage and u == ctx.author and (r.emoji == left or r.emoji == right)

        statusEmoji = ""
        charDict, charEmbedmsg = await checkForChar(ctx, char, charEmbed)
        if charDict:
            footer = f"To view your character's info, type the following command: {commandPrefix}info {charDict['Name']}"
            charLevel = charDict['Level']
            if charLevel < 5:
                role = 1
                charEmbed.colour = (roleColors['Junior Friend'])
            elif charLevel < 11:
                role = 2
                charEmbed.colour = (roleColors['Journeyfriend'])
            elif charLevel < 17:
                role = 3
                charEmbed.colour = (roleColors['Elite Friend'])
            elif charLevel < 21:
                role = 4
                charEmbed.colour = (roleColors['True Friend'])

            # Show Spellbook in inventory
            if 'Spellbook' in charDict:
                sPages = 1
                sPageStops = [0]
                spellBookString = ""
                for s in charDict['Spellbook']:
                    spellBookString += f"• {s['Name']} ({s['School']})\n" 
                    if len(spellBookString) > (768 * sPages):
                        sPageStops.append(len(spellBookString))
                        sPages += 1
                sPageStops.append(len(spellBookString))
                if sPages > 1:
                    for p in range(len(sPageStops)-1):
                        if(sPageStops[p+1] > sPageStops[p]):
                            charEmbed.add_field(name=f'Spellbook- p. {p+1}', value=spellBookString[sPageStops[p]:sPageStops[p+1]], inline=False)
                else:
                    charEmbed.add_field(name='Spellbook', value=spellBookString, inline=False)

            if 'Ritual Book' in charDict:
                ritualBookString = ""
                for s in charDict['Ritual Book']:
                    ritualBookString += f"• {s['Name']} ({s['School']})\n" 
                charEmbed.add_field(name='Ritual Book', value=ritualBookString, inline=False)

    
            # Show Consumables in inventory.
            cPages = 1
            cPageStops = [0]

            consumesString = ""
            consumesCount = collections.Counter(charDict['Consumables'].split(', '))
            for k, v in consumesCount.items():
                if v == 1:
                    consumesString += f"• {k}\n"
                else:
                    consumesString += f"• {k} x{v}\n"

                if len(consumesString) > (768 * cPages):
                    cPageStops.append(len(consumesString))
                    cPages += 1
            
            cPageStops.append(len(consumesString))

            if cPages > 1:
                for p in range(len(cPageStops)-1):
                    if(cPageStops[p+1] > cPageStops[p]):
                        charEmbed.add_field(name=f'Consumables - p. {p+1}', value=consumesString[cPageStops[p]:cPageStops[p+1]], inline=False)
            else:
                charEmbed.add_field(name='Consumables', value=consumesString, inline=False)

            # Show Magic items in inventory.
            mPages = 1
            mPageStops = [0]

            miString = ""
            miArray = collections.Counter(charDict['Magic Items'].split(', '))

            for m,v in miArray.items():
                if "Predecessor" in charDict and m in charDict["Predecessor"]:
                    upgrade_names = charDict['Predecessor'][m]["Names"]
                    stage = charDict['Predecessor'][m]["Stage"]
                    m = m + f" ({upgrade_names[stage]})"
                if v == 1:
                    miString += f"• {m}\n"
                else:
                    miString += f"• {m} x{v}\n"

                if len(miString) > (768 * mPages):
                    mPageStops.append(len(miString))
                    mPages += 1

            mPageStops.append(len(miString))
            if mPages > 1:
                for p in range(len(mPageStops)-1):
                    if(mPageStops[p+1] > mPageStops[p]):
                        charEmbed.add_field(name=f'Magic Items - p. {p+1}', value=miString[mPageStops[p]:mPageStops[p+1]], inline=False)
            else:
                charEmbed.add_field(name='Magic Items', value=miString, inline=False)


            charDictAuthor = guild.get_member(int(charDict['User ID']))
            charEmbed.title = f"{charDict['Name']} (Lv {charLevel}): Inventory"
            charEmbed.set_author(name=charDictAuthor, icon_url=charDictAuthor.avatar_url)
            if charDict['Inventory'] != 'None':
                typeDict = {}
                invCollection = db.shop
                namingDict = {}
                searchList = []
                keys = charDict['Inventory'].keys()
                for dbEntry in keys:
                    searchTerm = dbEntry
                    if(searchTerm.startswith("Silvered ")):
                        searchTerm=searchTerm.replace("Silvered ", "", 1)
                    if(searchTerm.startswith("Adamantine ")):
                        searchTerm= searchTerm.replace("Adamantine ", "", 1)
                    if(searchTerm in namingDict):
                        namingDict[searchTerm].append(dbEntry)
                    else:
                        namingDict[searchTerm] = [dbEntry]
                    searchList.append(searchTerm)
                charInv = list(invCollection.find({"Name": {'$in': searchList}}))
                for i in charInv:
                    iType = i['Type'].split('(')
                    if len(iType) == 1:
                        iType.append("")
                    else:
                        iType[1] = '(' + iType[1]
                
                    iType[0] = iType[0].strip()

                    if isinstance(i['Name'], str):
                        for entry in namingDict[i['Name']]:
                            amt = charDict['Inventory'][entry]
                            if amt == 1:
                                amt = ""
                            else:
                                amt = f"x{amt}"
                            
                            if iType[0] not in typeDict:
                                typeDict[iType[0]] = [f"• {entry} {iType[1]} {amt}\n"]
                            else:
                                typeDict[iType[0]].append(f"• {entry} {iType[1]} {amt}\n")
                    else:
                        for k,v in charDict['Inventory'].items():
                            if k in i['Name']:
                                amt = v
                                if amt == 1:
                                    amt = ""
                                else:
                                    amt = f"x{amt}"
                                
                                if iType[0] not in typeDict:
                                    typeDict[iType[0]] = [f"• {k} {iType[1]} {amt}\n"]
                                else:
                                    typeDict[iType[0]].append(f"• {k} {iType[1]} {amt}\n")

                for k, v in typeDict.items():
                    v.sort()
                    vString = ''.join(v)
                    if len(vString) > 1024:
                        vArray = vString.split("\n")
                        vPageStops = [0]
                        vPages = 1
                        vString = ""

                        for v in vArray:
                            vString += v + "\n"
                            if len(vString) > (768 * vPages):
                                vPageStops.append(len(vString))
                                vPages += 1

                        vPageStops.append(len(vString))
                        if vPages > 1  and vPageStops[-1] > vPageStops[-2]:
                            for p in range(len(vPageStops)-1):
                                charEmbed.add_field(name=f'{k} - p. {p+1}', value=vString[vPageStops[p]:vPageStops[p+1]], inline=False)

                    else:
                        charEmbed.add_field(name=k, value=vString, inline=False)
            if "Collectibles" in charDict:
                vString = ""
                for k, v in charDict["Collectibles"].items():
                        vString += f'• {k} x{v}\n'
                vPages = 0
                vPageStops = [0]
                if len(vString) > 1024:
                    vArray = vString.split("\n")
                    vPages = 1
                    vString = ""

                    for v in vArray:
                        vString += v + "\n"
                        if len(vString) > (768 * vPages):
                            vPageStops.append(len(vString))
                            vPages += 1

                    vPageStops.append(len(vString))
                if vPages > 1  and vPageStops[-1] > vPageStops[-2]:
                    for p in range(len(vPageStops)-1):
                        charEmbed.add_field(name=f'{k} - p. {p+1}', value=vString[vPageStops[p]:vPageStops[p+1]], inline=False)

                else:
                    charEmbed.add_field(name="Collectibles", value=vString, inline=False)
            
            embedList = [discord.Embed()]
            pages = 1
            if len(charEmbed) > 2048:
                charEmbedDict = charEmbed.to_dict()
                for f in charEmbedDict['fields']:
                    if len(embedList[pages - 1]) > 2048:
                        pages += 1
                        embedList.append(discord.Embed())
                    embedList[pages - 1].add_field(name=f["name"], value=f["value"] ,inline=False)
            else:
                 embedList[0] = charEmbed


            page = 0
            embedList[0].set_footer(text=f"{footer}\nPage {page+1} of {pages}")

            if not charEmbedmsg:
                charEmbedmsg = await ctx.channel.send(embed=embedList[0])
            else:
                await charEmbedmsg.edit(embed=embedList[0])

            while pages > 1:
                await charEmbedmsg.add_reaction(left) 
                await charEmbedmsg.add_reaction(right)
                try:
                    hReact, hUser = await self.bot.wait_for("reaction_add", check=userCheck, timeout=30.0)
                except asyncio.TimeoutError:
                    await charEmbedmsg.edit(content=f"Your user menu has timed out! I'll leave this page open for you. If you need to cycle through the menu again then use the same command!")
                    await charEmbedmsg.clear_reactions()
                    await charEmbedmsg.add_reaction('💤')
                    return
                else:
                    if hReact.emoji == left:
                        page -= 1
                        if page < 0:
                            page = len(embedList) - 1
                    if hReact.emoji == right:
                        page += 1
                        if page > len(embedList) - 1:
                            page = 0
                    embedList[page].set_footer(text=f"{footer}\nPage {page+1} of {pages}")
                    await charEmbedmsg.edit(embed=embedList[page]) 
                    await charEmbedmsg.clear_reactions()

            self.bot.get_command('inv').reset_cooldown(ctx)

    @commands.cooldown(1, 5, type=commands.BucketType.member)
    @is_log_channel()
    @commands.command()
    async def user(self,ctx):
        channel = ctx.channel
        author = ctx.author
        guild = ctx.guild
        charEmbed = discord.Embed()
        charEmbedmsg = None

        usersCollection = db.users
        userRecords = usersCollection.find_one({"User ID": str(author.id)})

        def userCheck(r,u):
            sameMessage = False
            if charEmbedmsg.id == r.message.id:
                sameMessage = True
            return sameMessage and u == ctx.author and (r.emoji == left or r.emoji == right)

        if not userRecords: 
            userRecords = {'User ID': str(author.id), 'Games' : 0}
            usersData = db.users.insert_one(userRecords)  
            await channel.send(f'A user profile has been created.') 
        playersCollection = db.players
        charRecords = list(playersCollection.find({"User ID": str(author.id)}))

        totalGamesPlayed = 0
        pages = 1
        pageStops = [0]
        charString = ""
        charDictTiers = [[],[],[],[],[]]
        charEmbed.set_author(name=author, icon_url=author.avatar_url)
        charEmbed.title = f"{author.display_name}" 
        if charRecords:
            charRecords = sorted(charRecords, key=lambda k: k['Name']) 


            for c in charRecords:
                if c["Level"] < 5:
                    charDictTiers[0].append(c)
                elif c["Level"] < 11:
                    charDictTiers[1].append(c)
                elif c["Level"] < 17:
                    charDictTiers[2].append(c)
                elif c["Level"] < 20:
                    charDictTiers[3].append(c)
                else:
                    charDictTiers[4].append(c)


            for n in range(0,len(charDictTiers)):
                charString += f"\n———**Tier {n+1} Characters:**———\n"
                for charDict in charDictTiers[n]:
                    tempCharString = charString
                    char_race = charDict['Race']
                    if "Reflavor" in charDict:
                        char_race = f"{charDict['Reflavor']} ({char_race})"
                    charString += f"• **{charDict['Name']}**: Lv {charDict['Level']}, {char_race}, {charDict['Class']}\n"

                    if 'Guild' in charDict:
                        charString += f"---Guild: *{charDict['Guild']}*\n"

                    if len(charString) > (768 * pages):
                        pageStops.append(len(tempCharString))
                        pages += 1
        else:
            charString = "None"
            
        pageStops.append(len(charString))

        if 'Games' in userRecords:
            totalGamesPlayed += userRecords['Games']
        if 'Double' in userRecords and userRecords["Double"]>0:
            charEmbed.add_field(name="Double Reward", inline=False, value=f"""Your next **{userRecords["Double"]}** games will have double rewards.""")


        if "Guilds" in userRecords:
            guildNoodles = "• "
            guildNoodles += "\n• ".join(userRecords["Guilds"])
            charEmbed.add_field(name="Guilds",  inline=False, value=f"""You have created **{len(userRecords["Guilds"])}** guilds:\n {guildNoodles}""")

        if "Campaigns" in userRecords:
            campaignString = ""
            for u, v in userRecords['Campaigns'].items():
                campaignString += f"• {(not v['Active'])*'~~'}{u}{(not v['Active'])*'~~'}: {v['Sessions']} sessions, {timeConversion(v['Time'])}\n"

            charEmbed.add_field(name='Campaigns', value=campaignString, inline=False)
        

        if 'Noodles' in userRecords:
            charEmbed.description = f"Total One-shots Played/Hosted: {totalGamesPlayed}\nNoodles: {userRecords['Noodles']}\n"
        else:
            charEmbed.description = f"Total One-shots Played/Hosted: {totalGamesPlayed}\nNoodles: 0 (Try hosting sessions to receive Noodles!)\n"
    
        charEmbed.description += f"Total Characters: {len(charRecords)}\nTier 1 Characters: {len(charDictTiers[0])}\nTier 2 Characters: {len(charDictTiers[1])}\nTier 3 Characters: {len(charDictTiers[2])}\nTier 4 Characters: {len(charDictTiers[3])}\nTier 5 Characters: {len(charDictTiers[4])}"

        userEmbedList = [charEmbed]
        page = 0
        userEmbedList[0].set_footer(text=f"Page {page+1} of {pages}")
        if pages > 1:
            for p in range(len(pageStops)-1):
                if p != 0:
                    userEmbedList.append(discord.Embed())
                userEmbedList[p].add_field(name=f'Characters - p. {p+1}:', value=charString[pageStops[p]:pageStops[p+1]], inline=False)

        else:
            charEmbed.add_field(name=f'Characters', value=charString, inline=False)

        if not charEmbedmsg:
            charEmbedmsg = await ctx.channel.send(embed=charEmbed)
        else:
            await charEmbedmsg.edit(embed=charEmbed)

        while pages > 1:
            await charEmbedmsg.add_reaction(left) 
            await charEmbedmsg.add_reaction(right)
            try:
                hReact, hUser = await self.bot.wait_for("reaction_add", check=userCheck, timeout=30.0)
            except asyncio.TimeoutError:
                await charEmbedmsg.edit(content=f"Your user menu has timed out! I'll leave this page open for you. If you need to cycle through the menu again then use the same command!")
                await charEmbedmsg.clear_reactions()
                await charEmbedmsg.add_reaction('💤')
                return
            else:
                if hReact.emoji == left:
                    page -= 1
                    if page < 0:
                        page = len(userEmbedList) - 1
                if hReact.emoji == right:
                    page += 1
                    if page > len(userEmbedList) - 1:
                        page = 0
                userEmbedList[page].set_footer(text=f"Page {page+1} of {pages}")
                await charEmbedmsg.edit(embed=userEmbedList[page]) 
                await charEmbedmsg.clear_reactions()

            
            
           
    @commands.cooldown(1, 5, type=commands.BucketType.member)
    @is_log_channel_or_game()
    @commands.command(aliases=['i', 'char'])
    async def info(self,ctx, char):
        channel = ctx.channel
        author = ctx.author
        guild = ctx.guild
        roleColors = {r.name:r.colour for r in guild.roles}
        charEmbed = discord.Embed()
        charEmbedmsg = None

        statusEmoji = ""
        charDict, charEmbedmsg = await checkForChar(ctx, char, charEmbed)
        if charDict:
            footer = f"To view your character's inventory, type the following command: {commandPrefix}inv {charDict['Name']}"
            
            char_race = charDict['Race']
            if "Reflavor" in charDict:
                char_race = f"{charDict['Reflavor']} ({char_race})"
            nick_string = ""
            if "Nickname" in charDict and charDict['Nickname'] != "":
                nick_string = f"Goes By: **{charDict['Nickname']}**\n"
            description = f"{nick_string}{char_race}\n{charDict['Class']}\n{charDict['Background']}\nOne-shots Played: {charDict['Games']}\n"
            if 'Proficiency' in charDict:
                description +=  f"Extra Training: {charDict['Proficiency']}\n"
            if 'NoodleTraining' in charDict:
                description +=  f"Noodle Training: {charDict['NoodleTraining']}\n"
            description += f":moneybag: {charDict['GP']} GP\n"
            charLevel = charDict['Level']
            if charLevel < 5:
                role = 1
                charEmbed.colour = (roleColors['Junior Friend'])
            elif charLevel < 11:
                role = 2
                charEmbed.colour = (roleColors['Journeyfriend'])
            elif charLevel < 17:
                role = 3
                charEmbed.colour = (roleColors['Elite Friend'])
            elif charLevel < 20:
                role = 4
                charEmbed.colour = (roleColors['True Friend'])
            else:
                role = 5
                charEmbed.colour = (roleColors['Ascended Friend'])

            cpSplit = charDict['CP']
            if charLevel < 20 and cpSplit >= cp_bound_array[role-1][0]:
                footer += f'\nYou need to level up! Use the following command before playing in another quest to do so: {commandPrefix}levelup {charDict["Name"]}'


            if charLevel == 4 or charLevel == 10 or charLevel == 16:
                footer += f'\nYou will no longer receive Tier {role} TP the next time you level up! Please plan accordingly.'

            if 'Death' in charDict:
                statusEmoji = "⚰️"
                description += f"{statusEmoji} Status: **DEAD** -  decide their fate with the following command: {commandPrefix}death" 
                charEmbed.colour = discord.Colour(0xbb0a1e)

            charDictAuthor = guild.get_member(int(charDict['User ID']))
            charEmbed.set_author(name=charDictAuthor, icon_url=charDictAuthor.avatar_url)
            charEmbed.description = description
            charEmbed.clear_fields()    
            charEmbed.title = f"{charDict['Name']} (Lv {charLevel}) - {charDict['CP']}/{cp_bound_array[role-1][1]} CP"
            tpString = ""
            for i in range (1,6):
                if f"T{i} TP" in charDict:
                    tpString += f"**Tier {i} TP**: {charDict[f'T{i} TP']} \n" 
            charEmbed.add_field(name='TP', value=f"Current TP Item: **{charDict['Current Item']}**\n{tpString}", inline=True)
            if 'Guild' in charDict:
                charEmbed.add_field(name='Guild', value=f"{charDict['Guild']}\nGuild Rank: {charDict['Guild Rank']}", inline=True)
            charEmbed.add_field(name='Feats', value=charDict['Feats'], inline=False)

            if 'Free Spells' in charDict:
                fsString = ""
                fsIndex = 0
                for el in charDict['Free Spells']:
                    if el > 0:
                        fsString += f"Level {fsIndex+1}: {el} free spells\n"
                    fsIndex += 1

                if fsString:
                    charEmbed.add_field(name='Free Spellbook Copies Available', value=fsString , inline=False)

            if 'Max Stats' not in charDict:
                maxStatDict = charDict['Max Stats'] = {'STR': 20 ,'DEX': 20,'CON': 20, 'INT': 20, 'WIS': 20,'CHA': 20}
            else:
                maxStatDict = charDict['Max Stats']

            for sk in charDict['Max Stats'].keys():
                if charDict[sk] > charDict['Max Stats'][sk]:
                    charDict[sk] = charDict['Max Stats'][sk]
            
            specialCollection = db.special
            specialRecords = list(specialCollection.find())

            totalHPAdd = 0
            for s in specialRecords:
                                            
                                    
                if 'Attuned' in charDict:
                    if s['Type'] == "Attuned":
                        if s['Name'] in charDict[s['Type']]:
                            if 'HP' in s:
                                totalHPAdd += s['HP']

            # Check for stat increases in attuned magic items.
            if 'Attuned' in charDict:
                charEmbed.add_field(name='Attuned', value='• ' + charDict['Attuned'].replace(', ', '\n• '), inline=False)
                statBonusDict = { 'STR': 0 ,'DEX': 0,'CON': 0, 'INT': 0, 'WIS': 0,'CHA': 0}
                for a in charDict['Attuned'].split(', '):
                    if '[' in a and ']' in a:
                        statBonus = a[a.find("[")+1:a.find("]")] 
                        if '+' not in statBonus and '-' not in statBonus:
                            statSplit = statBonus.split(' ')
                            modStat = str(charDict[statSplit[0]]).replace(')', '').split(' (')[0]
                            if '[' in modStat and ']' in modStat:
                                oldStat = modStat[modStat.find("[")+1:modStat.find("]")] 
                                if '+' not in modStat and '-' not in modStat:
                                    modStat = modStat.split(' [')[0]
                                    if int(oldStat) > int(statSplit[1]):
                                        charDict[statSplit[0]] = f"{modStat} ({oldStat})"
                                else:
                                    modStat = modStat.split(' [')[0]
                                    if (int(modStat) + int(statBonusDict[statSplit[0]])) > int(statSplit[1]):
                                        charDict[statSplit[0]] = f"{modStat} (+{statBonusDict[statSplit[0]]})" 
                                    else:
                                        charDict[statSplit[0]] = f"{modStat} ({statSplit[1]})"

                            elif int(statSplit[1]) > int(modStat):
                                maxStatNum = statSplit[1]
                                if '(' in str(charDict[statSplit[0]]):
                                    maxStatNum = max(int(str((charDict[statSplit[0]])).replace(')', '').split(' (')[1]), int(statSplit[1]) )
                                charDict[statSplit[0]] = f"{modStat} ({maxStatNum})"

                        elif '+' in statBonus:
                            statBonusSplit = statBonus.split(';')
                            statSplit = statBonusSplit[0].split(' +')
                            if 'MAX' in statSplit[0]:
                                maxStat = statSplit[0][:-3]
                                statSplit[0] = statSplit[0].replace(maxStat, "")
                                maxStat = maxStat.split(" ")
                                maxStatDict[statSplit[0]] += int(statSplit[1])

                            modStat = str(charDict[statSplit[0]])
                            modStat = modStat.split(' (')[0]
                            statBonusDict[statSplit[0]] += int(statSplit[1])
                            statName = charDict[statSplit[0]]
                            maxStatBonus = []
                            maxCalc = int(modStat) + int(statBonusDict[statSplit[0]]) > maxStatDict[statSplit[0]]

                            if maxCalc:
                                statBonusDict[statSplit[0]] = maxStatDict[statSplit[0]] - int(modStat)
                            if statBonusDict[statSplit[0]] > 0: 
                                charDict[statSplit[0]] = f"{modStat} (+{statBonusDict[statSplit[0]]})" 
                            else:
                                charDict[statSplit[0]] = f"{modStat}" 

                # recalc CON
                if statBonusDict['CON'] != 0 or '(' in str(charDict['CON']):
                    trueConValue = charDict['CON']
                    conValue = charDict['CON'].replace(')', '').split('(')            

                    if len(conValue) > 1:
                        trueConValue = max(map(lambda x: int(x), conValue))

                    if '+' in conValue[1]:
                        trueConValue = int(conValue[1].replace('+', '')) + int(conValue[0])


                    charDict['HP'] -= ((int(conValue[0]) - 10) // 2) * charLevel
                    charDict['HP'] += ((int(trueConValue) - 10) // 2) * charLevel

            charDict['HP'] += totalHPAdd * charLevel

            charEmbed.add_field(name='Stats', value=f":heart: {charDict['HP']} Max HP\n**STR**: {charDict['STR']} \n**DEX**: {charDict['DEX']} \n**CON**: {charDict['CON']} \n**INT**: {charDict['INT']} \n**WIS**: {charDict['WIS']} \n**CHA**: {charDict['CHA']}", inline=False)
            
            charEmbed.set_footer(text=footer)

            if 'Image' in charDict:
                charEmbed.set_thumbnail(url=charDict['Image'])

            if not charEmbedmsg:
                charEmbedmsg = await ctx.channel.send(embed=charEmbed)
            else:
                await charEmbedmsg.edit(embed=charEmbed)

            self.bot.get_command('info').reset_cooldown(ctx)

    @commands.cooldown(1, 5, type=commands.BucketType.member)
    @commands.command(aliases=['img'])
    @is_log_channel()
    async def image(self,ctx, char, url):

        channel = ctx.channel
        author = ctx.author
        guild = ctx.guild
        charEmbed = discord.Embed()

        infoRecords, charEmbedmsg = await checkForChar(ctx, char, charEmbed)

        if infoRecords:
            charID = infoRecords['_id']
            data = {
                'Image': url
            }

            try:
                r = requests.head(url)
                if r.status_code != requests.codes.ok:
                    await ctx.channel.send(content=f'It looks like the URL is either invalid or contains a broken image. Please follow this format:\n```yaml\n{commandPrefix}image "character name" URL```\n') 
                    return
            except:
                await ctx.channel.send(content=f'It looks like the URL is either invalid or contains a broken image. Please follow this format:\n```yaml\n{commandPrefix}image "character name" URL```\n') 

                return
              
            try:
                playersCollection = db.players
                playersCollection.update_one({'_id': charID}, {"$set": data})
            except Exception as e:
                print ('MONGO ERROR: ' + str(e))
                charEmbedmsg = await channel.send(embed=None, content="Uh oh, looks like something went wrong. Please try creating your character again.")
            else:
                print('Success')
                await ctx.channel.send(content=f'I have updated the image for ***{char}***. Please double-check using one of the following commands:\n```yaml\n{commandPrefix}info "character name"\n{commandPrefix}char "character name"\n{commandPrefix}i "character name"```')
    
    @commands.cooldown(1, 5, type=commands.BucketType.member)
    @is_log_channel()
    @commands.command(aliases=['r6'])
    async def reflavor(self,ctx, char, *, new_race):
        if( len(new_race) > 20 or len(new_race) <1):
            await ctx.channel.send(content=f'The new race must be between 1 and 20 symbols.')
            return

    
        channel = ctx.channel
        author = ctx.author
        guild = ctx.guild
        charEmbed = discord.Embed()

        infoRecords, charEmbedmsg = await checkForChar(ctx, char, charEmbed)

        if infoRecords:
            charID = infoRecords['_id']
            data = {
                'Reflavor': new_race
            }

            try:
                playersCollection = db.players
                playersCollection.update_one({'_id': charID}, {"$set": data})
            except Exception as e:
                print ('MONGO ERROR: ' + str(e))
                charEmbedmsg = await channel.send(embed=None, content="Uh oh, looks like something went wrong. Please try creating your character again.")
            else:
                print('Success')
                await ctx.channel.send(content=f'I have updated the race for ***{char}***. Please double-check using one of the following commands:\n```yaml\n{commandPrefix}info "character name"\n{commandPrefix}char "character name"\n{commandPrefix}i "character name"```')
    
    @commands.cooldown(1, 5, type=commands.BucketType.member)
    @is_log_channel()
    @commands.command(aliases=['aka'])
    async def alias(self,ctx, char, new_name = ""):
        channel = ctx.channel
        author = ctx.author
        guild = ctx.guild
        msg = self.name_check(new_name, author)
        if msg:
            await channel.send(msg)
            return
            
        charEmbed = discord.Embed()

        infoRecords, charEmbedmsg = await checkForChar(ctx, char, charEmbed)

        if infoRecords:
            charID = infoRecords['_id']
            data = {
                'Nickname': new_name
            }

            try:
                playersCollection = db.players
                playersCollection.update_one({'_id': charID}, {"$set": data})
            except Exception as e:
                print ('MONGO ERROR: ' + str(e))
                charEmbedmsg = await channel.send(embed=None, content="Uh oh, looks like something went wrong. Please try creating your character again.")
            else:
                print('Success')
                await ctx.channel.send(content=f'I have updated the name for ***{char}***. Please double-check using one of the following commands:\n```yaml\n{commandPrefix}info "character name"\n{commandPrefix}char "character name"\n{commandPrefix}i "character name"```')
            
    def name_check(self, name, author):
        msg = ""
        # Name should be less then 65 chars
        if len(name) > 64:
            msg += ":warning: Your character's name is too long! The limit is 64 characters.\n"

        # Reserved for regex, lets not use these for character names please
        invalidChars = ["[", "]", "?", '"', "\\", "*", "$", "{", "+", "}", "^", ">", "<", "|", "(",")" ]

        for i in invalidChars:
            if i in name:
                msg += f":warning: Your character's name cannot contain `{i}`. Please revise your character name.\n"
        # if msg == "":
            # playersCollection = db.players
            # userRecords = list(playersCollection.find({"User ID": str(author.id), "Name": name }))

            # if userRecords != list():
                # msg += f":warning: You already have a character by the name of ***{name}***! Please use a different name.\n"
        
        return msg
    
    @commands.cooldown(1, float('inf'), type=commands.BucketType.user)
    @is_log_channel()
    @commands.command(aliases=['lvl', 'lvlup', 'lv'])
    async def levelup(self,ctx, char):
        channel = ctx.channel
        author = ctx.author
        guild = ctx.guild
        levelUpEmbed = discord.Embed ()
        characterCog = self.bot.get_cog('Character')
        infoRecords, levelUpEmbedmsg = await checkForChar(ctx, char, levelUpEmbed)
        charClassChoice = ""
        if infoRecords:
            charID = infoRecords['_id']
            charDict = {}
            charName = infoRecords['Name']
            charClass = infoRecords['Class']
            cpSplit= infoRecords['CP']
            charLevel = infoRecords['Level']
            charStats = {'STR':infoRecords['STR'], 'DEX':infoRecords['DEX'], 'CON':infoRecords['CON'], 'INT':infoRecords['INT'], 'WIS':infoRecords['WIS'], 'CHA':infoRecords['CHA']}
            charHP = infoRecords['HP']
            charFeats = infoRecords['Feats']
            freeSpells = [0] * 9
            
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
                
            if 'Free Spells' in infoRecords:
                freeSpells = infoRecords['Free Spells']

            if 'Death' in infoRecords.keys():
                await channel.send(f'You cannot level up a dead character. Use the following command to decide their fate:\n```yaml\n$death "{charRecords["Name"]}"```')
                self.bot.get_command('levelup').reset_cooldown(ctx)
                return

            if charLevel > 19:
                await channel.send(f"***{infoRecords['Name']}*** is level 20 and cannot level up anymore.")
                self.bot.get_command('levelup').reset_cooldown(ctx)
                return
                

            elif cpSplit < cp_bound_array[tierNum-1][0]:
                await channel.send(f'***{charName}*** is not ready to level up. They currently have **{cpSplit}/{cp_bound_array[tierNum-1][1]}** CP.')
                self.bot.get_command('levelup').reset_cooldown(ctx)
                return
            else:
                cRecords, levelUpEmbed, levelUpEmbedmsg = await callAPI(ctx, levelUpEmbed, levelUpEmbedmsg,'classes')
                classRecords = sorted(cRecords, key=lambda k: k['Name']) 
                leftCP = cpSplit - cp_bound_array[tierNum-1][0]
                newCharLevel = charLevel  + 1
                totalCP = leftCP
                subclasses = []
                if '/' in charClass:
                    tempClassList = charClass.split(' / ')
                    for t in tempClassList:
                        temp = t.split(' ')
                        tempSub = ""
                        if '(' and ')' in t:
                            tempSub = t[t.find("(")+1:t.find(")")]

                        subclasses.append({'Name':temp[0], 'Subclass':tempSub, 'Level':int(temp[1])})
                else:
                    tempSub = ""
                    if '(' and ')' in charClass:
                        tempSub = charClass[charClass.find("(")+1:charClass.find(")")]
                    subclasses.append({'Name':charClass, 'Subclass':tempSub, 'Level':charLevel})

                for c in classRecords:
                    for s in subclasses:
                        if c['Name'] in s['Name']:
                            s['Hit Die Max'] = c['Hit Die Max']
                            s['Hit Die Average'] = c['Hit Die Average']
                            if "Spellcasting" in c:
                                s["Spellcasting"] = True

                
                def multiclassEmbedCheck(r, u):
                        sameMessage = False
                        if levelUpEmbedmsg.id == r.message.id:
                            sameMessage = True
                        return sameMessage and ((str(r.emoji) == '✅' and chooseClassString != "") or (str(r.emoji) == '🚫') or (str(r.emoji) == '❌')) and u == author
                def alphaEmbedCheck(r, u):
                        sameMessage = False
                        if levelUpEmbedmsg.id == r.message.id:
                            sameMessage = True
                        return sameMessage and ((r.emoji in alphaEmojis[:alphaIndex]) or (str(r.emoji) == '❌')) and u == author


                levelUpEmbed.clear_fields()
                lvl = charLevel
                newLevel = charLevel + 1
                levelUpEmbed.title = f"{charName}: Level Up! {lvl} → {newLevel}"
                levelUpEmbed.description = f"{infoRecords['Race']}: {charClass}\n**STR**: {charStats['STR']} **DEX**: {charStats['DEX']} **CON**: {charStats['CON']} **INT**: {charStats['INT']} **WIS**: {charStats['WIS']} **CHA**: {charStats['CHA']}"
                chooseClassString = ""
                alphaIndex = 0
                classes = []
                lvlClass = charClass

                # Multiclass Requirements
                failMulticlassList = []
                baseClass = {'Name': ''}
                
                for cRecord in classRecords:
                    if cRecord['Name'] in charClass:
                        baseClass = cRecord

                    statReq = cRecord['Multiclass'].split(' ')
                    if cRecord['Multiclass'] != 'None':
                        if '/' not in cRecord['Multiclass'] and '+' not in cRecord['Multiclass']:
                            if int(infoRecords[statReq[0]]) < int(statReq[1]):
                                failMulticlassList.append(cRecord['Name'])
                                continue
                        elif '/' in cRecord['Multiclass']:
                            statReq[0] = statReq[0].split('/')
                            reqFufill = False
                            for s in statReq[0]:
                                if int(infoRecords[s]) >= int(statReq[1]):
                                    reqFufill = True
                            if not reqFufill:
                                failMulticlassList.append(cRecord['Name'])
                                continue

                        elif '+' in cRecord['Multiclass']:
                            statReq[0] = statReq[0].split('+')
                            reqFufill = True
                            for s in statReq[0]:
                                if int(infoRecords[s]) < int(statReq[1]):
                                    reqFufill = False
                                    break
                            if not reqFufill:
                                failMulticlassList.append(cRecord['Name'])
                                continue


                        if cRecord['Name'] not in failMulticlassList and cRecord['Name'] != baseClass['Name']:
                            chooseClassString += f"{alphaEmojis[alphaIndex]}: {cRecord['Name']}\n"
                            alphaIndex += 1
                            classes.append(cRecord['Name'])


                # New Multiclass
                if chooseClassString != "":
                    levelUpEmbed.add_field(name="Would you like to choose a new multiclass?", value='✅: Yes\n\n🚫: No\n\n❌: Cancel')
                else:
                    levelUpEmbed.add_field(name="""~~Would you like to choose a new multiclass?~~\nThere are no classes available to multiclass into. Please react with "No" to proceed.""", value='~~✅: Yes~~\n\n🚫: No\n\n❌: Cancel')

                if not levelUpEmbedmsg:
                    levelUpEmbedmsg = await channel.send(embed=levelUpEmbed)
                else:
                    await levelUpEmbedmsg.edit(embed=levelUpEmbed)
                if chooseClassString != "":
                    await levelUpEmbedmsg.add_reaction('✅')
                await levelUpEmbedmsg.add_reaction('🚫')
                await levelUpEmbedmsg.add_reaction('❌')
                try:
                    tReaction, tUser = await self.bot.wait_for("reaction_add", check=multiclassEmbedCheck, timeout=60)
                except asyncio.TimeoutError:
                    await levelUpEmbedmsg.delete()
                    await channel.send(f'Level up cancelled. Try again using the same command or one of its shorthand forms:\n```yaml\n{commandPrefix}levelup "character name"\n{commandPrefix}lvlup "character name"\n{commandPrefix}lvl "character name"\n{commandPrefix}lv "character name"```')
                    self.bot.get_command('levelup').reset_cooldown(ctx)
                    return
                else:
                    await levelUpEmbedmsg.clear_reactions()
                    if tReaction.emoji == '❌':
                        await levelUpEmbedmsg.edit(embed=None, content=f"Level up cancelled. Try again using the same command or one of its shorthand forms:\n```yaml\n{commandPrefix}levelup \"character name\"\n{commandPrefix}lvlup \"character name\"\n{commandPrefix}lvl \"character name\"\n{commandPrefix}lv \"character name\"```")
                        await levelUpEmbedmsg.clear_reactions()
                        self.bot.get_command('levelup').reset_cooldown(ctx)
                        return
                    elif tReaction.emoji == '✅':
                        levelUpEmbed.clear_fields()
                        if baseClass['Name'] in failMulticlassList:
                            await levelUpEmbedmsg.edit(embed=None, content=f"You cannot multiclass right now because your base class, **{baseClass['Name']}**, requires at least **{baseClass['Multiclass']}**.\nCurrent stats: **STR**: {charStats['STR']} **DEX**: {charStats['DEX']} **CON**: {charStats['CON']} **INT**: {charStats['INT']} **WIS**: {charStats['WIS']} **CHA**: {charStats['CHA']}")

                            await levelUpEmbedmsg.clear_reactions()
                            self.bot.get_command('levelup').reset_cooldown(ctx)
                            return

                        levelUpEmbed.add_field(name="Pick a new class that you would like to multiclass into.", value=chooseClassString)

                        await levelUpEmbedmsg.edit(embed=levelUpEmbed)
                        await levelUpEmbedmsg.add_reaction('❌')
                        try:
                            tReaction, tUser = await self.bot.wait_for("reaction_add", check=alphaEmbedCheck, timeout=60)
                        except asyncio.TimeoutError:
                            await levelUpEmbedmsg.delete()
                            await channel.send(f'Level up cancelled. Try again using the same command or one of its shorthand forms:\n```yaml\n{commandPrefix}levelup "character name"\n{commandPrefix}lvlup "character name"\n{commandPrefix}lvl "character name"\n{commandPrefix}lv "character name"```')
                            self.bot.get_command('levelup').reset_cooldown(ctx)
                            return
                        else:
                            await levelUpEmbedmsg.clear_reactions()
                            if tReaction.emoji == '❌':
                                await levelUpEmbedmsg.edit(embed=None, content=f"Level up cancelled. Try again using the same command or one of its shorthand forms:\n```yaml\n{commandPrefix}levelup \"character name\"\n{commandPrefix}lvlup \"character name\"\n{commandPrefix}lvl \"character name\"\n{commandPrefix}lv \"character name\"```")
                                await levelUpEmbedmsg.clear_reactions()
                                self.bot.get_command('levelup').reset_cooldown(ctx)
                                return

                            if '/' not in charClass:
                                if '(' in charClass and ')' in charClass:
                                    charClass = charClass.replace('(', f"{lvl} (")
                                else:
                                    charClass += ' ' + str(lvl)
                                
                            charClassChoice = classes[alphaEmojis.index(tReaction.emoji)]
                            charClass += f' / {charClassChoice} 1'
                            lvlClass = charClassChoice
                            for c in classRecords:
                                if c['Name'] in charClassChoice:
                                    subclass_entry_add = {'Name': charClassChoice, 'Subclass': '', 'Level': 1, 'Hit Die Max': c['Hit Die Max'], 'Hit Die Average': c['Hit Die Average']}
                                    if "Spellcasting" in c:
                                        subclass_entry_add["Spellcasting"] = True

                                    subclasses.append(subclass_entry_add)

                            if "Wizard" in charClassChoice:
                                freeSpells[0] += 6

                            levelUpEmbed.description = f"{infoRecords['Race']}: {charClass}\n**STR**:{charStats['STR']} **DEX**:{charStats['DEX']} **CON**:{charStats['CON']} **INT**:{charStats['INT']} **WIS**:{charStats['WIS']} **CHA**:{charStats['CHA']}"
                            levelUpEmbed.clear_fields()
                    elif tReaction.emoji == '🚫':
                        if '/' not in charClass:
                            lvlClass = charClass
                            subclasses[0]['Level'] += 1
                            if 'Wizard' in charClass: 
                                fsLvl = (subclasses[0]['Level'] - 1) // 2
                                if fsLvl > 8:
                                    fsLvl = 8

                                freeSpells[fsLvl] += 2
                        else:
                            multiclassLevelString = ""
                            alphaIndex = 0
                            for sc in subclasses:
                                multiclassLevelString += f"{alphaEmojis[alphaIndex]}: {sc['Name']} Level {sc['Level']}\n"
                                alphaIndex += 1
                            levelUpEmbed.clear_fields()
                            levelUpEmbed.add_field(name=f"What class would you like to level up?", value=multiclassLevelString, inline=False)
                            await levelUpEmbedmsg.edit(embed=levelUpEmbed)
                            await levelUpEmbedmsg.add_reaction('❌')
                            try:
                                tReaction, tUser = await self.bot.wait_for("reaction_add", check=alphaEmbedCheck, timeout=60)
                            except asyncio.TimeoutError:
                                await levelUpEmbedmsg.delete()
                                await channel.send(f'Level up timed out! Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                                self.bot.get_command('levelup').reset_cooldown(ctx)
                                return
                            else:
                                if tReaction.emoji == '❌':
                                    await levelUpEmbedmsg.edit(embed=None, content=f"Level up cancelled. Try again using the same command or one of its shorthand forms:\n```yaml\n{commandPrefix}levelup \"character name\"\n{commandPrefix}lvlup \"character name\"\n{commandPrefix}lvl \"character name\"\n{commandPrefix}lv \"character name\"```")
                                    await levelUpEmbedmsg.clear_reactions()
                                    self.bot.get_command('levelup').reset_cooldown(ctx)
                                    return
                            await levelUpEmbedmsg.clear_reactions()
                            levelUpEmbed.clear_fields()
                            choiceLevelClass = multiclassLevelString.split('\n')[alphaEmojis.index(tReaction.emoji)]

                            for s in subclasses:
                                if s['Name'] in choiceLevelClass:
                                    lvlClass = s['Name']
                                    s['Level'] += 1
                                    if 'Wizard' in s['Name']:
                                        fsLvl = (s['Level'] - 1) // 2
                                        if fsLvl > 8:
                                            fsLvl = 8
                                        freeSpells[fsLvl] += 2
                                    break

                            charClass = charClass.replace(f"{lvlClass} {subclasses[alphaEmojis.index(tReaction.emoji)]['Level'] - 1}", f"{lvlClass} {subclasses[alphaEmojis.index(tReaction.emoji)]['Level']}")
                            levelUpEmbed.description = f"{infoRecords['Race']}: {charClass}\n**STR**:{charStats['STR']} **DEX**:{charStats['DEX']} **CON**:{charStats['CON']} **INT**:{charStats['INT']} **WIS**:{charStats['WIS']} **CHA**:{charStats['CHA']}"

                # Choosing a subclass
                subclassCheckClass = subclasses[[s['Name'] for s in subclasses].index(lvlClass)]

                for s in classRecords:
                    if s['Name'] == subclassCheckClass['Name'] and int(s['Subclass Level']) == subclassCheckClass['Level']:
                        subclassesList = s['Subclasses'].split(', ')
                        subclassChoice, levelUpEmbedmsg = await characterCog.chooseSubclass(ctx, subclassesList, s['Name'], levelUpEmbed, levelUpEmbedmsg) 
                        if not subclassChoice:
                            return
                        
                        if '/' not in charClass:
                            levelUpEmbed.description = levelUpEmbed.description.replace(s['Name'], f"{s['Name']} ({subclassChoice})") 
                            charClass = charClass.replace(s['Name'], f"{s['Name']} ({subclassChoice})" )
                        else:
                            levelUpEmbed.description = levelUpEmbed.description.replace(f"{s['Name']} {subclassCheckClass['Level']}", f"{s['Name']} {subclassCheckClass['Level']} ({subclassChoice})" ) 
                            charClass = charClass.replace(f"{s['Name']} {subclassCheckClass['Level']}", f"{s['Name']} {subclassCheckClass['Level']} ({subclassChoice})" )

                        for sub in subclasses:
                            if sub['Name'] == subclassCheckClass['Name']:
                                sub['Subclass'] = subclassChoice
                
                # Feat 
                featLevels = []
                for c in subclasses:
                    if (int(c['Level']) in (4,8,12,16,19) or ('Fighter' in c['Name'] and int(c['Level']) in (6,14)) or ('Rogue' in c['Name'] and int(c['Level']) == 10)) and lvlClass in c['Name']:
                        featLevels.append(int(c['Level']))

                charFeatsGained = ""
                charFeatsGainedStr = ""
                if featLevels != list():
                    featsChosen, statsFeats, charEmbedmsg = await characterCog.chooseFeat(ctx, infoRecords['Race'], charClass, subclasses, featLevels, levelUpEmbed, levelUpEmbedmsg, infoRecords, charFeats)
                    if not featsChosen and not statsFeats and not charEmbedmsg:
                        return

                    charStats = statsFeats 
                    
                    if featsChosen != list():
                        charFeatsGained = featsChosen

                if charFeatsGained != "":
                    charFeatsGainedStr = f"Feats Gained: **{charFeatsGained}**"

                data = {
                      'Class': charClass,
                      'Level': int(newCharLevel),
                      'CP': totalCP,
                      'STR': int(charStats['STR']),
                      'DEX': int(charStats['DEX']),
                      'CON': int(charStats['CON']),
                      'INT': int(charStats['INT']),
                      'WIS': int(charStats['WIS']),
                      'CHA': int(charStats['CHA']),
                }

                if 'Free Spells' in infoRecords:
                    if freeSpells != ([0] * 9):
                        data['Free Spells'] = freeSpells

                if charFeatsGained != "":
                    if infoRecords['Feats'] == 'None':
                        data['Feats'] = charFeatsGained
                        infoRecords['Feats'] = charFeatsGained
                    elif infoRecords['Feats'] != None:
                        data['Feats'] = charFeats + ", " + charFeatsGained
                        infoRecords['Feats'] = charFeats + ", " + charFeatsGained

                statsCollection = db.stats
                statsRecord  = statsCollection.find_one({'Life': 1})
                
                if charFeatsGained != "":
                    feat_split = charFeatsGained.split(", ")
                    for feat_key in feat_split:
                        if not feat_key in statsRecord['Feats']:
                            statsRecord['Feats'][feat_key] = 1
                        else:
                            statsRecord['Feats'][feat_key] += 1

                            
                subclassCheckClass['Name'] = subclassCheckClass['Name'].split(' (')[0]
                if subclassCheckClass['Subclass'] != "" :
                    if subclassCheckClass['Subclass']  in statsRecord['Class'][subclassCheckClass['Name']]:
                        statsRecord['Class'][subclassCheckClass['Name']][subclassCheckClass['Subclass']] += 1
                    else:
                        statsRecord['Class'][subclassCheckClass['Name']][subclassCheckClass['Subclass']] = 1
                else:
                    if subclassCheckClass['Name'] in statsRecord['Class']:
                        statsRecord['Class'][subclassCheckClass['Name']]['Count'] += 1
                    else:
                        statsRecord['Class'][subclassCheckClass['Name']] = {'Count': 1}

                if 'Max Stats' not in infoRecords:
                    infoRecords['Max Stats'] = {'STR':20, 'DEX':20, 'CON':20, 'INT':20, 'WIS':20, 'CHA':20}
                
                data['Max Stats'] = infoRecords['Max Stats']

                #Special stat bonuses (Barbarian cap / giant soul sorc)
                specialCollection = db.special
                specialRecords = list(specialCollection.find())
                specialStatStr = ""
                for s in specialRecords:
                    if 'Bonus Level' in s:
                        for c in subclasses:
                            if s['Bonus Level'] == c['Level'] and s['Name'] in f"{c['Name']} ({c['Subclass']})":
                                if 'MAX' in s['Stat Bonuses']:
                                    statSplit = s['Stat Bonuses'].split('MAX ')[1].split(', ')
                                    for stat in statSplit:
                                        maxSplit = stat.split(' +')
                                        data[maxSplit[0]] += int(maxSplit[1])
                                        charStats[maxSplit[0]] += int(maxSplit[1])
                                        data['Max Stats'][maxSplit[0]] += int(maxSplit[1]) 

                                    specialStatStr = f"Level {s['Bonus Level']} {c['Name']} stat bonus unlocked! {s['Stat Bonuses']}"


                maxStatStr = ""
                for sk in data['Max Stats'].keys():
                    if charStats[sk] > data['Max Stats'][sk]:
                        data[sk] = charStats[sk] = data['Max Stats'][sk]
                        if charFeatsGained != "":
                            maxStatStr += f"\n{infoRecords['Name']}'s {sk} will not increase because their maximum is {data['Max Stats'][sk]}."
                infoRecords["Class"] = data["Class"]
                infoRecords['CON'] = charStats['CON']
                charHP = await characterCog.calcHP(ctx, subclasses, infoRecords, int(newCharLevel))
                data['HP'] = charHP
                tierNum += int(newCharLevel in [5, 11, 17, 20])
                levelUpEmbed.title = f'{charName} has leveled up to {newCharLevel}!\nCurrent CP: {totalCP}/{cp_bound_array[tierNum-1][1]} CP'
                levelUpEmbed.description = f"{infoRecords['Race']} {charClass}\n**STR**: {charStats['STR']} **DEX**: {charStats['DEX']} **CON**: {charStats['CON']} **INT**: {charStats['INT']} **WIS**: {charStats['WIS']} **CHA**: {charStats['CHA']}" + f"\n{charFeatsGainedStr}{maxStatStr}\n{specialStatStr}"
                if charClassChoice != "":
                    levelUpEmbed.description += f"{charName} has multiclassed into **{charClassChoice}!**"
                levelUpEmbed.set_footer(text= levelUpEmbed.Empty)
                levelUpEmbed.clear_fields()

                def charCreateCheck(r, u):
                    sameMessage = False
                    if levelUpEmbedmsg.id == r.message.id:
                        sameMessage = True
                    return sameMessage and ((str(r.emoji) == '✅') or (str(r.emoji) == '❌')) and u == author


                if not levelUpEmbedmsg:
                   levelUpEmbedmsg = await channel.send(embed=levelUpEmbed, content="**Double-check** your character information.\nIf this is correct, please react with one of the following:\n✅ to finish creating your character.\n❌ to cancel. ")
                else:
                    await levelUpEmbedmsg.edit(embed=levelUpEmbed, content="**Double-check** your character information.\nIf this is correct, please react with one of the following:\n✅ to finish creating your character.\n❌ to cancel. ")

                await levelUpEmbedmsg.add_reaction('✅')
                await levelUpEmbedmsg.add_reaction('❌')
                try:
                    tReaction, tUser = await self.bot.wait_for("reaction_add", check=charCreateCheck , timeout=60)
                except asyncio.TimeoutError:
                    await levelUpEmbedmsg.delete()
                    await channel.send(f'Level up cancelled. Try again using the same command or one of its shorthand forms:\n```yaml\n{commandPrefix}levelup "character name"\n{commandPrefix}lvlup "character name"\n{commandPrefix}lvl "character name"\n{commandPrefix}lv "character name"```')
                    self.bot.get_command('levelup').reset_cooldown(ctx)
                    return
                else:
                    await levelUpEmbedmsg.clear_reactions()
                    if tReaction.emoji == '❌':
                        await levelUpEmbedmsg.edit(embed=None, content=f"Try again using the same command or one of its shorthand forms:\n```yaml\n{commandPrefix}levelup \"character name\"\n{commandPrefix}lvlup \"character name\"\n{commandPrefix}lvl \"character name\"\n{commandPrefix}lv \"character name\"```")
                        await levelUpEmbedmsg.clear_reactions()
                        self.bot.get_command('levelup').reset_cooldown(ctx)
                        return

                try:
                    playersCollection = db.players
                    playersCollection.update_one({'_id': charID}, {"$set": data})
                    statsCollection.update_one({'Life':1}, {"$set": statsRecord}, upsert=True)
                except Exception as e:
                    print ('MONGO ERROR: ' + str(e))
                    charEmbedmsg = await channel.send(embed=None, content="Uh oh, looks like something went wrong. Please try creating your character again.")
                else:
                    print("Success")

                roleName = await self.levelCheck(ctx, newCharLevel, charName)
                levelUpEmbed.clear_fields()
                await levelUpEmbedmsg.edit(content=f":arrow_up:   __**L E V E L   U P!**__\n\n:warning:   **Don't forget to spend your TP!** Use the following command to spend your TP:\n```yaml\n$tp buy \"{charName}\" \"magic item\"```", embed=levelUpEmbed)

                if roleName != "":
                    levelUpEmbed.title = f":tada: {roleName} role acquired! :tada:\n" + levelUpEmbed.title
                    await levelUpEmbedmsg.edit(embed=levelUpEmbed)
                    await levelUpEmbedmsg.add_reaction('🎉')
                    await levelUpEmbedmsg.add_reaction('🎊')
                    await levelUpEmbedmsg.add_reaction('🥳')
                    await levelUpEmbedmsg.add_reaction('🍾')
                    await levelUpEmbedmsg.add_reaction('🥂')

        self.bot.get_command('levelup').reset_cooldown(ctx)
    async def levelCheck(self, ctx, level, charName):
        author = ctx.author
        roles = [r.name for r in author.roles]
        guild = ctx.guild
        roleName = ""
        if not any([(x in roles) for x in ['Junior Friend', 'Journeyfriend', 'Elite Friend', 'True Friend', 'Ascended Friend']]) and 'D&D Friend' in roles and level > 1:
            roleName = 'Junior Friend' 
            levelRole = get(guild.roles, name = roleName)
            await author.add_roles(levelRole, reason=f"***{author}***'s character ***{charName}*** is the first character who has reached level 2!")
        if 'Journeyfriend' not in roles and 'Junior Friend' in roles and level > 4:
            roleName = 'Journeyfriend' 
            roleRemoveStr = 'Junior Friend'
            levelRole = get(guild.roles, name = roleName)
            roleRemove = get(guild.roles, name = roleRemoveStr)
            await author.add_roles(levelRole, reason=f"***{author}***'s character ***{charName}*** is the first character who has reached level 5!")
            await author.remove_roles(roleRemove)
        if 'Elite Friend' not in roles and 'Journeyfriend' in roles and level > 10:
            roleName = 'Elite Friend'
            roleRemoveStr = 'Journeyfriend'
            levelRole = get(guild.roles, name = roleName)
            roleRemove = get(guild.roles, name = roleRemoveStr)
            await author.add_roles(levelRole, reason=f"***{author}***'s character ***{charName}*** is the first character who has reached level 11!")
            await author.remove_roles(roleRemove)
        if 'True Friend' not in roles and 'Elite Friend' in roles and level > 16:
            roleName = 'True Friend'
            roleRemoveStr = 'Elite Friend'
            levelRole = get(guild.roles, name = roleName)
            roleRemove = get(guild.roles, name = roleRemoveStr)
            await author.add_roles(levelRole, reason=f"***{author}***'s character ***{charName}*** is the first character who has reached level 17!")
            await author.remove_roles(roleRemove)
        if 'Ascended Friend' not in roles and 'True Friend' in roles and level > 19:
            roleName = 'Ascended Friend'
            roleRemoveStr = 'True Friend'
            levelRole = get(guild.roles, name = roleName)
            roleRemove = get(guild.roles, name = roleRemoveStr)
            await author.add_roles(levelRole, reason=f"***{author}***'s character ***{charName}*** is the first character who has reached level 20!")
            await author.remove_roles(roleRemove)
        return roleName
    @commands.cooldown(1, 5, type=commands.BucketType.member)
    @is_log_channel()
    @commands.command(aliases=['att'])
    async def attune(self,ctx, char, m):
        channel = ctx.channel
        author = ctx.author
        guild = ctx.guild
        charEmbed = discord.Embed ()
        charRecords, charEmbedmsg = await checkForChar(ctx, char, charEmbed)

        if charRecords:
            if 'Death' in charRecords:
                await channel.send(f"You cannot attune to items while your character is dead! Use the following command to decide their fate:\n```yaml\n$death \"{charRecords['Name']}\"```")
                return

            # Check number of items character can attune to. Artificer has exceptions.
            attuneLength = 3
            
            for multi in charRecords['Class'].split("/"):
                multi = multi.strip()
                multi_split = multi.split(" ")
                if multi_split[0] == 'Artificer':
                    class_level = charRecords["Level"]
                    if len(multi_split)>2:
                        try:
                            class_level = int(multi_split[1])
                        except Exception as e:
                            pass
                    if class_level >= 18:
                        attuneLength = 6
                    elif class_level >= 14:
                        attuneLength = 5
                    elif class_level >= 10:
                        attuneLength = 4
            if "Attuned" not in charRecords:
                attuned = []
            else:
                attuned = charRecords['Attuned'].split(', ')


            charID = charRecords['_id']
            charRecordMagicItems = charRecords['Magic Items'].split(', ')
            if len(attuned) >= attuneLength:
                await channel.send(f"The maximum number of magic items you can attune to is {attuneLength}! You cannot attune to any more items!")
                return

            def apiEmbedCheck(r, u):
                sameMessage = False
                if charEmbedmsg.id == r.message.id:
                    sameMessage = True
                return sameMessage and ((r.emoji in numberEmojis[:min(len(mList), 9)]) or (str(r.emoji) == '❌')) and u == author

            mList = []
            mString = ""
            numI = 0

            # Check if query is in character's Magic Item List. Limit is 8 to show if there are multiple matches.
            for k in charRecordMagicItems:
                if m.lower() in k.lower():
                    if k not in [a.split(' [')[0] for a in attuned]:
                        mList.append(k)
                        mString += f"{numberEmojis[numI]} {k} \n"
                        numI += 1
                if numI > 8:
                    break

            # IF multiple matches, check which one the player meant.
            if (len(mList) > 1):
                charEmbed.add_field(name=f"There seems to be multiple results for **`{m}`**, please choose the correct one.\nIf the result you are looking for is not here, please cancel the command with ❌ and be more specific.", value=mString, inline=False)
                if not charEmbedmsg:
                    charEmbedmsg = await channel.send(embed=charEmbed)
                else:
                    await charEmbedmsg.edit(embed=charEmbed)

                await charEmbedmsg.add_reaction('❌')

                try:
                    tReaction, tUser = await self.bot.wait_for("reaction_add", check=apiEmbedCheck, timeout=60)
                except asyncio.TimeoutError:
                    await charEmbedmsg.delete()
                    await channel.send('Timed out! Try using the command again.')
                    ctx.command.reset_cooldown(ctx)
                    return None, charEmbed, charEmbedmsg
                else:
                    if tReaction.emoji == '❌':
                        await charEmbedmsg.edit(embed=None, content=f"Command cancelled. Try using the command again.")
                        await charEmbedmsg.clear_reactions()
                        ctx.command.reset_cooldown(ctx)
                        return None,charEmbed, charEmbedmsg
                charEmbed.clear_fields()
                await charEmbedmsg.clear_reactions()
                m = mList[int(tReaction.emoji[0]) - 1]

            elif len(mList) == 1:
                m = mList[0]
            else:
                await channel.send(f"`{m}` isn't in {charRecords['Name']}'s inventory. Please try the command again.")
                return

            # Check if magic item's actually exist, and grab properties. (See if they're attuneable)
            mRecord, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg,'mit', m, True)
            if not mRecord:
                mRecord, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg,'rit', m, True)
                if not mRecord:
                    await channel.send(f"`{m}`belongs to a tier which you do not have access to or it doesn't exist! Check to see if it's on the Magic or Reward Item Table, what tier it is, and your spelling.\n")
                    return
                elif mRecord['Name'].lower() not in [x.lower() for x in charRecordMagicItems]:
                    await channel.send(f"You don't have the **{mRecord['Name']}** item in your inventory to attune to.")
                    return
            elif mRecord['Name'].lower() not in [x.lower() for x in charRecordMagicItems]:
                    await channel.send(f"You don't have the **{mRecord['Name']}** item in your inventory to attune to.")
                    return

            # Check if they are already attuned to the item.
            if mRecord['Name'] == 'Hammer of Thunderbolts':
                if 'Max Stats' not in charRecords:
                    charRecords['Max Stats'] = {'STR':20, 'DEX':20, 'CON':20, 'INT':20, 'WIS':20, 'CHA':20}
                # statSplit = MAX STAT +X
                statSplit = mRecord['Stat Bonuses'].split(' +')
                maxSplit = statSplit[0].split(' ')

                #Increase stats from Hammer and add to max stats. 
                if "MAX" in statSplit[0]:
                    charRecords['Max Stats'][maxSplit[1]] += int(statSplit[1]) 

                if 'Belt of' not in charRecords['Magic Items'] and 'Frost Giant Strength' not in charRecords['Magic Items'] and 'Gauntlets of Ogre Power' not in charRecords['Magic Items']:
                    await channel.send(f"`Hammer of Thunderbolts` requires you to have a `Belt of Giant Strength (any variety)` and `Gauntlets of Ogre Power` in your inventory in order to attune to it.")
                    return 

            if mRecord['Name'] in [a.split('[')[0].strip() for a in attuned]:
                await channel.send(f"You are already attuned to **{mRecord['Name']}**!")
                return
            elif 'Attunement' in mRecord:
                if "Predecessor" in mRecord and 'Stat Bonuses' in mRecord["Predecessor"]:
                    attuned.append(f"{mRecord['Name']} [{mRecord['Predecessor']['Stat Bonuses'][charRecords['Predecessor'][mRecord['Name']]['Stage']]}]")
                elif 'Stat Bonuses' in mRecord:
                    attuned.append(f"{mRecord['Name']} [{mRecord['Stat Bonuses']}]")
                else:
                    attuned.append(mRecord['Name'])
            else:
                await channel.send(f"`{m}` does not require attunement so there is no need to try to attune this item.")
                return
                        
            
            charRecords['Attuned'] = ', '.join(attuned)
            data = charRecords

            try:
                playersCollection = db.players
                playersCollection.update_one({'_id': charID}, {"$set": data})
            except Exception as e:
                print ('MONGO ERROR: ' + str(e))
                charEmbedmsg = await channel.send(embed=None, content="Uh oh, looks like something went wrong. Please try creating your character again.")
            else:
                await channel.send(f"You successfully attuned to **{mRecord['Name']}**!")

    @commands.cooldown(1, 5, type=commands.BucketType.member)
    @is_log_channel()
    @commands.command(aliases=['uatt', 'unatt'])
    async def unattune(self,ctx, char, m):
        channel = ctx.channel
        author = ctx.author
        guild = ctx.guild
        charEmbed = discord.Embed ()
        charRecords, charEmbedmsg = await checkForChar(ctx, char, charEmbed)

        if charRecords:
            if 'Death' in charRecords:
                await channel.send(f"You cannot unattune from items with a dead character. Use the following command to decide their fate:\n```yaml\n$death \"{charRecords['Name']}\"```")
                return

            if "Attuned" not in charRecords:
                await channel.send(f"You have no attuned items to unattune from.")
                return
            else:
                attuned = charRecords['Attuned'].split(', ')

            charID = charRecords['_id']

            def apiEmbedCheck(r, u):
                sameMessage = False
                if charEmbedmsg.id == r.message.id:
                    sameMessage = True
                return sameMessage and ((r.emoji in numberEmojis[:min(len(mList), 9)]) or (str(r.emoji) == '❌')) and u == author

            mList = []
            mString = ""
            numI = 0

            # Filter through attuned items, some attuned items have [STAT +X]; filter out those too and get raw.
            for k in charRecords['Attuned'].split(', '):
                if m.lower() in k.lower().split(' [')[0]:
                    mList.append(k.lower().split(' [')[0])
                    mString += f"{numberEmojis[numI]} {k} \n"
                    numI += 1
                if numI > 8:
                    break

            if (len(mList) > 1):
                charEmbed.add_field(name=f"There seems to be multiple results for `{m}`, please choose the correct one.\nIf the result you are looking for is not here, please cancel the command with ❌ and be more specific.", value=mString, inline=False)
                if not charEmbedmsg:
                    charEmbedmsg = await channel.send(embed=charEmbed)
                else:
                    await charEmbedmsg.edit(embed=charEmbed)

                await charEmbedmsg.add_reaction('❌')

                try:
                    tReaction, tUser = await self.bot.wait_for("reaction_add", check=apiEmbedCheck, timeout=60)
                except asyncio.TimeoutError:
                    await charEmbedmsg.delete()
                    await channel.send('Timed out! Try using the command again.')
                    ctx.command.reset_cooldown(ctx)
                    return None, charEmbed, charEmbedmsg
                else:
                    if tReaction.emoji == '❌':
                        await charEmbedmsg.edit(embed=None, content=f"Command cancelled. Try using the command again.")
                        await charEmbedmsg.clear_reactions()
                        ctx.command.reset_cooldown(ctx)
                        return None,charEmbed, charEmbedmsg
                charEmbed.clear_fields()
                await charEmbedmsg.clear_reactions()
                m = mList[int(tReaction.emoji[0]) - 1]

            elif len(mList) == 1:
                m = mList[0]
            else:
                await channel.send(f'`{m}` doesn\'t exist on the Magic Item Table! Check to see if it is a valid item and check your spelling.')
                return

            mRecord, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg,'mit', m, True)
            if not mRecord:
                mRecord, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg,'rit', m, True)
                if not mRecord:
                    await channel.send(f"`{m}` belongs to a tier which you do not have access to or it doesn't exist! Check to see if it's on the Magic or Reward Item Table, what tier it is, and your spelling.")
                    return

            if mRecord['Name'] not in [a.split(' [')[0] for a in attuned]:
                await channel.send(f"**{mRecord['Name']}** cannot be unattuned from because it is currently not attuned to you.")
                return
            else:
                if mRecord['Name'] == 'Hammer of Thunderbolts':
                    statSplit = mRecord['Stat Bonuses'].split(' +')
                    maxSplit = statSplit[0].split(' ')
                    if "MAX" in statSplit[0]:
                        charRecords['Max Stats'][maxSplit[1]] -= int(statSplit[1]) 
                
                try:
                    index = list([a.split("[")[0].strip() for a in attuned]).index(mRecord["Name"])
                    attuned.pop(index)
                except Exception as e:
                    pass
                
                charRecords['Attuned'] = ', '.join(attuned)

                try:
                    playersCollection = db.players
                    if attuned != list():
                        playersCollection.update_one({'_id': charID}, {"$set": charRecords})
                    else:
                        playersCollection.update_one({'_id': charID}, {"$unset": {"Attuned":1}})

                except Exception as e:
                    print ('MONGO ERROR: ' + str(e))
                    charEmbedmsg = await channel.send(embed=None, content="Uh oh, looks like something went wrong. Please try creating your character again.")
                else:
                    await channel.send(f"You successfully unattuned from **{mRecord['Name']}**!")
                    

    @commands.command()
    @commands.cooldown(1, 5, type=commands.BucketType.member)
    @stats_special()
    async def stats(self,ctx, month = None, year = None):                
        statsCollection = db.stats
        currentDate = datetime.now().strftime("%b-%y")
        if not year:
            year = currentDate.split("-")[1]
        if month:
            if month.isnumeric() and int(month)>0 and int(month) < 13:
                currentDate = datetime.now().replace(month = int(month)).replace(year = 2000+int(year)).strftime("%b-%y")
                
            else:
                await ctx.channel.send(f"Month needs to be a number between 1 and 12.")
                ctx.command.reset_cooldown(ctx)
                return
                    
        statRecords = statsCollection.find_one({"Date": currentDate})
        statRecordsLife = statsCollection.find_one({"Life": 1})
        guild=ctx.guild
        channel = ctx.channel

        statsEmbed = discord.Embed()
        statsEmbedmsg = None
        statsEmbed.title = f'Stats' 

        statsTotalString = ""
        guildsString = ""
        superTotal = 0
        avgString = ""
        statsString = ""
        charString = ""
        raceString = ""
        bgString = ""
        author = ctx.author

        def statsEmbedCheck(r, u):
            sameMessage = False
            if statsEmbedmsg.id == r.message.id:
                sameMessage = True
            return sameMessage and ((r.emoji in alphaEmojis[:7]) or (str(r.emoji) == '❌')) and u == author

        statsEmbed.description = f"Please choose a category:\n{alphaEmojis[0]}: Monthly Stats\n{alphaEmojis[1]}: Lifetime Main Stats\n{alphaEmojis[2]}: Lifetime Class Stats\n{alphaEmojis[3]}: Lifetime Race Stats\n{alphaEmojis[4]}: Lifetime Background Stats\n{alphaEmojis[5]}: Lifetime Feat Stats\n{alphaEmojis[6]}: Lifetime Magic Items Stats"
        statsEmbedmsg = await ctx.channel.send(embed=statsEmbed)
        for num in range(0,7): await statsEmbedmsg.add_reaction(alphaEmojis[num])
        try:
            tReaction, tUser = await self.bot.wait_for("reaction_add", check=statsEmbedCheck , timeout=60)
        except asyncio.TimeoutError:
            await statsEmbedmsg.delete()
            await channel.send(f'Stats cancelled. Try again using the same command!')
            ctx.command.reset_cooldown(ctx)
            return
        else:
            statsEmbed.description = ""

        # Lets the user choose a category to view stats
        if tReaction.emoji == alphaEmojis[0] or tReaction.emoji == alphaEmojis[1]:
            identity_strings = ["Monthly", "Month"]
            if tReaction.emoji == alphaEmojis[1]:
                identity_strings = ["Server", "Server"]
                statRecords = statRecordsLife
            dmPages = 0
            if statRecords is None:
                statsEmbed.add_field(name="Monthly Quest Stats", value="There have been 0 one-shots played this month. Check back later!", inline=False)
            else:
                # Iterate through each DM and track tiers + total
                if "DM" in statRecords:
                    
                    dmPages = 1
                    dmPageStops = [0]
                    for k,v in statRecords['DM'].items():
                        dmMember = guild.get_member(int(k))
                        if dmMember is None:
                            statsString += f"<@!{k}>" + " - "
                            # continue
                        else:
                            statsString += dmMember.mention + " - "
                        totalGames = 0
                        for i in range (0,6):
                            if f'T{i}' not in v:
                                statsString += f"T{i}: 0 | "
                            else:
                                statsString += f"T{i}: {v[f'T{i}']} | " 
                                totalGames += v[f'T{i}']
                       
                        # Total Number of Games per DM
                        statsString += f"Total: {totalGames}\n"
                        if len(statsString) > (768 * dmPages):
                            dmPageStops.append(len(statsString))
                            dmPages += 1
                    dmPageStops.append(len(statsString))


              
                # Total number of Games for the month
                if "Games" in statRecords:
                    superTotal += statRecords["Games"]

                gq_sum = 0
                if "GQ Total" in statRecords:
                    gq_sum = statRecords["GQ Total"]
                
                # Games By Guild
                if "Guilds" in statRecords:
                    gPages = 1
                    gPageStops = [0]
                    guildGamesString = ""
                    guild_data_0s = ["GQ", "GQM", "GQNM", "GQDM", "DM Sparkles", "Player Sparkles", "Joins"]
                    for gk, gv in statRecords["Guilds"].items():
                        for data_key in guild_data_0s:
                            if not data_key in gv:
                                gv[data_key] = 0
                        
                        guildGamesString += f"• {gk}"    
                        guildGamesString += f": {gv['GQ']}\n"
                        if len(guildGamesString) > (768 * gPages):
                            gPageStops.append(len(guildGamesString))
                            gPages += 1
                    gPageStops.append(len(guildGamesString))

                    if gPages > 1:
                        for p in range(len(gPageStops)-1):
                            statsEmbed.add_field(name=f'Guilds - p. {p+1}', value=guildGamesString[gPageStops[p]:gPageStops[p+1]], inline=False)
                    else:
                        statsEmbed.add_field(name=f'Guild Quests (Total: {gq_sum})', value=guildGamesString, inline=False)
                if "Campaigns" in statRecords:
                    statsEmbed.add_field(name=f'Campaigns', value=f"Sessions: {statRecords['Campaigns']}", inline=False)
                
                if "Life" in statRecords:
                    monthStart = datetime.now().replace(day = 14).replace(month = 1).replace(year = 2021)
                elif month:
                    
                    monthStart = datetime.now().replace(year=2000+int(year), month= int(month), day=1) -  timedelta(days=1)
                else:
                    monthStart = datetime.now().replace(day = 1)
                
                # Stat for average player and average play time
                if 'Players' in statRecords and 'Playtime' in statRecords:
                    avgString += f"Average Number of Players per Game: {(int(statRecords['Players']  / superTotal *100) /100.0)}\n" 
                    avgString += f"Average Game Time: {timeConversion(statRecords['Playtime'] / superTotal)}\n"
                    avgString += f"Average Games Per Day: {(int(superTotal / (max((datetime.now()-monthStart).days, 1))*100) /100.0)}\n"
                    statsEmbed.add_field(name="Averages", value=avgString, inline=False) 

                if statsString:
                    
                    if dmPages > 1:
                        for p in range(len(dmPageStops)-1):
                            if dmPageStops[p+1] > dmPageStops[p]:
                                statsEmbed.add_field(name=f'One-shots by DM - p. {p+1}', value=statsString[dmPageStops[p]:dmPageStops[p+1]], inline=False)
                    else:
                        statsEmbed.add_field(name="One-shots by DM", value=statsString, inline=False)

                # Number of games by total and by tier
                statsTotalString += f"**{identity_strings[0]} Stats**\nTotal One-shots for the {identity_strings[1]}: {superTotal}\n" 
                if superTotal > 0:
                    statsTotalString += f'Guild Quest % (Out of Total Quests): {round((gq_sum / superTotal)* 100,2) }%\n'                   
                for i in range (0,6):
                    if f'T{i}' not in statRecords:
                        statsTotalString += f"Tier {i} One-shots for the {identity_strings[1]}: 0\n"
                    else: 
                        statsTotalString += f"Tier {i} One-shots for the {identity_strings[1]}: {statRecords[f'T{i}']}\n"


                if 'Players' in statRecords and 'Playtime' in statRecords:
                    statsTotalString += f"Total Hours Played: {timeConversion(statRecords['Playtime'])}\n"
                    statsTotalString += f"Total Number of Players: {statRecords['Players']}\n"
                if 'Unique Players' in statRecords and 'Playtime' in statRecords:
                    statsTotalString += f"Number of Unique Players: {len(statRecords['Unique Players'])}\n"
                statsEmbed.description = statsTotalString
          
        # Below are lifetime stats which consists of character data
        # Lifetime Class Stats
        elif tReaction.emoji == alphaEmojis[2]: 
            cPages = 1
            cPageStops = [0]
            charString = ""
            srClass = collections.OrderedDict(sorted(statRecordsLife['Class'].items()))
            for k, v in srClass.items():
                charString += f"**{k}**: {v['Count']}\n"
                for vk, vv in collections.OrderedDict(sorted(v.items())).items():
                    if vk != 'Count':
                        charString += f"• {vk}: {vv}\n"
                charString += f"━━━━━\n"
                if len(charString) > (768 * cPages):
                    cPageStops.append(len(charString))
                    cPages += 1
            cPageStops.append(len(charString))
            if not charString:
                charString = "No stats yet."
            if cPages > 1:
                for p in range(len(cPageStops)-1):
                    statsEmbed.add_field(name=f"Character Class Stats (Lifetime) p. {p+1}", value=charString[cPageStops[p]:cPageStops[p+1]], inline=False)  
            else:
                statsEmbed.add_field(name="Character Class Stats (Lifetime)", value=charString, inline=False)  

        # Lifetime race stats
        elif tReaction.emoji == alphaEmojis[3]:
            rPages = 1
            rPageStops = [0]
            raceString = ""
            srRace = collections.OrderedDict(sorted(statRecordsLife['Race'].items()))
            for k, v in srRace.items():
                raceString += f"{k}: {v}\n"
                if len(raceString) > (768 * rPages):
                    rPageStops.append(len(raceString))
                    rPages += 1

            rPageStops.append(len(raceString))

            if not raceString:
                raceString = "No stats yet."
            if rPages > 1:
                for p in range(len(rPageStops)-1):
                    statsEmbed.add_field(name=f"Character Race Stats (Lifetime) p. {p+1}", value=raceString[rPageStops[p]:rPageStops[p+1]], inline=False)  
            else:
                statsEmbed.add_field(name="Character Race Stats (Lifetime)", value=raceString, inline=True)  

        # Lifetime background Stats
        elif tReaction.emoji == alphaEmojis[4]:
            bPages = 1
            bPageStops = [0]
            bgString = ""
            srBg = collections.OrderedDict(sorted(statRecordsLife['Background'].items()))

            for k, v in srBg.items():
                bgString += f"{k}: {v}\n"
                if len(bgString) > (768 * bPages):
                    bPageStops.append(len(bgString))
                    bPages += 1

            bPageStops.append(len(bgString))
            if not bgString:
                bgString = "No stats yet."
            if bPages > 1:
                for p in range(len(bPageStops)-1):
                    statsEmbed.add_field(name=f"Character Background Stats (Lifetime) p. {p+1}", value=bgString[bPageStops[p]:bPageStops[p+1]], inline=False)  
            else:
                statsEmbed.add_field(name="Character Background Stats (Lifetime)", value=bgString, inline=False)  
        # Lifetime Feats Stats
        elif tReaction.emoji == alphaEmojis[5]:
            bPages = 1
            bPageStops = [0]
            bgString = ""
            srBg = collections.OrderedDict(sorted(statRecordsLife['Feats'].items()))

            for k, v in srBg.items():
                bgString += f"{k}: {v}\n"
                if len(bgString) > (768 * bPages):
                    bPageStops.append(len(bgString))
                    bPages += 1

            bPageStops.append(len(bgString))

            if not bgString:
                bgString = "No stats yet."
            if bPages > 1:
                for p in range(len(bPageStops)-1):
                    statsEmbed.add_field(name=f"Character Feats Stats (Lifetime) p. {p+1}", value=bgString[bPageStops[p]:bPageStops[p+1]], inline=False)  
            else:
                statsEmbed.add_field(name="Character Feats Stats (Lifetime)", value=bgString, inline=False)  
        # Lifetime Magic Items Stats
        elif tReaction.emoji == alphaEmojis[6]:
            bPages = 1
            bPageStops = [0]
            bgString = ""
            srBg = collections.OrderedDict(sorted(statRecordsLife['Magic Items'].items()))

            for k, v in srBg.items():
                lastEntry = False
                bgString += f"{k}: {v}\n"
                if len(bgString) > (768 * bPages):
                    bPageStops.append(len(bgString))
                    bPages += 1
                    lastEntry = True
            if(not lastEntry):
                bPageStops.append(len(bgString))

            if not bgString:
                bgString = "No stats yet."
            if bPages > 1:
                for p in range(min(len(bPageStops)-1, 5)):
                    statsEmbed.add_field(name=f"Character Magic Items Stats (Lifetime) p. {p+1}", value=bgString[bPageStops[p]:bPageStops[p+1]], inline=False)  
            else:
                statsEmbed.add_field(name="Character Magic Items Stats (Lifetime)", value=bgString, inline=False)  
            await statsEmbedmsg.clear_reactions()
            await statsEmbedmsg.edit(embed=statsEmbed)
            def userCheck(r,u):
                sameMessage = False
                if statsEmbedmsg.id == r.message.id:
                    sameMessage = True
                return sameMessage and u == ctx.author and (r.emoji == left or r.emoji == right)
            subpages= 5
            page = 0
            while bPages >= subpages:
                await statsEmbedmsg.add_reaction(left) 
                await statsEmbedmsg.add_reaction(right)
                try:
                    hReact, hUser = await self.bot.wait_for("reaction_add", check=userCheck, timeout=30.0)
                except asyncio.TimeoutError:
                    await statsEmbedmsg.edit(content=f"Your user menu has timed out! I'll leave this page open for you. If you need to cycle through the menu again then use the same command!")
                    await statsEmbedmsg.clear_reactions()
                    await statsEmbedmsg.add_reaction('💤')
                    return
                else:
                    if hReact.emoji == left:
                        page -= 1
                        if page < 0:
                            page = (len(bPageStops) -1) // subpages
                    if hReact.emoji == right:
                        page += 1
                        if page > (len(bPageStops) -1 ) // subpages:
                            page = 0
                    statsEmbed.clear_fields()
                    for p in range(subpages*page, subpages*page+min(len(bPageStops)-1-page*subpages, subpages)):
                        statsEmbed.add_field(name=f"Character Magic Items Stats (Lifetime) p. {p+1}", value=bgString[bPageStops[p]:bPageStops[p+1]], inline=False)  
            
                    statsEmbed.set_footer(text=f"Page {subpages*page+1} of {bPages}")
                    await statsEmbedmsg.edit(embed=statsEmbed) 
                    await statsEmbedmsg.clear_reactions()
            return
        await statsEmbedmsg.clear_reactions()
        await statsEmbedmsg.edit(embed=statsEmbed)
        
        
        
    @commands.command()
    @commands.cooldown(1, 5, type=commands.BucketType.member)
    @stats_special()
    async def fanatic(self,ctx, month = None, year = None):                
        statsCollection = db.stats
        currentDate = datetime.now().strftime("%b-%y")
        if not year:
            year = currentDate.split("-")[1]
        if month:
            if month.isnumeric() and int(month)>0 and int(month) < 13:
                currentDate = datetime.now().replace(month = int(month)).replace(year = 2000+int(year)).strftime("%b-%y")
                
            else:
                await ctx.channel.send(f"Month needs to be a number between 1 and 12.")
                ctx.command.reset_cooldown(ctx)
                return
        statRecords = statsCollection.find_one({"Date": currentDate})
        guild=ctx.guild
        channel = ctx.channel

        statsEmbed = discord.Embed()
        statsEmbedmsg = None
        statsEmbed.title = f'Fanatic Competition' 

        friendString = ""
        guildString = ""
        author = ctx.author

        
        if statRecords is None or "DM" not in statRecords:
            statsEmbed.add_field(name="Fanatic Stats", value="There have been 0 valid one-shots played this month. Check back later!", inline=False)
        else:
            friend_list = []
            guild_list = []
            
            dm_dictionary = statRecords['DM']
            # Iterate through each DM and track tiers + total
            for k,v in dm_dictionary.items():
                dmMember = guild.get_member(int(k))
                if dmMember is None:
                    continue
                if "Friend" in v:
                    friend_list.append({"Member": dmMember, "Count": v["Friend"]})
                if "Guild Fanatic" in v:
                    guild_list.append({"Member": dmMember, "Count": v["Guild Fanatic"]})
            friend_list.sort(key = lambda x: -x["Count"])
            
            guild_list.sort(key = lambda x: -x["Count"])
            
            for f in friend_list:
                friendString += f"{f['Member'].mention}: {f['Count']} Points\n"
            for g in guild_list:
                guildString += f"{g['Member'].mention}: {g['Count']} Points\n"
            if friendString:
                statsEmbed.add_field(name=f"Friend Fanatic", value=friendString, inline=True) 
            if guildString: 
                statsEmbed.add_field(name=f"Guild Fanatic", value=guildString, inline=True)  
                
        await ctx.channel.send(embed=statsEmbed)

    async def calcHP (self, ctx, classes, charDict, lvl):
        # classes = sorted(classes, key = lambda i: i['Hit Die Max'],reverse=True) 
        totalHP = 0
        totalHP += classes[0]['Hit Die Max']
        currentLevel = 1
        charDict = charDict.copy()
        for c in classes:
            classLevel = int(c['Level'])
            while currentLevel < classLevel:
                totalHP += c['Hit Die Average']
                currentLevel += 1
            currentLevel = 0

        totalHP += ((int(charDict['CON']) - 10) // 2 ) * lvl
        
        specialCollection = db.special
        specialRecords = list(specialCollection.find())

        for s in specialRecords:
            if s['Type'] == "Race" or s['Type'] == "Feats" or s['Type'] == "Magic Items":
                
                if s['Name'] in charDict[s['Type']]:
                    if 'HP' in s:
                        if 'Half Level' in s:
                            totalHP += s['HP'] * floor(lvl/2)
                        else:
                            totalHP += s['HP'] * lvl
            elif s['Type'] == "Class":
                for multi in charDict['Class'].split("/"):
                    multi = multi.strip()
                    multi_split = list(multi.split(" "))
                    class_level = lvl
                    class_name = multi_split[0]
                    if len(multi_split) > 2:
                        try:
                            class_level=int(multi_split.pop(1))
                        except Exception as e:
                            continue
                    class_name = " ".join(multi_split)
                        
                        
                    if class_name == s["Name"]:
                        
                        if 'HP' in s:
                            if 'Half Level' in s:
                                totalHP += s['HP'] * floor(class_level/2)
                            else:
                                totalHP += s['HP'] * class_level
                            
                             

        return totalHP

    async def pointBuy(self,ctx, statsArray, rRecord, charEmbed, charEmbedmsg):
        author = ctx.author
        channel = ctx.channel
        def anyCharEmbedcheck(r, u):
            sameMessage = False
            if charEmbedmsg.id == r.message.id:
                sameMessage = True
            if (r.emoji in uniqueReacts or r.emoji == '❌') and u == author:
                anyList[charEmbedmsg.id].add(r.emoji)
            return sameMessage and ((len(anyList[charEmbedmsg.id]) == anyCheck) or str(r.emoji) == '❌') and u == author

        def slashCharEmbedcheck(r, u):
            sameMessage = False
            if charEmbedmsg.id == r.message.id:
                sameMessage = True
            return sameMessage and ((r.emoji in numberEmojis[:len(statSplit)]) or (str(r.emoji) == '❌')) and u == author

        if rRecord:
            statsBonus = rRecord['Modifiers'].replace(" ", "").split(',')
            uniqueArray = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
            allStatsArray = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
            
            for s in statsBonus:
                if '/' in s:
                    statSplit = s[:len(s)-2].replace(" ", "").split('/')
                    statSplitString = ""
                    for num in range(len(statSplit)):
                        statSplitString += f'{numberEmojis[num]}: {statSplit[num]}\n'
                    try:
                        charEmbed.add_field(name=f"The {rRecord['Name']} race lets you choose between {s}. React [1-{len(statSplit)}] below with the stat(s) you would like to choose.", value=statSplitString, inline=False)
                        if charEmbedmsg:
                            await charEmbedmsg.edit(embed=charEmbed)
                        else: 
                            charEmbedmsg = await channel.send(embed=charEmbed)
                        for num in range(0,len(statSplit)): await charEmbedmsg.add_reaction(numberEmojis[num])
                        await charEmbedmsg.add_reaction('❌')
                        tReaction, tUser = await self.bot.wait_for("reaction_add", check=slashCharEmbedcheck, timeout=60)
                    except asyncio.TimeoutError:
                        await charEmbedmsg.delete()
                        await channel.send(f'Character creation timed out! Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                        self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                        return None, None
                    else:
                        if tReaction.emoji == '❌':
                            await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}char {ctx.invoked_with}```")
                            await charEmbedmsg.clear_reactions()
                            self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                            return None, None
                    await charEmbedmsg.clear_reactions()
                    s = statSplit[int(tReaction.emoji[0]) - 1] + s[-2:]

                if 'STR' in s:
                    statsArray[0] += int(s[len(s)-1]) if s[len(s)-2] == "+" else int("-" + s[len(s)-1])
                    uniqueArray.remove('STR')
                elif 'DEX' in s:
                    statsArray[1] += int(s[len(s)-1]) if s[len(s)-2] == "+" else int("-" + s[len(s)-1])
                    uniqueArray.remove('DEX')
                elif 'CON' in s:
                    statsArray[2] += int(s[len(s)-1]) if s[len(s)-2] == "+" else int("-" + s[len(s)-1])
                    uniqueArray.remove('CON')
                elif 'INT' in s:
                    statsArray[3] += int(s[len(s)-1]) if s[len(s)-2] == "+" else int("-" + s[len(s)-1])
                    uniqueArray.remove('INT')
                elif 'WIS' in s:
                    statsArray[4] += int(s[len(s)-1]) if s[len(s)-2] == "+" else int("-" + s[len(s)-1])
                    uniqueArray.remove('WIS')
                elif 'CHA' in s:
                    statsArray[5] += int(s[len(s)-1]) if s[len(s)-2] == "+" else int("-" + s[len(s)-1])
                    uniqueArray.remove('CHA')

                elif 'AOU' in s or 'ANY' in s:
                    try:
                        anyList = dict()
                        anyCheck = [int(charL) for charL in s if charL.isnumeric()][0] #int(s[len(s)-1])
                        anyAmount = int(s[len(s)-1])
                        anyList = {charEmbedmsg.id:set()}
                        uniqueStatStr = ""
                        uniqueReacts = []

                        if 'ANY' in s:
                            uniqueArray = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']

                        for u in range(0,len(uniqueArray)):
                            uniqueStatStr += f'{numberEmojis[u]}: {uniqueArray[u]}\n'
                            uniqueReacts.append(numberEmojis[u])

                        charEmbed.add_field(name=f"The {rRecord['Name']} race lets you choose {anyCheck} extra stats to increase by {anyAmount}. React below with the stat(s) you would like to choose.", value=uniqueStatStr, inline=False)
                        if charEmbedmsg:
                            await charEmbedmsg.edit(embed=charEmbed)
                        else: 
                            charEmbedmsg = await channel.send(embed=charEmbed)
                        for num in range(0,len(uniqueArray)): await charEmbedmsg.add_reaction(numberEmojis[num])
                        await charEmbedmsg.add_reaction('❌')
                        tReaction, tUser = await self.bot.wait_for("reaction_add", check=anyCharEmbedcheck, timeout=60)
                        
                    except asyncio.TimeoutError:
                        await charEmbedmsg.delete()
                        await channel.send(f'Point buy timed out! Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                        self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                        return None, None

                    else:
                        if tReaction.emoji == '❌':
                            await charEmbedmsg.edit(embed=None, content=f'Point buy cancelled out! Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                            await charEmbedmsg.clear_reactions()
                            self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                            return None, None 
                        

                    charEmbed.clear_fields()
                    await charEmbedmsg.clear_reactions()
                    if 'AOU' in s:
                        for s in anyList[charEmbedmsg.id]:
                            statsArray[allStatsArray.index(uniqueArray.pop(int(s[0]) - 1))] += anyAmount
                    else:

                        for s in anyList[charEmbedmsg.id]:
                            statsArray[(int(s[0]) - 1)] += anyAmount
            return statsArray, charEmbedmsg

    async def chooseSubclass(self, ctx, subclassesList, charClass, charEmbed, charEmbedmsg):
        author = ctx.author
        channel = ctx.channel
        def classEmbedCheck(r, u):
            sameMessage = False
            if charEmbedmsg.id == r.message.id:
                sameMessage = True
            return sameMessage and ((r.emoji in alphaEmojis[:alphaIndex]) or (str(r.emoji) == '❌')) and u == author

        try:
            subclassString = ""
            for num in range(len(subclassesList)):
                subclassString += f'{alphaEmojis[num]}: {subclassesList[num]}\n'

            charEmbed.clear_fields()
            charEmbed.add_field(name=f"The {charClass} class allows you to pick a subclass at this level. React to the choices below to select your subclass.", value=subclassString, inline=False)
            alphaIndex = len(subclassesList)
            if charEmbedmsg:
                await charEmbedmsg.edit(embed=charEmbed)
            else: 
                charEmbedmsg = await channel.send(embed=charEmbed)
            await charEmbedmsg.add_reaction('❌')
            tReaction, tUser = await self.bot.wait_for("reaction_add", check=classEmbedCheck, timeout=60)
        except asyncio.TimeoutError:
            await charEmbedmsg.delete()
            await channel.send(f'Character creation timed out! Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
            self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
            return None, None
        else:
            if tReaction.emoji == '❌':
                await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                await charEmbedmsg.clear_reactions()
                self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                return None, None
        await charEmbedmsg.clear_reactions()
        charEmbed.clear_fields()
        choiceIndex = alphaEmojis.index(tReaction.emoji)
        subclass = subclassesList[choiceIndex].strip()

        return subclass, charEmbedmsg

    async def chooseFeat(self, ctx, race, charClass, cRecord, featLevels, charEmbed,  charEmbedmsg, charStats, charFeats):
        statNames = ['STR','DEX','CON','INT','WIS','CHA']
        author = ctx.author
        channel = ctx.channel

        def featCharEmbedCheck(r, u):
            sameMessage = False
            if charEmbedmsg.id == r.message.id:
                sameMessage = True
            return sameMessage and ((r.emoji in numberEmojis[:2]) or (str(r.emoji) == '❌')) and u == author
        
        def asiCharEmbedCheck(r, u):
            sameMessage = False
            if charEmbedmsg.id == r.message.id:
                sameMessage = True
            return sameMessage and ((r.emoji in alphaEmojis[:asiIndex]) or (str(r.emoji) == '❌')) and u == author

        def asiCharEmbedCheck2(r, u):
            sameMessage = False
            if charEmbedmsg2.id == r.message.id:
                sameMessage = True
            return sameMessage and ((r.emoji in alphaEmojis[:asiIndex]) or (str(r.emoji) == '❌')) and u == author


        featChoices = []
        featsPickedList = []
        featsChosen = ""
        featsCollection = db.feats

        if 'Max Stats' not in charStats:
            charStats['Max Stats'] = {'STR':20, 'DEX':20, 'CON':20, 'INT':20, 'WIS':20, 'CHA':20}

        spellcasting = False
        for f in featLevels:
            charEmbed.clear_fields()
            if f != 'Extra Feat':
                try:
                    charEmbed.add_field(name=f"Your level allows you to pick an Ability Score Improvement or a feat. Please react with 1 or 2 for your level {f} ASI/feat.", value=f"{numberEmojis[0]}: Ability Score Improvement\n{numberEmojis[1]}: Feat\n", inline=False)
                    if charEmbedmsg:
                        await charEmbedmsg.edit(embed=charEmbed)
                    else: 
                        charEmbedmsg = await channel.send(embed=charEmbed)
                    for num in range(0,2): await charEmbedmsg.add_reaction(numberEmojis[num])
                    await charEmbedmsg.add_reaction('❌')
                    charEmbed.set_footer(text= "React with ❌ to cancel.\nPlease react with a choice even if no reactions appear.")

                    tReaction, tUser = await self.bot.wait_for("reaction_add", check=featCharEmbedCheck, timeout=60)
                except asyncio.TimeoutError:
                    await charEmbedmsg.delete()
                    await channel.send(f'Feat selection timed out! Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                    self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                    return None, None, None
                else:
                    if tReaction.emoji == '❌':
                        await charEmbedmsg.edit(embed=None, content=f"Feat selection cancelled.  Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                        await charEmbedmsg.clear_reactions()
                        self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                        return None, None, None

                choice = int(tReaction.emoji[0])
                await charEmbedmsg.clear_reactions()

            else:
                choice = 2

            if choice == 1:
                try:
                    charEmbed.clear_fields()    
                    statsString = ""
                    asiString = ""
                    asiList = []
                    asiIndex = 0
                    for n in range(0,6):
                        if (int(charStats[statNames[n]]) + 1 <= charStats['Max Stats'][statNames[n]]):
                            statsString += f"{statNames[n]}: **{charStats[statNames[n]]}** "
                            asiString += f"{alphaEmojis[asiIndex]}: {statNames[n]}\n"
                            asiList.append(statNames[n])
                            asiIndex += 1
                        else:
                            statsString += f"{statNames[n]}: **{charStats[statNames[n]]}** (MAX) "

                    charEmbed.add_field(name=f"{statsString}\nReact to choose your first stat for your ASI:", value=asiString, inline=False)
                    await charEmbedmsg.edit(embed=charEmbed)
                    await charEmbedmsg.add_reaction('❌')
                    tReaction, tUser = await self.bot.wait_for("reaction_add", check=asiCharEmbedCheck, timeout=60)
                except asyncio.TimeoutError:
                    await charEmbedmsg.delete()
                    await channel.send(f'Character creation timed out! Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                    self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                    return None, None, None
                else:
                    if tReaction.emoji == '❌':
                        await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                        await charEmbedmsg.clear_reactions()
                        self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                        return None, None, None
                asi = alphaEmojis.index(tReaction.emoji)

                # May not need this at all due to choice omitting maxes
                # if (int(charStats[statNames[asi]]) + 1 > charStats['Max Stats'][statNames[asi]]):
                #     await charEmbedmsg.delete()
                #     await channel.send(f"You cannot increase your character's {statNames[asi]} above your maximum of {charStats['Max Stats'][statNames[asi]]}. Please try creating your character again.")
                #     self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                #     return None, None, None

                charStats[asiList[asi]] = int(charStats[asiList[asi]]) + 1
                charEmbed.set_field_at(0,name=f"ASI First Stat", value=f"{alphaEmojis[asi]}: {statNames[asi]}", inline=False)
                if ctx.invoked_with == "levelup":
                     charEmbed.description = f"{race}: {charClass}\n**STR**:{charStats['STR']} **DEX**:{charStats['DEX']} **CON**:{charStats['CON']} **INT**:{charStats['INT']} **WIS**:{charStats['WIS']} **CHA**:{charStats['CHA']}"

                try:
                    statsString = ""
                    asiString = ""
                    asiIndex = 0
                    asiList = []
                    for n in range(0,6):
                        if (int(charStats[statNames[n]]) + 1 <= charStats['Max Stats'][statNames[n]]):
                            statsString += f"{statNames[n]}: **{charStats[statNames[n]]}** "
                            asiString += f"{alphaEmojis[asiIndex]}: {statNames[n]}\n"
                            asiList.append(statNames[n])
                            asiIndex += 1
                        else:
                            statsString += f"{statNames[n]}: **{charStats[statNames[n]]}** (MAX) "
                        
                    charEmbed.add_field(name=f"{statsString}\nReact to choose your second stat for your ASI:", value=asiString, inline=False)
                    charEmbedmsg2 = await channel.send(embed=charEmbed)
                    await charEmbedmsg2.add_reaction('❌')
                    tReaction, tUser = await self.bot.wait_for("reaction_add", check=asiCharEmbedCheck2, timeout=60)
                except asyncio.TimeoutError:
                    await charEmbedmsg2.delete()
                    await channel.send(f'Character creation timed out! Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                    self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                    return None, None, None
                else:
                    if tReaction.emoji == '❌':
                        await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                        await charEmbedmsg.clear_reactions()
                        await charEmbedmsg2.delete()
                        self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                        return None, None, None
                asi = alphaEmojis.index(tReaction.emoji)

                # May not need this at all due to choice omitting maxes
                # if (int(charStats[statNames[asi]]) + 1 > charStats['Max Stats'][statNames[asi]]):
                #     await channel.send(f"You cannot increase your character's {statNames[asi]} above your MAX {charStats['Max Stats'][statNames[asi]]}. Please try creating your character again.")
                #     self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                #     return None, None, None

                charStats[asiList[asi]] = int(charStats[asiList[asi]]) + 1
                if ctx.invoked_with == "levelup":
                     charEmbed.description = f"{race}: {charClass}\n**STR**: {charStats['STR']} **DEX**: {charStats['DEX']} **CON**: {charStats['CON']} **INT**: {charStats['INT']} **WIS**: {charStats['WIS']} **CHA**: {charStats['CHA']}"
                await charEmbedmsg2.delete()
                await charEmbedmsg.clear_reactions()

            elif choice == 2:
                if featChoices == list():
                    fRecords, charEmbed, charEmbedmsg = await callAPI(ctx, charEmbed, charEmbedmsg,'feats')
                    for feat in fRecords:
                        featList = []
                        meetsRestriction = False

                        if 'Feat Restriction' not in feat and 'Race Restriction' not in feat and 'Class Restriction' not in feat and 'Stat Restriction' not in feat and (feat['Name'] not in charFeats) and 'Race Unavailable' not in feat and 'Require Spellcasting' not in feat:
                            featChoices.append(feat)

                        else:
                            if 'Feat Restriction' in feat and feat["Name"] not in charFeats:
                                featsList = [x.strip() for x in feat['Feat Restriction'].split(', ')]

                                for f in featsList:
                                    if f in charFeats or f in featsChosen:
                                        meetsRestriction = True
                                        
                            if 'Race Restriction' in feat:
                                featsList = [x.strip() for x in feat['Race Restriction'].split(', ')]

                                for f in featsList:
                                    if f in race:
                                        meetsRestriction = True

                            if 'Race Unavailable' in feat:
                                if race not in feat['Race Unavailable']:
                                    meetsRestriction = True
                            if 'Class Restriction' in feat:
                                featsList = [x.strip() for x in feat['Class Restriction'].split(', ')]
                                for c in cRecord:
                                    if ctx.invoked_with.lower() == "create" or ctx.invoked_with.lower() == "respec":
                                        if c['Class']['Name'] in featsList or c['Subclass'] in featsList:
                                            meetsRestriction = True
                                    else:
                                        if c['Name'] in featsList or c['Subclass'] in featsList:
                                            meetsRestriction = True
                                            
                            if 'Stat Restriction' in feat:
                                s = feat['Stat Restriction']
                                statNumber = int(s[-2:])
                                if '/' in s:
                                    checkStat = s[:len(s)-2].replace(" ", "").split('/')
                                    statSplitString = ""
                                else:
                                    checkStat = [s[:len(s)-2].strip()]

                                for stat in checkStat:
                                    if int(charStats[stat]) >= statNumber:
                                        meetsRestriction = True

                            if "Require Spellcasting" in feat:
                                for c in cRecord:
                                    if "Class" in c:
                                        if "Spellcasting" in c["Class"]:
                                            if c["Class"]["Spellcasting"] == True or c["Class"]["Spellcasting"] in charClass:
                                                meetsRestriction = True
                                    else:
                                        if "Spellcasting" in c:
                                            if c["Spellcasting"] == True or c["Spellcasting"] in charClass:
                                                meetsRestriction = True

                                
                                spellcastingFeats = list(featsCollection.find({"Spellcasting": True}))
                                for f in spellcastingFeats:
                                    if f["Name"] in charFeats:
                                         meetsRestriction = True

                            if meetsRestriction:
                                featChoices.append(feat)


                else:
                    # Whenever a feat that grants spellcasting gets picked.
                    if spellcasting == True:
                        spellcastingFeats = list(featsCollection.find({"Require Spellcasting": True}))
                        for f in spellcastingFeats:
                            featChoices.append(f)

                    featRestrictRecords = list(featsCollection.find({"Feat Restriction": {"$regex": featPicked["Name"], "$options": 'i' }}))
                    for f in featRestrictRecords:
                        if f not in featChoices:
                            featChoices.append(f)
                    featChoices.remove(featPicked)

                def featChoiceCheck(r, u):
                    sameMessage = False
                    if charEmbedmsg.id == r.message.id:
                        sameMessage = True
                    return sameMessage and u == author and (r.emoji == left or r.emoji == right or r.emoji == '❌' or r.emoji == back or r.emoji in alphaEmojis[:alphaIndex])

                page = 0
                perPage = 24
                numPages =((len(featChoices) - 1) // perPage) + 1
                featChoices = sorted(featChoices, key = lambda i: i['Name']) 

                while True:
                    charEmbed.clear_fields()  
                    if f == 'Extra Feat':
                        charEmbed.add_field(name=f"Your race allows you to choose a feat. Please choose your feat from the list below.", value=f"-", inline=False)
                    else:
                        charEmbed.add_field(name=f"Please choose your feat from the list below:", value=f"━━━━━━━━━━━━━━━━━━━━", inline=False)

                    pageStart = perPage*page
                    pageEnd = perPage * (page + 1)
                    alphaIndex = 0
                    for i in range(pageStart, pageEnd if pageEnd < (len(featChoices) - 1) else (len(featChoices)) ):
                        charEmbed.add_field(name=alphaEmojis[alphaIndex], value=featChoices[i]['Name'], inline=True)
                        alphaIndex+=1
                    charEmbed.set_footer(text= f"Page {page+1} of {numPages} -- use {left} or {right} to navigate or ❌ to cancel.")
                    await charEmbedmsg.edit(embed=charEmbed) 
                    await charEmbedmsg.add_reaction(left) 
                    await charEmbedmsg.add_reaction(right)
                    # await charEmbedmsg.add_reaction(back)
                    await charEmbedmsg.add_reaction('❌')

                    try:
                        react, user = await self.bot.wait_for("reaction_add", check=featChoiceCheck, timeout=90.0)
                    except asyncio.TimeoutError:
                        await charEmbedmsg.delete()
                        await channel.send(f"Character creation timed out!")
                        self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                        return None, None, None
                    else:
                        if react.emoji == left:
                            page -= 1
                            if page < 0:
                              page = numPages - 1
                        elif react.emoji == right:
                            page += 1
                            if page > numPages - 1: 
                              page = 0
                        elif react.emoji == '❌':
                            await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                            await charEmbedmsg.clear_reactions()
                            self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                            return None, None, None
                        # elif react.emoji == back:
                        #     await charEmbedmsg.delete()
                        #     await ctx.reinvoke()
                        elif react.emoji in alphaEmojis:
                            await charEmbedmsg.clear_reactions()
                            break
                        charEmbed.clear_fields()
                        await charEmbedmsg.clear_reactions()
                
                featPicked = featChoices[(page * perPage) + alphaEmojis.index(react.emoji)]

                # If feat picked grants spellcasting
                if "Spellcasting" in featPicked:
                    spellcasting = True

                featsPickedList.append(featPicked)

                # Special Case of Picked Ritual Caster
                def ritualFeatEmbedcheck(r, u):
                    sameMessage = False
                    if charEmbedmsg.id == r.message.id:
                        sameMessage = True
                    return sameMessage and ((r.emoji in alphaEmojis[:6]) or (str(r.emoji) == '❌')) and u == author

                def ritualSpellEmbedCheck(r, u):
                    sameMessage = False
                    if charEmbedmsg.id == r.message.id:
                        sameMessage = True

                    if (r.emoji in alphaEmojis[:alphaIndex]) and u == author:
                        ritualChoiceList[charEmbedmsg.id].add(r.emoji)

                    return sameMessage and ((len(ritualChoiceList[charEmbedmsg.id]) == 2) or (str(r.emoji) == '❌')) and u == author

                if featPicked['Name'] == "Ritual Caster":
                    ritualClasses = ["Bard", "Cleric", "Druid", "Sorcerer", "Warlock", "Wizard"]
                    charEmbed.clear_fields()
                    charEmbed.set_footer(text=charEmbed.Empty)
                    charEmbed.add_field(name="For the **Ritual Caster** feat, please pick the spellcasting class.", value=f"{alphaEmojis[0]}: Bard\n{alphaEmojis[1]}: Cleric\n{alphaEmojis[2]}: Druid\n{alphaEmojis[3]}: Sorcerer\n{alphaEmojis[4]}: Warlock\n{alphaEmojis[5]}: Wizard\n", inline=False)

                    try:
                        await charEmbedmsg.edit(embed=charEmbed)
                        await charEmbedmsg.add_reaction('❌')
                        tReaction, tUser = await self.bot.wait_for("reaction_add", check=ritualFeatEmbedcheck, timeout=60)
                    except asyncio.TimeoutError:
                        await charEmbedmsg.delete()
                        await channel.send(f'Character creation timed out! Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                        self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                        return None, None, None
                    else:
                        if tReaction.emoji == '❌':
                            await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                            await charEmbedmsg.clear_reactions()
                            self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                            return None, None, None
                    await charEmbedmsg.clear_reactions()

                    ritualClass = ritualClasses[alphaEmojis.index(tReaction.emoji)]
                    featPicked['Name'] = f"{featPicked['Name']} ({ritualClass})"
                    spellsCollection = db.spells
                    ritualSpellsList = list(spellsCollection.find({"$and": [{"Classes": {"$regex": ritualClass, '$options': 'i' }}, {"Ritual": True}, {"Level": 1}] }))

                    alphaIndex = 0
                    ritualSpellsString = ""
                    for r in ritualSpellsList:
                        ritualSpellsString += f"{alphaEmojis[alphaIndex]}: {r['Name']}\n"
                        alphaIndex += 1

                    charEmbed.set_field_at(0, name=f"For the **Ritual Caster** feat, please pick the spellcasting class.", value=f"{tReaction.emoji}: {ritualClass}", inline=False)
                    charEmbed.add_field(name=f"Please pick two {ritualClass} spells from this list to add to your ritual book.", value=ritualSpellsString, inline=False)
                    ritualChoiceList = {charEmbedmsg.id:set()}

                    charStats['Ritual Book'] = []
                    if len(ritualSpellsList) > 2:
                        try:
                            await charEmbedmsg.edit(embed=charEmbed)
                            await charEmbedmsg.add_reaction('❌')
                            tReaction, tUser = await self.bot.wait_for("reaction_add", check=ritualSpellEmbedCheck, timeout=60)
                        except asyncio.TimeoutError:
                            await charEmbedmsg.delete()
                            await channel.send(f'Character creation timed out! Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                            self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                            return None, None, None
                        else:
                            if tReaction.emoji == '❌':
                                await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                                await charEmbedmsg.clear_reactions()
                                self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                                return None, None, None
                        await charEmbedmsg.clear_reactions()
                        for r in ritualChoiceList[charEmbedmsg.id]:
                            rChoice = ritualSpellsList[alphaEmojis.index(r)]
                            charStats['Ritual Book'].append({'Name':rChoice['Name'], 'School':rChoice['School']})
                    else:
                        charStats['Ritual Book'].append({'Name':ritualSpellsList[0]['Name'], 'School':ritualSpellsList[0]['School']})
                        charStats['Ritual Book'].append({'Name':ritualSpellsList[1]['Name'], 'School':ritualSpellsList[1]['School']})
                    

                def slashFeatEmbedcheck(r, u):
                    sameMessage = False
                    if charEmbedmsg.id == r.message.id:
                        sameMessage = True
                    return sameMessage and ((r.emoji in numberEmojis[:len(featBonusList)]) or (str(r.emoji) == '❌')) and u == author

                if 'Stat Bonuses' in featPicked:
                    featBonus = featPicked['Stat Bonuses']
                    if '/' in featBonus or 'ANY' in featBonus:
                        if '/' in featBonus:
                            featBonusList = featBonus[:len(featBonus) - 3].split('/')
                        elif 'ANY' in featBonus:
                            featBonusList = statNames
                        featBonusString = ""
                        for num in range(len(featBonusList)):
                            featBonusString += f'{numberEmojis[num]}: {featBonusList[num]}\n'

                        try:
                            charEmbed.clear_fields()    
                            charEmbed.set_footer(text= charEmbed.Empty)
                            charEmbed.add_field(name=f"The {featPicked['Name']} feat lets you choose between {featBonus}. React with [1-{len(featBonusList)}] below with the stat(s) you would like to choose.", value=featBonusString, inline=False)
                            await charEmbedmsg.edit(embed=charEmbed)
                            for num in range(0,len(featBonusList)): await charEmbedmsg.add_reaction(numberEmojis[num])
                            await charEmbedmsg.add_reaction('❌')
                            tReaction, tUser = await self.bot.wait_for("reaction_add", check=slashFeatEmbedcheck, timeout=60)
                        except asyncio.TimeoutError:
                            await charEmbedmsg.delete()
                            await channel.send(f'Character creation timed out! Try again using the same command:\n```yaml\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"```')
                            self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                            return None, None, None
                        else:
                            if tReaction.emoji == '❌':
                                await charEmbedmsg.edit(embed=None, content=f"Character creation cancelled. Try again using the same command:\n```yaml\n{commandPrefix}create \"character name\" level \"race\" \"class\" \"background\" STR DEX CON INT WIS CHA \"reward item1, reward item2, [...]\"```")
                                await charEmbedmsg.clear_reactions()
                                self.bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
                                return None, None, None
                        await charEmbedmsg.clear_reactions()
                        charStats[featBonusList[int(tReaction.emoji[0]) - 1]] = int(charStats[featBonusList[int(tReaction.emoji[0]) - 1]]) + int(featBonus[-1:])
                            
                    else:
                        featBonusList = featBonus.split(', ')
                        for fb in featBonusList:
                            charStats[fb[:3]] =  int(charStats[fb[:3]]) + int(fb[-1:])

                if featsPickedList != list():
                    featsChosen = ', '.join(str(string['Name']) for string in featsPickedList)            

        if ctx.invoked_with == "levelup":
              charEmbed.description = f"{race}: {charClass}\n**STR**:{charStats['STR']} **DEX**:{charStats['DEX']} **CON**:{charStats['CON']} **INT**:{charStats['INT']} **WIS**:{charStats['WIS']} **CHA**:{charStats['CHA']}"

        return featsChosen, charStats, charEmbedmsg        


def setup(bot):
    bot.add_cog(Character(bot))
