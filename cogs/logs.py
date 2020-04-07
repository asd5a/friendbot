import discord
import asyncio
import re
from discord.utils import get        
from discord.ext import commands
from bfunc import sheet, refreshKey, refreshTime, callAPI, db
from pymongo import UpdateOne

class Log(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
    
    @commands.group()
    async def log(self, ctx):	
        pass
      
    @log.command()
    async def edit(self, ctx, num, *, editString=""):
        # The real Bot
        # botUser = self.bot.get_user(502967681956446209)
        botUser = self.bot.get_user(650734548077772831)

        # Logs channel 
        channel = self.bot.get_channel(577227687962214406) 


        limit = 100
        msgFound = False
        async with channel.typing():
            async for message in channel.history(oldest_first=False, limit=limit):
                if int(num) == message.id and message.author == botUser:
                    editMessage = message
                    msgFound = True
                    break 

        if not msgFound:
            delMessage = await ctx.channel.send(content=f"I couldn't find your game with ID - `{num}` in the last {limit} games. Please try again, I will delete your message and this message in 10 seconds")
            await asyncio.sleep(10) 
            await delMessage.delete()
            await ctx.message.delete() 
            return


        sessionLogEmbed = editMessage.embeds[0]
        charData = []

        for log in sessionLogEmbed.fields:
            for i in "\<>@#&!:":
                log.value = log.value.replace(i, "")

            logItems = log.value.split(' | ')

            if "DM" in logItems[0]:
                for i in "*DM":
                    logItems[0] = logItems[0].replace(i, "")
                    dmID = logItems[0].strip()
            
            charData.append({"User ID" : logItems[0].strip() , "Name": logItems[1].split('\n')[0].strip()})

        if int(dmID) != ctx.author.id:
            delMessage = await ctx.channel.send(content=f"It doesn't look your you were the DM of this game. You won't be able to edit this session log. I will delete your message and this message in 10 seconds")
            await asyncio.sleep(10) 
            await delMessage.delete()
            await ctx.message.delete() 
            return


        sessionLogEmbed.description = editString+"\n"

        await editMessage.edit(embed=sessionLogEmbed)
        delMessage = await ctx.channel.send(content=f"I've edited the summary for Game #{num}.\n```{editString}```\nPlease double check that the edit is correct. I will now delete your message and this message in 30 seconds")

        if "✅" not in sessionLogEmbed.footer.text:
            usersCollection = db.users
            playersCollection = db.players
            uRecord = usersCollection.find_one({"User ID": dmID}, {'P-Noodles': 1})
            charRecordsList = list(playersCollection.find({"$or": charData }))

            data = []

            for charDict in charRecordsList:
                if f'GID{num}' in charDict:
                    charRewards = eval(charDict[f'GID{num}'])
                    keyList = []
                    for key, value in charRewards.items():
                        if 'TP' in key:
                            keyList.append(key)
                            if len(keyList) > 1:
                                tierTP2 = keyList[1]
                            tierTP = keyList[0]

                    print(tierTP)

                    if len(keyList) > 1:
                        data.append({'_id': charDict['_id'], "fields": {"$set": {'GP': charRewards['GP'], tierTP: charRewards[tierTP], tierTP2: charRewards[tierTP2], 'Consumables': charRewards['Consumables'], 'Magic Items': charRewards['Magic Items'], 'CP': charRewards['CP'], 'Games':charRewards['Games']}, "$unset": {f"GID{num}": 1} }})
                    else:
                        data.append({'_id': charDict['_id'], "fields": {"$set": {'GP': charRewards['GP'], tierTP: charRewards[tierTP], 'Consumables': charRewards['Consumables'], 'Magic Items': charRewards['Magic Items'], 'CP': charRewards['CP'], 'Games':charRewards['Games']}, "$unset": {f"GID{num}": 1} }})

            playersData = list(map(lambda item: UpdateOne({'_id': item['_id']}, item['fields']), data))

            try:
                if len(data) > 0:
                    playersCollection.bulk_write(playersData)

                usersCollection.update_one({'User ID': dmID}, {"$set": {'Noodles': uRecord['P-Noodles']}, "$unset": {"P-Noodles":1}}, upsert=True)        

            except Exception as e:
                print ('MONGO ERROR: ' + str(e))
                charEmbedmsg = await channel.send(embed=None, content="Uh oh, looks like something went wrong. Please try the command again.")
            else:
                print("Success")
                sessionLogEmbed.set_footer(text=sessionLogEmbed.footer.text + "\n✅ Log complete! Players have been rewarded. THe DM may still edit the summary if they wish.")
                await editMessage.edit(embed=sessionLogEmbed)
                await asyncio.sleep(30) 
                await delMessage.delete()
                await ctx.message.delete()

def setup(bot):
    bot.add_cog(Log(bot))
