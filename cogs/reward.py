import discord
import re
from discord.ext import commands
from bfunc import roleArray, calculateTreasure, timeConversion, commandPrefix, tier_reward_dictionary, checkForChar

class Reward(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot

    @commands.cooldown(1, 5, type=commands.BucketType.member)
    @commands.command()

    async def reward(self,ctx, timeString=None, tier=None):
        rewardCommand = f"\nPlease follow this format:\n```yaml\n{commandPrefix}reward \"#h#m\" \"tier or character name\"```\n"

        def convert_to_seconds(s):
            return int(s[:-1]) * seconds_per_unit[s[-1]]

        channel = ctx.channel
        author = ctx.author
        charEmbed = discord.Embed()
        charEmbedmsg = None
        char = tier #this is mainly for my sanity
        
        if timeString is None:
            await channel.send(content="Woops, you're forgetting the time duration for the command." + rewardCommand)
            return

        if tier is None:
            await channel.send(content="Woops, you're forgetting the tier or character name for the command. Please try again with 1, 2, 3, or 4 or Junior, Journey, Elite, or True as the tier, or use a character name and" + rewardCommand)
            return

        seconds_per_unit = { "m": 60, "h": 3600 }
        lowerTimeString = timeString.lower()
        
        characterPresent = None

        if tier not in ('0','1','2','3','4', '5') and tier.lower() not in [r.lower() for r in roleArray]:
            charDict, charEmbedmsg = await checkForChar(ctx, char, charEmbed)
            if charDict == None:
                await channel.send(f"**{tier}** is not a valid tier or character name. Please try again with **New** or **0**, **Junior** or **1**, **Journey** or **2**, **Elite** or **3**, **True** or **4**, or **Ascended** or **5**, or input a valid character name.")
                return
            else:
                characterPresent = True
        
        if characterPresent == None:
            tierName = ""
            if tier.isdigit():
                tierName = roleArray[int(tier)]
                tier = tierName
            else:
                tierName = tier.capitalize()
            print(tierName)
            l = list((re.findall('.*?[hm]', lowerTimeString)))
            totalTime = 0
            for timeItem in l:
                totalTime += convert_to_seconds(timeItem)

            if totalTime == 0:
                await channel.send(content="You may have formatted the time incorrectly or calculated for 0. Try again with the correct format." + rewardCommand)
                return

            cp = ((totalTime) // 1800) / 2
            tier = tier.lower()
            t = 0
            if tier == 'junior':
              t = 0
            elif tier == "journey":
              t = 1
            elif tier == "elite":
              t = 2
            elif tier == "true":
              t = 3
            elif tier == "ascended":
              t = 4
            
            gp = cp* tier_reward_dictionary[t][0]
            tp = cp* tier_reward_dictionary[t][1]

            treasureArray = [cp, tp, gp]
            durationString = timeConversion(totalTime)
            treasureString = f"{treasureArray[0]} CP, {treasureArray[1]} TP, and {treasureArray[2]} GP"
            await channel.send(content=f"A {durationString} game would give a **{tierName}** Friend\n{treasureString}")
            return
        elif characterPresent == True:
            l = list((re.findall('.*?[hm]', lowerTimeString)))
            totalTime = 0
            for timeItem in l:
                totalTime += convert_to_seconds(timeItem)

            if totalTime == 0:
                await channel.send(content="You may have formatted the time incorrectly or calculated for 0. Try again with the correct format." + rewardCommand)
                return
            
            t = 0
            if charDict["Level"] < 5:
                t = 0
                tierInitial = 'T1 TP'
                tierNext = 'T2 TP'
            elif charDict["Level"] < 11:
                t = 1
                tierInitial = 'T2 TP'
                tierNext = 'T3 TP'
            elif charDict["Level"] < 17:
                t = 2
                tierInitial = 'T3 TP'
                tierNext = 'T4 TP'
            elif charDict["Level"] < 20:
                t = 3
                tierInitial = 'T4 TP'
                tierNext = 'T5 TP'
            elif charDict["Level"] == 20:
                t = 4
                tierInitial = 'T5 TP'
            
            treasureArray  = calculateTreasure(charDict["Level"], charDict["CP"] , t, totalTime)
            durationString = timeConversion(totalTime)
            treasureString = f"{treasureArray[0]} CP, {sum(treasureArray[1].values())} TP, {treasureArray[2]} GP"
            resultLevel = charDict["Level"]
            resultCP = charDict["CP"] + treasureArray[0]
            resultLevel += resultCP // 10
            nextCP = resultCP % 10
            totalGold = charDict["GP"] + treasureArray[2]
            tpGained = treasureArray[1].values()
            if len(tpGained) == 1:
                await channel.send(content=f"A {durationString} game would give **{charDict['Name']}** \n{treasureString}\n**{charDict['Name']}** will be level {int(resultLevel)} with {int(nextCP)} CP with an additional {treasureArray[1].pop(tierInitial)} T{t+1} TP and {totalGold} gold total!")
            else:
                await channel.send(content=f"A {durationString} game would give **{charDict['Name']}** \n{treasureString}\n**{charDict['Name']}** will be level {int(resultLevel)} with {int(nextCP)} CP with an additional {treasureArray[1].pop(tierInitial)} T{t+1} TP, {treasureArray[1].pop(tierNext)} T{t+2} TP,  and {totalGold} gold total!")
            return
            
            
def setup(bot):
    bot.add_cog(Reward(bot))
