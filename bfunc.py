import discord
import decimal
import math
import os
import time
import traceback
from discord.ext import commands, tasks
from os import listdir
from os.path import isfile, join
import asyncio
from pymongo import MongoClient
import re

from itertools import cycle

from pymongo import UpdateOne

from secret import *

cogs_dir = "cogs"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


def timeConversion (time,hmformat=False):
        hours = time//3600
        time = time - 3600*hours
        minutes = time//60
        if hmformat is False:
            return ('%d Hours %d Minutes' %(hours,minutes))
        else:
            return ('%dh%dm' %(hours,minutes))
        

async def traceBack (ctx,error,silent=False):
    ctx.command.reset_cooldown(ctx)
    etype = type(error)
    trace = error.__traceback__

    # 'traceback' is the stdlib module, `import traceback`.
    lines = traceback.format_exception(etype,error, trace)

    # format_exception returns a list with line breaks embedded in the lines, so let's just stitch the elements together
    traceback_text = ''.join(lines) +f"\n{ctx.message.author.mention}"

    dorfer = bot.get_user(203948352973438995)

    if not silent:
        length = len(traceback_text)
        while(length>1994):
            x = traceback_text[:1994]
            x = x.rsplit("\n", 1)[0]
            await dorfer.send(content=f"```{x}```")
            traceback_text = traceback_text[len(x):]
            length -= len(x)
        await dorfer.send(content=f"```{traceback_text}```")
        await ctx.channel.send(f"Uh oh, looks like this is some unknown error I have ran into. {dorfer.mention} has been notified.")
    raise error


def calculateTreasure(level, charcp, seconds, guildDouble=False, playerDouble=False, dmDouble=False, gold_modifier = 100):
    # calculate the CP gained during the game
    cp = ((seconds) // 1800) / 2
    cp_multiplier = 1 + guildDouble + playerDouble + dmDouble
       
        
    crossTier = None
    
    # calculate the CP with the bonuses included
    cp *= cp_multiplier
    
    gainedCP = cp
    
    #######role = role.lower()
    
    tier = 5
    # calculate the tier of the rewards
    if level < 5:
        tier = 1
    elif level < 11:
        tier = 2
    elif level < 17:
        tier = 3
    elif level < 20:
        tier = 4
        
    #unreasonably large number as a cap
    cpThreshHoldArray = [16, 16+60, 16+60+60, 16+60+60+30, 90000000]
    # calculate how far into the current level CP the character is after the game
    leftCP = charcp
    gp= 0
    tp = {}
    charLevel = level
    levelCP = (((charLevel-5) * 10) + 16)
    if charLevel < 5:
        levelCP = ((charLevel -1) * 4)
    while(cp>0):
        
        # Level 20 characters haves access to exclusive items
        # create a string representing which tier the character is in in order to create/manipulate the appropriate TP entry in the DB
        tierTP = f"T{tier} TP"
            
        if levelCP + leftCP + cp > cpThreshHoldArray[tier-1]:
            consideredCP = cpThreshHoldArray[tier-1] - (levelCP + leftCP)
            leftCP -= min(leftCP, cpThreshHoldArray[tier-1]-levelCP)
            levelCP = cpThreshHoldArray[tier-1]
        else:
            consideredCP = cp
        if consideredCP > 0:
            cp -=  consideredCP
            tp[tierTP] = consideredCP * tier_reward_dictionary[tier-1][1]
            gp += consideredCP * tier_reward_dictionary[tier-1][0]
        tier += 1
    gp = math.ceil(gold_modifier * gp/100)
    return [gainedCP, tp, int(gp)]
        
def refreshKey (timeStarted):
    if (time.time() - timeStarted > 60 * 59):
            gClient.login()
            print("Sucessfully refreshed OAuth")
            global refreshTime
            refreshTime = time.time()
    return

# token = os.environ['TOKEN']
currentTimers = {}

gameCategory = ["🎲 game rooms", "🐉 campaigns", "mod friends"]
roleArray = ['New', 'Junior', 'Journey', 'Elite', 'True', 'Ascended', '']
noodleRoleArray = ['Good Noodle', 'Elite Noodle', 'True Noodle', 'Ascended Noodle', 'Immortal Noodle', 'Eternal Noodle']
commandPrefix = '$'
timezoneVar = 'US/Eastern'

tier_reward_dictionary = [[50, 0.5], [100, 0.5], [150, 1], [200, 1], [200, 1]]

cp_bound_array = [[4, "4"], [10, "10"], [10, "10"], [10, "10"], [9999999999, "∞"]]

left = '\N{BLACK LEFT-POINTING TRIANGLE}'
right = '\N{BLACK RIGHT-POINTING TRIANGLE}'
back = '\N{LEFTWARDS ARROW WITH HOOK}'

numberEmojisMobile = ['1⃣','2⃣','3⃣','4⃣','5⃣','6⃣','7⃣','8⃣','9⃣']
numberEmojis = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','0️⃣']

alphaEmojis = ['🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰',
'🇱','🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹','🇺','🇻','🇼','🇽','🇾','🇿']

statuses = [f'D&D Friends | {commandPrefix}help', "We're all friends here!", f"See a bug? tell @MSchildorfer!", "Practicing social distancing!", "Wearing a mask!", "Being a good boio.", "Vibing", "Hippity Hoppity", "These Logs Are My Property", "UwU"]
discordClient = discord.Client(intents = intents)
@tasks.loop(minutes=10)
async def change_status():
    await bot.wait_until_ready()
    statusLoop = cycle(statuses)

    while not bot.is_closed():
        current_status = next(statusLoop)
        await bot.change_presence(activity=discord.Activity(name=current_status, type=discord.ActivityType.watching))
        await asyncio.sleep(5)

class FriendBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commandPrefix, case_insensitive=True, intents = intents)

    async def setup_hook(self):
        change_status.start()
        for extension in [f.replace('.py', '') for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
            try:
                await bot.load_extension(cogs_dir + "." + extension)
            except (discord.ClientException, ModuleNotFoundError):
                print(f'Failed to load extension {extension}.')
                traceback.print_exc()

    async def close(self):
        await super().close()
        #await self.session.close()


    async def on_ready(self):
        print('We have logged in as ' + self.user.name)

bot = FriendBot()
connection = MongoClient(mongoConnection, ssl=True) 
db = connection.dnd

settings = db.settings

global settingsRecord
settingsRecord = list(settings.find())[0]
# get all entries of the relevant DB and extract the Text field and compile as a list and assign to the dic
liner_dic = {"Find" : list([line["Text"] for line in db.liners_find.find()]),
             "Meme" : list([line["Text"] for line in db.liners_meme.find()]),
             "Craft" : list([line["Text"] for line in db.liners_craft.find()]),
             "Money" : list([line["Text"] for line in db.liners_money.find()])}
