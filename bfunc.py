import discord
import gspread
import decimal
import os
import time
import traceback
# import json
import requests
from discord.ext import commands
import asyncio
from oauth2client.service_account import ServiceAccountCredentials
from pymongo import MongoClient
import re

from pymongo import UpdateOne

from secret import *

def timeConversion (time):
		hours = time//3600
		time = time - 3600*hours
		minutes = time//60
		return ('%d Hours %d Minutes' %(hours,minutes))
		
# def getTiers (tiers):
#     getTierArray = []
#     for i in range(len(tiers)):
#         if tiers[i] != "":
#             getTierArray.append(i)
#     getTierArray.append(len(sheet.row_values(3)) + 1)

#     return getTierArray

async def traceBack (ctx,error,silent=False):
    ctx.command.reset_cooldown(ctx)
    etype = type(error)
    trace = error.__traceback__

    # the verbosity is how large of a traceback to make
    # more specifically, it's the amount of levels up the traceback goes from the exception source
    verbosity = 2

    # 'traceback' is the stdlib module, `import traceback`.
    lines = traceback.format_exception(etype,error, trace, verbosity)

    # format_exception returns a list with line breaks embedded in the lines, so let's just stitch the elements together
    traceback_text = ''.join(lines)

    xyffei = ctx.guild.get_member(220742049631174656)

    if not silent:
        await xyffei.send(f"```{traceback_text}```\n")
        await ctx.channel.send(f"Uh oh, looks like this is some unknown error I have ran into. {ctx.guild.get_member(220742049631174656).mention} has been notified.")
    raise error

def calculateTreasure(seconds, role):
    cp = ((seconds) // 1800) / 2
    tp = .5 if cp == .5 else int(decimal.Decimal((cp / 2) * 2).quantize(0, rounding=decimal.ROUND_HALF_UP )) / 2
    gp = cp * 60
    role = role.lower()

    if role == 'journey':
      gp = cp * 120

    if role == "elite":
      tp = cp
      gp = cp * 180

    if role == "true":
      tp = cp
      gp = cp * 240

    # refactor later
    dcp = int(decimal.Decimal((cp / 2) * 2).quantize(0, rounding=decimal.ROUND_HALF_UP )) / 2
    dtp = int(decimal.Decimal((tp / 2) * 2).quantize(0, rounding=decimal.ROUND_HALF_UP )) / 2
    dgp = int(decimal.Decimal((gp / 2) * 2).quantize(0, rounding=decimal.ROUND_HALF_UP )) / 2

    return [cp, tp, gp, dcp, dtp, dgp]
    

    
    
    
"""
The purpose of this function is to do a general call to the database
apiEmbed -> the embed element that the calling function will be using
apiEmbedmsg -> the message that will contain apiEmbed
table -> the table in the database that should be searched in, most common tables are RIT, MIT and SHOP
query -> the word which will be searched for in the "Name" property of elements, adjustments were made so that also a special property "Grouped" also gets searched
singleItem -> if only one item should be returned
"""
async def callAPI(ctx, apiEmbed="", apiEmbedmsg=None, table=None, query=None, singleItem=False):
    
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
    query = query.strip()
    query = query.replace('(', '\\(')
    query = query.replace(')', '\\)')
    query = query.replace('+', '\\+')
    
    #I am not sure of the difference in behavior beside the extended Grouped search
    if singleItem:
        records = list(collection.find({"Name": {"$regex": query, '$options': 'i' }}))
    else:
        #search through the table for an element were the Name or Grouped property contain the query
        if table == "spells":
            filterDic = {"Name": {"$regex": query, '$options': 'i' }, 'Level': {'$gt':0}}
        else:
            filterDic = {"$or": [
                            {
                              "Name": {
                                "$regex": query,
                                #make the check case-insensitively
                                "$options": "i"
                              }
                            },
                            {
                              "Grouped": {
                                "$regex": query,
                                "$options": "i"
                              }
                            }
                          ]
                        }
                    
        # Here lies MSchildorfer's dignity. He copy and pasted with abandon and wondered why
        #  collection.find(collection.find(filterDic)) does not work for he could not read
        # https://cdn.discordapp.com/attachments/663504216135958558/735695855667118080/New_Project_-_2020-07-22T231158.186.png
        records = list(collection.find(filterDic))
    
    #turn the query into a regex expression
    r = re.compile(query)
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
    
    #sort all items alphabetically 
    records = sorted(records, key = sortingEntryAndList)    
    #if no elements are left, return nothing
    if records == list():
        return None, apiEmbed, apiEmbedmsg
    else:
        # if theres an exact match return
        if 'Name' in records[0]:
            print([r['Name'].lower() for r in records])
            for r in records:
                if query.lower() == r['Name'].lower():
                    return r, apiEmbed, apiEmbedmsg
    
        #create a string to provide information about the items to the user
        infoString = ""
        if (len(records) > 1):
            #sort items by tier if the magic item tables were requested
            if table == 'mit' or table == 'rit':
                records = sorted(records, key = lambda i : i ['Tier'])
            #limit items to 20
            for i in range(0, min(len(records), 20)):
                if table == 'mit':
                    infoString += f"{alphaEmojis[i]}: {records[i]['Name']} (Tier {records[i]['Tier']}): **{records[i]['TP']} TP**\n"
                elif table == 'rit':
                    infoString += f"{alphaEmojis[i]}: {records[i]['Name']} (Tier {records[i]['Tier']} {records[i]['Minor/Major']})\n"
                else:
                    infoString += f"{alphaEmojis[i]}: {records[i]['Name']}\n"
            #check if the response from the user matches the limits
            def apiEmbedCheck(r, u):
                sameMessage = False
                if apiEmbedmsg.id == r.message.id:
                    sameMessage = True
                return ((r.emoji in alphaEmojis[:min(len(records), 20)]) or (str(r.emoji) == '❌')) and u == author and sameMessage
            #inform the user of the current information and ask for their selection of an item
            apiEmbed.add_field(name=f"There seems to be multiple results for `{query}`, please choose the correct one.\nThe maximum results shown are 20. If the result you are looking for is not here, please react with ❌ and be more specific.", value=infoString, inline=False)
            if not apiEmbedmsg or apiEmbedmsg == "Fail":
                apiEmbedmsg = await channel.send(embed=apiEmbed)
            else:
                await apiEmbedmsg.edit(embed=apiEmbed)

            await apiEmbedmsg.add_reaction('❌')

            try:
                tReaction, tUser = await bot.wait_for("reaction_add", check=apiEmbedCheck, timeout=60)
            except asyncio.TimeoutError:
                #stop if no response was given within the timeframe and reenable the command
                await apiEmbedmsg.delete()
                await channel.send('Timed out! Try using the command again.')
                ctx.command.reset_cooldown(ctx)
                return None, apiEmbed, "Fail"
            else:
                #stop if the cancel emoji was given and reenable the command
                if tReaction.emoji == '❌':
                    await apiEmbedmsg.edit(embed=None, content=f"Command canceled. Try using the command again.")
                    await apiEmbedmsg.clear_reactions()
                    ctx.command.reset_cooldown(ctx)
                    return None, apiEmbed, "Fail"
            apiEmbed.clear_fields()
            #return the selected item indexed by the emoji given by the user
            await apiEmbedmsg.clear_reactions()
            return records[alphaEmojis.index(tReaction.emoji)], apiEmbed, apiEmbedmsg

        else:
            #if only 1 item was left, simply return it
            return records[0], apiEmbed, apiEmbedmsg

async def checkForChar(ctx, char, charEmbed="", mod=False):
    channel = ctx.channel
    author = ctx.author
    guild = ctx.guild

    playersCollection = db.players

    char = char.strip()
    char = char.replace('(', '\\(').replace(')', '\\)').replace('+', '\\+')

    if mod == True:
        charRecords = list(playersCollection.find({"Name": {"$regex": char, '$options': 'i' }})) 
    else:
        charRecords = list(playersCollection.find({"User ID": str(author.id), "Name": {"$regex": char, '$options': 'i' }}))

    if charRecords == list():
        if not mod:
            await channel.send(content=f'I was not able to find your character named `{char}`. Please check your spelling and try again.')
        ctx.command.reset_cooldown(ctx)
        return None, None

    else:
        if len(charRecords) > 1:
            infoString = ""
            charRecords = sorted(list(charRecords), key = lambda i : i ['Name'])
            for i in range(0, min(len(charRecords), 9)):
                infoString += f"{alphaEmojis[i]}: {charRecords[i]['Name']} ({guild.get_member(int(charRecords[i]['User ID']))})\n"
            
            def infoCharEmbedcheck(r, u):
                sameMessage = False
                if charEmbedmsg.id == r.message.id:
                    sameMessage = True
                return ((r.emoji in alphaEmojis[:min(len(charRecords), 9)]) or (str(r.emoji) == '❌')) and u == author and sameMessage

            charEmbed.add_field(name=f"There seems to be multiple results for `{char}`, please choose the correct character. If you do not see your character here, please react with ❌ and be more specific with your query.", value=infoString, inline=False)
            charEmbedmsg = await channel.send(embed=charEmbed)
            await charEmbedmsg.add_reaction('❌')

            try:
                tReaction, tUser = await bot.wait_for("reaction_add", check=infoCharEmbedcheck, timeout=60)
            except asyncio.TimeoutError:
                await charEmbedmsg.delete()
                await channel.send('Character information timed out! Try using the command again.')
                ctx.command.reset_cooldown(ctx)
                return None, None
            else:
                if tReaction.emoji == '❌':
                    await charEmbedmsg.edit(embed=None, content=f"Character information canceled. User `{commandPrefix}char info` command and try again!")
                    await charEmbedmsg.clear_reactions()
                    ctx.command.reset_cooldown(ctx)
                    return None, None
            charEmbed.clear_fields()
            await charEmbedmsg.clear_reactions()
            return charRecords[alphaEmojis.index(tReaction.emoji[0])], charEmbedmsg

    return charRecords[0], None

async def checkForGuild(ctx, name):
    channel = ctx.channel
    author = ctx.author
    guild = ctx.guild

    collection = db.guilds
    records = collection.find_one({"Name": {"$regex": name, '$options': 'i' }})

    if not records:
        return False
    else:
        return records
        
def refreshKey (timeStarted):
		if (time.time() - timeStarted > 60 * 59):
				gClient.login()
				print("Sucessfully refreshed OAuth")
				global refreshTime
				refreshTime = time.time()
		return

# use creds to create a client to interact with the Google Drive API
# gSecret = {
#   "type": "service_account",
#   "project_id": "magic-item-table",
#   "private_key_id": os.environ['PKEY_ID'],
#   "private_key": os.environ['PKEY'],
#   "client_email": os.environ['CEMAIL'],
#   "client_id": os.environ['C_ID'],
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://oauth2.googleapis.com/token",
#   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#   "client_x509_cert_url": os.environ['C_CERT']
# }

# scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# creds = ServiceAccountCredentials.from_json_keyfile_dict(gSecret, scope)

# gClient = gspread.authorize(creds)
# refreshTime = time.time()

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
# sheet = gClient.open("Magic Items Document").sheet1
# ritSheet = gClient.open("Magic Items Document").get_worksheet(1)
# charDatabase = gClient.open("Character Database").worksheet("Character Database")
# refListSheet = gClient.open("Character Database").worksheet("Reference Lists")


# sheet = gClient.open("Magic Item Table").sheet1
# ritSheet = gClient.open("Reward Item Table").sheet1

# token = os.environ['TOKEN']
currentTimers = []

gameCategory = ["🎲 game rooms", "🐉 campaigns", "mod friends"]
roleArray = ['Junior', 'Journey', 'Elite', 'True', '']
noodleRoleArray = ['Good Noodle', 'Elite Noodle', 'True Noodle', 'Ascended Noodle', 'Immortal Noodle']
# tierArray = getTiers(sheet.row_values(2))
# tpArray = sheet.row_values(3)
commandPrefix = '$'
timezoneVar = 'US/Central'

# ritTierArray = getTiers(ritSheet.row_values(2))
# ritSubArray = ritSheet.row_values(3)

# Quest Buffs - 2x Rewards, 2x Items, Recruitment Drive
questBuffsDict = {'2xRewards': [20, "2x CP,TP, and gp"], 
"2xItems - Small": [5,"+ 1 Tier 1 Minor Non-Consumable Reward"], 
"2xItems - Medium": [10, "+ 1 Same Tier or Lower Reward"], 
"2xItems - Large": [15,"Both of the above + 1 Tier 1 Minor Non-Consumable Reward"], 
"RD - Small":[4,"Small Guild Upgrade"], 
"RD - Medium": [6,"Small and Medium Upgrades"], 
"RD - Large": [9,"Small, Medium, and Large Upgrades"], 
"RD - All": [13, " All Guild Upgrades"]}
questBuffsArray = list(questBuffsDict.keys())

left = '\N{BLACK LEFT-POINTING TRIANGLE}'
right = '\N{BLACK RIGHT-POINTING TRIANGLE}'
back = '\N{LEFTWARDS ARROW WITH HOOK}'

numberEmojisMobile = ['1⃣','2⃣','3⃣','4⃣','5⃣','6⃣','7⃣','8⃣','9⃣']
numberEmojis = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣']

alphaEmojis = ['🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰',
'🇱','🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹','🇺','🇻','🇼','🇽','🇾','🇿']

statuses = [f'D&D Friends | {commandPrefix}help', "We're all friends here!", f"See a bug? tell @Xyffei!", "Practicing social distancing!", "Wearing a mask!", "Being a good boio."]
discordClient = discord.Client()
bot = commands.Bot(command_prefix=commandPrefix, case_insensitive=True)

connection = MongoClient(mongoConnection, ssl=True) 
db = connection.dnd

settings = db.settings
settingsRecord = list(settings.find())[0]

# API_URL = ('https://api.airtable.com/v0/appF4hiT6A0ISAhUu/'+ 'races')
# # API_URL += '?offset=' + 'itr4Z54rnNABYW8jj/recr2ss2DkyF4Q84X' 
# r = requests.get(API_URL, headers=headers)
# r = r.json()['records']
# playersCollection = db.races
# addList = []
# for i in r:
#     print(i['fields'])
#     addList.append(i['fields'])

# playersCollection.insert_many(addList)

# collection = db['mit']
# cl = list(collection.find({"Name": {"$regex": 'Vicious.*\+1$', '$options': 'i' }}))
# cData = list(map(lambda item: UpdateOne({'_id': item['_id']}, {'$set': {'TP':12, 'GP':5280 } }, upsert=True), cl))
# collection.bulk_write(cData)

# records = list(collection.find({"Modifiers": {"$regex": '', '$options': 'i' }}))


# i = 0
# for r in sorted(records, key = lambda i: i['Name']) :
#     print(r['Name'])
#     i+=1

# print (i)

# # delete
# collection.remove(({"Modifiers": {"$regex": '', '$options': 'i' }}))
