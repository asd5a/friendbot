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
        
        
        # Converts the time given to data
        l = list((re.findall('.*?[hm]', lowerTimeString)))
        totalTime = 0
        
        # protect from incorrect inputs like #h#m
        try:
            for timeItem in l:
                    totalTime += convert_to_seconds(timeItem)
        except Exception as e:
            totalTime = 0

        if totalTime == 0:
            charEmbed.description = "You may have formatted the time incorrectly or calculated for 0. Try again with the correct format." + rewardCommand
            await channel.send(embed=charEmbed)
            return
        
        characterPresent = False    #base case: No character is given
        
        
        # Checks to see if a tier was given. If there wasn't, it then checks to see if a valid character was given. If not, error.
        if tier not in ('0','1','2','3','4', '5') and tier.lower() not in [r.lower() for r in roleArray]:
            charDict, charEmbedmsg = await checkForChar(ctx, char, charEmbed)
            if charDict == None:
                charEmbed.description = f"**{tier}** is not a valid tier or character name. Please try again with **New** or **0**, **Junior** or **1**, **Journey** or **2**, **Elite** or **3**, **True** or **4**, or **Ascended** or **5**, or input a valid character name."
                charEmbed.clear_fields()
                
                # reuse the message created by checkForChar
                if charEmbedmsg:
                    await charEmbedmsg.edit(embed=charEmbed)
                else:
                    await channel.send(embed=charEmbed)
                return
            else:
                characterPresent = True
        
        

        # Calculates rewards and output if a tier was given instead of a character
        if not characterPresent:
            tierName = ""
            if tier.isdigit():
                tierName = roleArray[int(tier)]
                tier = tierName
            else:
                tierName = tier.capitalize()

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
            
            charEmbed.description = f"A {durationString} game would give a **{tierName}** Friend\n{treasureString}"
            charEmbed.clear_fields()
            if charEmbedmsg:
                await charEmbedmsg.edit(embed=charEmbed)
            else:
                await channel.send(embed=charEmbed)
            return
        else:  # Calculates rewards and output if a character was given.
                        

            if charDict["Level"] < 5:
                tierNum = 0
            elif charDict["Level"] < 11:
                tierNum = 1
            elif charDict["Level"] < 17:
                tierNum = 2
            elif charDict["Level"] < 20:
                tierNum = 3
            else:
                tierNum = 4
            
            # Uses calculateTreasure to determine the rewards from the quest based on the character
            treasureArray  = calculateTreasure(charDict["Level"], charDict["CP"] , tierNum, totalTime)
            durationString = timeConversion(totalTime)
            treasureString = f"{treasureArray[0]} CP, {sum(treasureArray[1].values())} TP, {treasureArray[2]} GP"
            resultLevel = charDict["Level"]
            resultCP = charDict["CP"] + treasureArray[0]
            
            # CP and level calculations
            if resultLevel < 5:
                maxCP = 4
            else:
                maxCP = 10
                
            while(resultCP >= maxCP and resultLevel <20):
                resultCP -= maxCP
                resultLevel += 1
                if resultLevel > 4:
                    maxCP = 10
            
            # A list comprehension that joins together the TP values with their names into one string.
            tpString = ", ".join([f"{value} {key}" for key, value in treasureArray[1].items()])+", "
            
            totalGold = charDict["GP"] + treasureArray[2]
            
            # Final output plugs in the duration string, treasure string, tp string, and other variables to make a coherent output
            charEmbed.description = f"A {durationString} game would give **{charDict['Name']}** \n{treasureString}\n**{charDict['Name']}** will be level {resultLevel} with {resultCP} CP with an additional {tpString}and {totalGold} gold total!"
            charEmbed.clear_fields()
            if charEmbedmsg:
                await charEmbedmsg.edit(embed=charEmbed)
            else:
                await channel.send(embed=charEmbed)
            return
            
            
def setup(bot):
    bot.add_cog(Reward(bot))
