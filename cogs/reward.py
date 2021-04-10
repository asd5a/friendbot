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
        
        characterPresent = False    #base case: No character is given
        
        
        # Checks to see if a tier was given. If there wasn't, it then checks to see if a valid character was given. If not, error.
        if tier not in ('0','1','2','3','4', '5') and tier.lower() not in [r.lower() for r in roleArray]:
            charDict, charEmbedmsg = await checkForChar(ctx, char, charEmbed)
            if charDict == None:
                await channel.send(f"**{tier}** is not a valid tier or character name. Please try again with **New** or **0**, **Junior** or **1**, **Journey** or **2**, **Elite** or **3**, **True** or **4**, or **Ascended** or **5**, or input a valid character name.")
                return
            else:
                characterPresent = True
        
        # Converts the time given to data
        l = list((re.findall('.*?[hm]', lowerTimeString)))
        totalTime = 0
        for timeItem in l:
            totalTime += convert_to_seconds(timeItem)

        if totalTime == 0:
            await channel.send(content="You may have formatted the time incorrectly or calculated for 0. Try again with the correct format." + rewardCommand)
            return

        # Calculates rewards and output if a tier was given instead of a character
        if not characterPresent:
            tierName = ""
            if tier.isdigit():
                tierName = roleArray[int(tier)]
                tier = tierName
            else:
                tierName = tier.capitalize()
            print(tierName)

            cp = ((totalTime) // 1800) / 2
            tier = tier.lower()
            tierNum = 0
            if tier == 'junior':
              tierNum = 0
            elif tier == "journey":
              tierNum = 1
            elif tier == "elite":
              tierNum = 2
            elif tier == "true":
              tierNum = 3
            elif tier == "ascended":
              tierNum = 4
            
            gp = cp* tier_reward_dictionary[tierNum][0]
            tp = cp* tier_reward_dictionary[tierNum][1]

            treasureArray = [cp, tp, gp]
            durationString = timeConversion(totalTime)
            treasureString = f"{treasureArray[0]} CP, {treasureArray[1]} TP, and {treasureArray[2]} GP"
            await channel.send(content=f"A {durationString} game would give a **{tierName}** Friend\n{treasureString}")
            return
        else:  # Calculates rewards and output if a character was given.
                        

            if charDict["Level"] < 5:
                tierNum = 0
                tierInitial = 'T1 TP'
                tierNext = 'T2 TP'
                tierNext1 = 'T3 TP'
                tierNext2 = 'T4 TP'
                tierNext3 = 'T5 TP'
            elif charDict["Level"] < 11:
                tierNum = 1
                tierInitial = 'T2 TP'
                tierNext = 'T3 TP'
                tierNext1 = 'T4 TP'
                tierNext2 = 'T5 TP'
            elif charDict["Level"] < 17:
                tierNum = 2
                tierInitial = 'T3 TP'
                tierNext = 'T4 TP'
                tierNext1 = 'T5 TP'
            elif charDict["Level"] < 20:
                tierNum = 3
                tierInitial = 'T4 TP'
                tierNext = 'T5 TP'
            else:
                tierNum = 4
                tierInitial = 'T5 TP'
            
            # Uses calculateTreasure to determine the rewards from the quest based on the character
            treasureArray  = calculateTreasure(charDict["Level"], charDict["CP"] , tierNum, totalTime)
            durationString = timeConversion(totalTime)
            treasureString = f"{treasureArray[0]} CP, {sum(treasureArray[1].values())} TP, {treasureArray[2]} GP"
            resultLevel = charDict["Level"]
            resultCP = charDict["CP"] + treasureArray[0]
            
            if tierNum == 0 and resultCP > 4:   # For when levels are gained in tier 1
                while resultLevel < 5:
                    resultLevel += 1
                    resultCP -= 4
                    if resultCP < 5: # break the loop if they wouldn't level past 4
                        nextCP = resultCP
                        break
                    if resultLevel == 5: #if they go outside of tier 1
                        resultLevel += resultCP // 10
                        nextCP = resultCP % 10
            elif tierNum == 0:
                nextCP = resultCP
            else:
                resultLevel += resultCP // 10
                nextCP = resultCP % 10

            if resultLevel > 20:    # If tier 5 is reached, level is capped at 20
                levelDifference = resultLevel - 20
                nextCP += (levelDifference * 10)
                resultLevel = 20
                
            
            totalGold = charDict["GP"] + treasureArray[2]
            tpGained = treasureArray[1].values()
            if len(tpGained) == 1:  # Case for when the character stays in the tier
                await channel.send(content=f"A {durationString} game would give **{charDict['Name']}** \n{treasureString}\n**{charDict['Name']}** will be level {int(resultLevel)} with {int(nextCP)} CP with an additional {treasureArray[1].pop(tierInitial)} T{tierNum+1} TP and {totalGold} gold total!")
            elif len(tpGained) == 2: # Case for crossing just one tier
                await channel.send(content=f"A {durationString} game would give **{charDict['Name']}** \n{treasureString}\n**{charDict['Name']}** will be level {int(resultLevel)} with {int(nextCP)} CP with an additional {treasureArray[1].pop(tierInitial)} T{tierNum+1} TP, {treasureArray[1].pop(tierNext)} T{tierNum+2} TP, and {totalGold} gold total!")
            elif len(tpGained) == 3: # Rest are cases for cheeky bastards who think they'll be in absurdly long games
                await channel.send(content=f"A {durationString} game would give **{charDict['Name']}** \n{treasureString}\n**{charDict['Name']}** will be level {int(resultLevel)} with {int(nextCP)} CP with an additional {treasureArray[1].pop(tierInitial)} T{tierNum+1} TP, {treasureArray[1].pop(tierNext)} T{tierNum+2} TP, {treasureArray[1].pop(tierNext1)} T{tierNum+3} TP, and {totalGold} gold total! Did you remember to hydrate?")
            elif len(tpGained) == 4:
                await channel.send(content=f"A {durationString} game would give **{charDict['Name']}** \n{treasureString}\n**{charDict['Name']}** will be level {int(resultLevel)} with {int(nextCP)} CP with an additional {treasureArray[1].pop(tierInitial)} T{tierNum+1} TP, {treasureArray[1].pop(tierNext)} T{tierNum+2} TP, {treasureArray[1].pop(tierNext1)} T{tierNum+3} TP, {treasureArray[1].pop(tierNext2)} T{tierNum+4} TP, and {totalGold} gold total! Please, check on the kids.")
            elif len(tpGained) == 5:
                await channel.send(content=f"A {durationString} game would give **{charDict['Name']}** \n{treasureString}\n**{charDict['Name']}** will be level {int(resultLevel)} with {int(nextCP)} CP with an additional {treasureArray[1].pop(tierInitial)} T{tierNum+1} TP, {treasureArray[1].pop(tierNext)} T{tierNum+2} TP, {treasureArray[1].pop(tierNext1)} T{tierNum+3} TP, {treasureArray[1].pop(tierNext2)} T{tierNum+4} TP, {treasureArray[1].pop(tierNext3)} T{tierNum+5} TP, and {totalGold} gold total! Of course, you will die of exhaustion from playing that much in one game, but yay tier 5???")
            return
            
            
def setup(bot):
    bot.add_cog(Reward(bot))
