import asyncio
import traceback
from discord.ext import commands
from os import listdir
from os.path import isfile, join
from itertools import cycle

from bfunc import *

cogs_dir = "cogs"

# Files to check for server differences: logs, timer, misc

# Things that can change
# ~ Server roles.
# ~ Quest Board.
# ~ Session Logs.
# ~ Campaign Board.
# ~ Applications.
# ~ Game Rooms (including timers).
# ~ General Rooms (excluding timers).
# ~ Suggestions.
# ~ General Reports.
# ~ Staff Reports.

async def change_status():
      await bot.wait_until_ready()
      statusLoop = cycle(statuses)

      while not bot.is_closed():
          current_status = next(statusLoop)
          await bot.change_presence(activity=discord.Activity(name=current_status, type=discord.ActivityType.watching))
          await asyncio.sleep(5)

@bot.event
async def on_ready():
    print('We have logged in as ' + bot.user.name)
    # bot.loop.create_task(change_status())

    #secret area channel
    # channel = bot.get_channel(577611798442803205) 
    # await channel.send('Hello I have restarted uwu')
  
bot.remove_command('help')

@bot.event
async def on_command_error(ctx,error):
    msg = None
    print(ctx.invoked_with)
    print(ctx.command.parent)
    print(error)
    
    if isinstance(error, commands.UnexpectedQuoteError) or isinstance(error, commands.ExpectedClosingQuoteError) or isinstance(error, commands.InvalidEndOfQuotedStringError):
        await ctx.channel.send("There seems to be an unexpected or a missing closing quote mark somewhere, please check your format and retry the command. ")
        #bot.get_command(ctx.invoked_with).reset_cooldown(ctx)
        ctx.command.reset_cooldown(ctx)
        return
    
    elif ctx.cog is not None and ctx.cog._get_overridden_method(ctx.cog.cog_command_error) is not None:
        return
        
    elif isinstance(error, commands.CommandOnCooldown):
        commandParent = ctx.command.parent
        if commandParent is None:
            commandParent = ''
        else:
            commandParent = commandParent.name + " "

        if error.retry_after == float('inf'):
            await ctx.channel.send(f"Sorry, the command **`{commandPrefix}{commandParent}{ctx.invoked_with}`** is already in progress, please complete the command before trying again.")
        else:
            await ctx.channel.send(f"Sorry, the command **`{commandPrefix}{commandParent}{ctx.invoked_with}`** is on cooldown for you! Try the command in the next " + "{:.1f}seconds".format(error.retry_after))
        return



    elif isinstance(error, commands.CommandNotFound):
        await ctx.channel.send(f'Sorry, the command **`{commandPrefix}{ctx.invoked_with}`** is not valid, please try again!')

    else:
        ctx.command.reset_cooldown(ctx)
        await traceBack(ctx,error)

@bot.command()
async def help(ctx, *, pageString=''):
    def helpCheck(r,u):
        sameMessage = False
        if helpMsg.id == r.message.id:
            sameMessage = True
        return (r.emoji in numberEmojis[:numPages]) and u == ctx.author and sameMessage

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
    if 'general' in pageString:
        page = 1
    elif 'char' in pageString:
        page = 2
    elif 'timer2' in pageString:
        page = 4
    elif 'timer3' in pageString:
        page = 5
    elif 'timer1' in pageString or 'timer' in pageString:
        page = 3
    elif 'shop' in pageString:
        page = 6
    elif 'tp' in pageString:
        page = 7
    elif 'guild' in pageString:
        page = 8
    elif 'campaign' in pageString:
        page = 9


# MAIN HELP MENU ($help)


    helpList = [helpEmbedMenu, helpEmbedGen, helpEmbedChar, helpEmbedTimerOne, helpEmbedTimerTwo, helpEmbedTimerThree, helpEmbedShop, helpEmbedTp, helpEmbedGuild, helpEmbedCampaign]

    helpEmbedMenu.title = 'Bot Friend Commands - Table of Contents'
    helpEmbedMenu.description = 'Please react to the group of commands you would like to see and gain more knowledge about.'
    helpEmbedMenu.add_field(name=f"1️⃣ General Commands\n{commandPrefix}help gen", value="Various commands which don't fit into any other section.", inline=False)
    helpEmbedMenu.add_field(name=f"2️⃣ Character Commands\n{commandPrefix}help char", value="How to manage your character(s).", inline=False)
    helpEmbedMenu.add_field(name=f"3️⃣ Pre-Quest Timer Commands\n{commandPrefix}help timer1", value="How to prepare and sign up to a timer for a one-shot.", inline=False)
    helpEmbedMenu.add_field(name=f"4️⃣ Running Timer Commands\n{commandPrefix}help timer2", value="How to do various things while hosting or participating in a one-shot.", inline=False)
    helpEmbedMenu.add_field(name=f"5️⃣ Post-Quest Timer Commands\n{commandPrefix}help timer3", value="How to do various things after the completion of a one-shot.", inline=False)
    helpEmbedMenu.add_field(name=f"6️⃣ Shop Commands\n{commandPrefix}help shop", value="How to spend GP to purchase various things or sell mundane items.", inline=False)
    helpEmbedMenu.add_field(name=f"7️⃣ TP Commands\n{commandPrefix}help tp", value="How to spend TP to acquire magic items.", inline=False)
    helpEmbedMenu.add_field(name=f"8️⃣ Guild Commands\n{commandPrefix}help guild", value="How to be a member of a guild or manage one.", inline=False)
    helpEmbedMenu.add_field(name=f"9️⃣ Campaign Commands\n{commandPrefix}help campaign", value="How to create, host, and participate in a campaign.", inline=False)



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

    helpEmbedGen.add_field(name=f'▫️ Creating and Viewing Your User Profile\n{commandPrefix}user', value="Create a user profile on our system and view the total number of one-shots that you’ve played in, the number of Noodles you have, the number of characters you have, the guilds you’ve created, and a list of your characters sorted by tier.", inline=False)

    helpEmbedGen.add_field(name=f'▫️ Viewing Server Stats\n{commandPrefix}stats', value="View various stats about the server such as the number of one-shots and campaign sessions hosted on a monthly and lifetime basis, character creation stats, and magic item stats.", inline=False)

    helpEmbedGen.add_field(name=f'▫️ Calculating Rewards\n{commandPrefix}reward XhYm tier', value="Look up the rewards that a specified amount of time would give for the specified tier.", inline=False)

    helpEmbedGen.add_field(name=f'▫️ Viewing the Help Menu\n{commandPrefix}help', value="View the help menu which has the same information as the Bot Friend Command Guides.", inline=False)

    helpEmbedGen.add_field(name=f'▫️ Print a List of Allowed Races\n{commandPrefix}printRaces', value="Print a list of all races which are allowed on the server in order to know exactly how to spell them for character creation.", inline=False)



# CHARACTER COMMANDS MENU ($help char)

    helpEmbedChar.title = 'Character Commands'

    helpEmbedChar.add_field(name=f'▫️ Creating a Character\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"', value="Create a character with the specified parameters. See #how-to-play or the Bot Friend Player Commands Guide for more information.", inline=False)

    helpEmbedChar.add_field(name=f'▫️ Viewing a Character\'s Information\n{commandPrefix}info "character name"\n[{commandPrefix}char, {commandPrefix}i]', value="View your character's stats  and general information.", inline=False)

    helpEmbedChar.add_field(name=f'▫️ Viewing a Character\'s Inventory\n{commandPrefix}inventory "character name"\n[{commandPrefix}inv, {commandPrefix}bag]', value="View your character's inventory.", inline=False)

    helpEmbedChar.add_field(name=f'▫️ Adding an Image to a Character\n{commandPrefix}image "character name" "URL"\n[{commandPrefix}img]', value="Add an image to your character’s information page using a URL. Images must be SFW (Safe For Work).", inline=False)

    helpEmbedChar.add_field(name=f'▫️ Leveling Up\n{commandPrefix}levelup "character name"\n[{commandPrefix}lvlup, {commandPrefix}lvl, {commandPrefix}lv]', value="Level up your character to the next level (if possible). If they gain an ASI or feat, you will be prompted to choose one during the level-up process.", inline=False)

    helpEmbedChar.add_field(name=f'▫️ Creating a Multiclass Character\n{commandPrefix}create "character name" total level "race" "class1 level / class2 level, [...]" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]"', value="Create a multiclass character with the specified parameters.", inline=False)

    helpEmbedChar.add_field(name=f'▫️ Respecing a Character\n{commandPrefix}respec "character name" "new character name" "race" "class" "background" STR DEX CON INT WIS CHA', value="Respec your character into a single class if they are under level 5 or if you are given special permission. TP and GP will be assigned to them based on the amount of CP they have and their entire inventory will be reset.", inline=False)

    helpEmbedChar.add_field(name=f'▫️ Respecing a Character into a Multiclass\n{commandPrefix}respec "character name" "new character name" "race" "class1 level / class2 level / [...]" "background" STR DEX CON INT WIS CHA', value="Respec your character into a multiclass if they are under level 5 or if you are given special permission. TP and GP will be assigned to them based on the amount of CP they have and their entire inventory will be reset.", inline=False)

    helpEmbedChar.add_field(name=f'▫️ Reflavoring a Character\'s Race\n{commandPrefix}reflavor "character name" race name\n[{commandPrefix}r5]', value="Reflavor the name of your character’s race into whatever you want. The new race name must be between 1 and 20 symbols in length and must be SFW (Safe For Work).", inline=False)

    helpEmbedChar.add_field(name=f'▫️ Retiring a Character\n{commandPrefix}retire "character name"', value="Retire your character. This will permanently delete them from the system and you will no longer be able to access them.", inline=False)

    helpEmbedChar.add_field(name=f'▫️ Attuning to a Magic Item\n{commandPrefix}attune "character name" "magic item"\n[{commandPrefix}att]', value="Make your character attune to a magic item which requires attunement.", inline=False)

    helpEmbedChar.add_field(name=f'▫️ Unattuning from a Magic Item\n{commandPrefix}unattune "character name" "magic item"\n[{commandPrefix}unatt, {commandPrefix}uatt]', value="Make your character unattune from a magic item which requires attunement.", inline=False)

    helpEmbedChar.add_field(name=f'▫️ Death Options\n{commandPrefix}death "character name"', value=f"Decide the fate of your character who died during a quest.", inline=False)


# PRE-QUEST TIMER COMMANDS MENU ($help timer1)

# PLAYER COMMANDS

    helpEmbedTimerOne.title = f"Pre-Quest Timer Commands\n{commandPrefix}timer, {commandPrefix}t"

    helpEmbedTimerOne.add_field(name=f'▫️ Signing Up (Player)\n{commandPrefix}timer signup "character name" "consumable1, consumable2, [...]"', value="Sign up to a prepared timer with your character and their consumables but only if you have been selected to join the one-shot and were mentioned when the timer was prepared.", inline=False)

# DM COMMANDS

    helpEmbedTimerOne.add_field(name=f'▫️ Preparing the Timer (DM)\n{commandPrefix}timer prep "@player1, @player2, [...]" questname', value="Prepare a timer with a list of players so they can sign up with their characters.", inline=False)

    helpEmbedTimerOne.add_field(name=f'▫️ Adding Players to the Roster (DM)\n{commandPrefix}timer add @player', value="Add a player to the roster after you have already prepared the timer so they can sign up.", inline=False)

    helpEmbedTimerOne.add_field(name=f'▫️ Removing Players from the Roster (DM)\n{commandPrefix}timer remove @player', value="Remove a player from the roster.", inline=False)

    helpEmbedTimerOne.add_field(name=f'▫️ Adding Guilds (DM)\n{commandPrefix}timer guild #guild1, #guild2, #guild3', value="Add a maximum of three guilds to your quest. Each use of this command replaces the previous use.", inline=False)

    helpEmbedTimerOne.add_field(name=f'▫️ Cancelling the Timer (DM)\n{commandPrefix}timer cancel', value="Cancel the prepared timer.", inline=False)

    helpEmbedTimerOne.add_field(name=f'▫️ Starting the Timer (DM)\n{commandPrefix}timer start', value="Start the prepared timer.", inline=False)


# RUNNING TIMER COMMANDS MENU ($help timer2)

# PLAYER COMMANDS

    helpEmbedTimerTwo.title = f"Running Timer Commands\n{commandPrefix}timer, {commandPrefix}t"

    helpEmbedTimerTwo.add_field(name=f'▫️ Adding Yourself (Player)\n{commandPrefix}timer addme "character name" "consumable1, consumable2, [...]"', value="Request permission to join a one-shot with your character and their consumables after it has already been started. This only functions if there is a spot for the player and the DM must approve the request.", inline=False)

    helpEmbedTimerTwo.add_field(name=f'▫️ Using Items (Player)\n- item', value="Use one of the consumables that your character brought into the one-shot or any mundane item in their inventory. This will permanently remove the consumable or item from their inventory.", inline=False)

    helpEmbedTimerTwo.add_field(name=f'▫️ Removing Yourself (Player)\n{commandPrefix}timer removeme', value="Remove yourself from the running timer.", inline=False)

    helpEmbedTimerTwo.add_field(name=f'▫️ Checking the Timestamp (Player)\n{commandPrefix}timer removeme', value="Refresh the running timer’s information box.", inline=False)

# DM COMMANDS

    helpEmbedTimerTwo.add_field(name=f'▫️ Adding Players During a Quest (DM)\n{commandPrefix}timer add @player "character name" "consumable1, consumable2, [...]"', value="Add a player to the running timer with their character and consumables.", inline=False)

    helpEmbedTimerTwo.add_field(name=f'▫️ Removing Players During a Quest (DM)\n{commandPrefix}timer remove @player', value="Remove a player from the running timer.", inline=False)

    helpEmbedTimerTwo.add_field(name=f'▫️ Awarding Reward Items (DM)\n{commandPrefix}timer reward @player "reward item1, reward item2, [...]"', value="Award one or more reward items from the **Reward Item Table** to a player.", inline=False)

    helpEmbedTimerTwo.add_field(name=f'▫️ Revoking Reward Items (DM)\n{commandPrefix}timer undo rewards @player "reward item1, reward item2, [...]"', value="Revoke all reward items that you have awarded to your players and yourself.", inline=False)

    helpEmbedTimerTwo.add_field(name=f'▫️ Character Death (DM)\n{commandPrefix}timer death @player', value="Remove a player (and their character) from the timer if their character dies during the quest.", inline=False)

    helpEmbedTimerTwo.add_field(name=f'▫️ Stopping the Timer (DM)\n{commandPrefix}timer stop', value="Stop the running timer which creates the session log for it.", inline=False)


# POST-QUEST TIMER COMMANDS MENU ($help timer3)

# PLAYER COMMANDS

    helpEmbedTimerThree.title = f"Post-Quest Timer Commands\n{commandPrefix}timer, {commandPrefix}t"

    helpEmbedTimerThree.add_field(name=f'▫️ Opting Out of Guild 2x Rewards (Player)\n{commandPrefix}session optout2xR gameID', value="Opt out of the 2x Rewards Guild Boon whenever it is activated. You are automatically opted into it whenever it is used.", inline=False)

    helpEmbedTimerThree.add_field(name=f'▫️ Opting Into of Guild 2x Rewards (Player)\n{commandPrefix}session optin2xR gameID', value="Opt into the 2x Rewards Guild Boon if you previously opted out of it.", inline=False)

    helpEmbedTimerThree.add_field(name=f'▫️ Opting Out of Guild 2x Items (Player)\n{commandPrefix}session optout2xI gameID', value="Opt out of the 2x Items Guild Boon whenever it is activated. You are automatically opted into it whenever it is used.", inline=False)

    helpEmbedTimerThree.add_field(name=f'▫️ Opting Into of Guild 2x Items (Player)\n{commandPrefix}session optin2xI gameID', value="Opt into the 2x Items Guild Boon when the guild that your character is a member of activates it in a quest that you are participating in with that character. You are automatically opted into 2x Items whenever it is used.", inline=False)

# DM COMMANDS

    helpEmbedTimerThree.add_field(name=f'▫️ Submitting a Session Log (DM)\n{commandPrefix}session log questID summary', value="Submit a session log summary for the running timer which you just stopped. See #hosting-a-one-shot or the Bot Friend DM Commands Guide for more information.", inline=False)

    helpEmbedTimerThree.add_field(name=f'▫️ Approve Guild 2x Rewards (DM)\n{commandPrefix}approveRewards gameID #guild-channel', value="Enable the 2x Rewards Guild Boon for a guild quest which you host.", inline=False)

    helpEmbedTimerThree.add_field(name=f'▫️ Deny Guild 2x Rewards (DM)\n{commandPrefix}session denyRewards gameID #guild-channel', value="Disable the 2x Rewards Guild Boon for a guild quest which you host.", inline=False)

    helpEmbedTimerThree.add_field(name=f'▫️ Approve Guild 2x Items (DM)\n{commandPrefix}approveItems gameID #guild-channel', value="Enable the 2x Items Guild Boon for a guild quest which you host.", inline=False)

    helpEmbedTimerThree.add_field(name=f'▫️ Deny Guild 2x Items (DM)\n{commandPrefix}session denyItems gameID #guild-channel', value="Disable the 2x Items Guild Boon for a guild quest which you host.", inline=False)

    helpEmbedTimerThree.add_field(name=f'▫️ Approve Recruitment Drive (DM)\n{commandPrefix}approveDrive gameID #guild-channel', value="Enable the Recruitment Drive Guild Boon for a guild quest which you host.", inline=False)

    helpEmbedTimerThree.add_field(name=f'▫️ Deny Recruitment Drive (DM)\n{commandPrefix}session denyDrive gameID #guild-channel', value="Disable the Recruitment Drive Guild Boon for a guild quest which you host.", inline=False)

    helpEmbedTimerThree.add_field(name=f'▫️ Opting Out of DDMRW (DM)\n{commandPrefix}session ddmrw optout gameID', value="Opt out of Double DM Rewards Weekend (DDMRW) and not to receive Double DM Rewards for a quest which host during DDMRW. Any quest which ends during DDMRW will automatically have Double DM Rewards applied to it so you will have to opt out of it by default.", inline=False)

    helpEmbedTimerThree.add_field(name=f'▫️ Opting Into DDMRW (DM)\n{commandPrefix}session ddmrw optin gameID', value="Opt into DDMRW if you previously opted out of it.", inline=False)


# ITEM TABLE COMMANDS MENU ($help itemtable)

############### THIS IS OBSOLETE UNTIL YOU MAKE A NEW SYSTEM.

#    helpEmbedItems.title = 'Item Table Commands'
#    helpEmbedItems.add_field(name=f'▫️ Magic Item Table Lookup\n{commandPrefix}mit [optional name search]', value=f"Look up items from the Magic Item Table, sorted by tier and TP cost. React to the lists to change pages or view items. You can also search by name, for example: {commandPrefix}mit Folding Boat", inline=False)
#    helpEmbedItems.add_field(name=f'▫️ Reward Item Table Lookup\n{commandPrefix}rit [optional name search]', value=f"Look up items from the Reward Item Table, sorted by tier and Minor/Major. React to the lists to change pages or view items. You can also search by name, for example: {commandPrefix}rit Clockwork Dog", inline=False)
#    helpEmbedItems.add_field(name=f'▫️ Random Reward Item\n{commandPrefix}rit random', value=f"Display a random reward item based on the tier and sub-tier you selected.", inline=False)


# SHOP COMMANDS MENU ($help shop)

    helpEmbedShop.title = 'Shop Commands'

    helpEmbedShop.add_field(name=f'▫️ Buying a Shop Item\n{commandPrefix}shop buy "character name" "item" #', value="Purchase a specified number of a single item for your character from the shop. If no number is specified then only one mundane item will be purchased. Purchasing a spell scroll uses the following format: \"Spell Scroll (spell name)\"", inline=False)

    helpEmbedShop.add_field(name=f'▫️ Buying a Miscellaneous Item\n{commandPrefix}shop buy "character name" Miscellaneous #', value="Spend a specified amount of your character’s GP on nothing. This simulates expenses of any kind or items which aren’t available on the **Other Item Table (OIT)**.", inline=False)

    helpEmbedShop.add_field(name=f'▫️ Selling a Mundane Item\n{commandPrefix}shop sell "character name" "item" #', value="Sell a specified number of a single mundane item from your character to the shop. If no number is specified then only one mundane item will be sold.", inline=False)

    helpEmbedShop.add_field(name=f'▫️ Copying a Spell Scroll\n{commandPrefix}shop copy "character name" "spell name"', value="Copy a spell scroll into your character’s spellbook if they have access to one. See #marketplace-rules or the Bot Friend Player Commands Guide for more information.", inline=False)

    helpEmbedShop.add_field(name=f'▫️ Coating a Weapon in Silver or Adamantine\n{commandPrefix}shop silver "character name" "weapon name" #\n{commandPrefix}shop adamantine', value="Coat a specified number of one of your character’s weapons in silver or adamantine. If no number is specified then only one weapon will be coated.", inline=False)

    helpEmbedShop.add_field(name=f'▫️ Downtime Friend Training\n{commandPrefix}downtime training "character name"\n[{commandPrefix}dt training]', value="Have your character learn a language or gain proficiency in a tool (or a skill later on).", inline=False)

    helpEmbedShop.add_field(name=f'▫️ Downtime Noodle Training\n{commandPrefix}downtime noodle "character name"\n[{commandPrefix}dt noodle]', value="Have your character learn more languages or gain proficiency in more tools (or a skill later on) but only if you have a Noodle role.", inline=False)


# TP COMMANDS MENU ($help tp)

    helpEmbedTp.title = 'TP Commands'

    helpEmbedTp.add_field(name=f'▫️ Acquiring a Magic Item\n{commandPrefix}tp buy "character name" "magic item"', value="Put your character’s TP towards a magic item or purchase it with GP. See #after-a-quest or the Bot Friend Player Commands Guide for more information.", inline=False)

    helpEmbedTp.add_field(name=f'▫️ Discarding an Incomplete Magic Item\n{commandPrefix}tp discard "character name"', value="Discard your character’s incomplete magic item(s) that have partial TP towards them. You will permanently lose all of the TP that has been put towards the magic item(s).", inline=False)

    helpEmbedTp.add_field(name=f'▫️ Abandoning Leftover TP\n{commandPrefix}tp abandon "character name" tier', value="Abandon your character’s leftover TP in the tier of your choice.", inline=False)


# GUILD COMMANDS MENU ($help guild)

    helpEmbedGuild.title = 'Guild Commands'

    helpEmbedGuild.add_field(name=f'▫️ Viewing a Guild’s Information\n{commandPrefix}guild info #guild-channel', value="View the roster of a guild, the reputation in its bank and total, and its monthly and lifetime stats. If the guild has yet to be funded, it will instead display the amount of GP that it requires before it will be officially opened.", inline=False)

    helpEmbedGuild.add_field(name=f'▫️ Joining a Guild\n{commandPrefix}guild join "character name" #guild-channel', value="Join a guild with your character.", inline=False)

    helpEmbedGuild.add_field(name=f'▫️ Increasing Your Rank\n{commandPrefix}guild rankup "character name"', value="Increase the rank of your character in the guild that they are a member of.", inline=False)

    helpEmbedGuild.add_field(name=f'▫️ Leaving a Guild\n{commandPrefix}guild leave "character name"', value="Leave a guild that your character is a member of", inline=False)

    helpEmbedGuild.add_field(name=f'▫️ Creating a Guild\n{commandPrefix}guild create "character name" "guild name" @guildrole #guild-channel', value="Create a guild which will require funding in order to officially open. Your character will automatically join the guild as a result of creating it and will fund a minimum amount of GP equal to the joining fee of their tier.", inline=False)

    helpEmbedGuild.add_field(name=f'▫️ Funding a Guild\n{commandPrefix}guild fund "character name" "guild name" GP', value="Fund and join a newly-created guild which still requires funding with your character. The minimum amount of GP that you must fund is equal to the joining fee of your character’s tier.", inline=False)


# CAMPAIGN COMMANDS MENU ($help campaign)

# PLAYER CAMPAIGN COMMANDS

    helpEmbedCampaign.title = f"Campaign Commands\n{commandPrefix}c"

    helpEmbedCampaign.add_field(name=f'▫️ Viewing a Campaign’s Information\n{commandPrefix}campaign info #campaign-channel', value="View a campaign’s DM (Campaign Master), the number of sessions that the campaign has run, its active and inactive roster, the number of sessions that each player has participated in, and the hours that each player has accumulated.", inline=False)

    helpEmbedCampaign.add_field(name=f'▫️ Signing Up (Player)\n{commandPrefix}campaign timer signup', value="Sign up to a prepared timer but only if you have been selected to join the campaign session and were mentioned when the timer was prepared.", inline=False)

    helpEmbedCampaign.add_field(name=f'▫️ Adding Yourself (Player)\n{commandPrefix}campaign timer addme', value="Request permission to join the campaign session after it has already been started. The DM must approve the request.", inline=False)

    helpEmbedCampaign.add_field(name=f'▫️ Removing Yourself (Player)\n{commandPrefix}campaign timer removeme', value="Remove yourself from the running timer.", inline=False)

    helpEmbedCampaign.add_field(name=f'▫️ Checking the Timestamp (Player)\n{commandPrefix}timer removeme', value="Refresh the running timer’s information box.", inline=False)

    helpEmbedCampaign.add_field(name=f'▫️ Creating a Character with a Campaign Transfer\n{commandPrefix}create "character name" level "race" "class" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]" #campaign-channel XhYm', value="Create a character at a higher level than you normally can by transferring some or all of the time that you have accumulated throughout the campaign to the character during creation.", inline=False)

    helpEmbedCampaign.add_field(name=f'▫️ Creating a Multiclass Character with a Campaign Transfer\n{commandPrefix}create "character name" starting level "race" "class1 final level / class2 final level / [...]" "background" STR DEX CON INT WIS CHA "reward item1, reward item2, [...]" #campaign-channel XhYm', value="Create a multiclass character at a higher level than you normally can by transferring some or all of the time that you have accumulated throughout the campaign to the character during creation.", inline=False)


# DM CAMPAIGN COMMANDS

    helpEmbedCampaign.add_field(name=f'▫️ Creating a Campaign (DM)\n{commandPrefix}campaign create @campaignrole #campaign-channel', value="Create a campaign if you have the Campaign Master role and the campaign channel has been created.", inline=False)

    helpEmbedCampaign.add_field(name=f'▫️ Adding Players to a Campaign Roster (DM)\n{commandPrefix}campaign add @player #campaign-channel', value="Add a player to your campaign roster.", inline=False)

    helpEmbedCampaign.add_field(name=f'▫️ Removing Players from a Campaign Roster (DM)\n{commandPrefix}campaign remove @player #campaign-channel', value="Remove yourself from the running timer.", inline=False)

    helpEmbedCampaign.add_field(name=f'▫️ Preparing the Timer (DM)\n{commandPrefix}campaign timer prep "@player1, @player2,#player3, [...]" sessionname', value="Prepare a timer with a list of players who will be participating in the session. If no session name is given, it defaults to the name of the channel. Any member of a campaign can use this command (as well all subsequent commands) to host a campaign session.", inline=False)

    helpEmbedCampaign.add_field(name=f'▫️ Adding Players During a Session (DM)\n{commandPrefix}campaign timer add @player', value="Add a player to the roster after you have already prepared the timer so they can sign up or add them to the running timer.", inline=False)

    helpEmbedCampaign.add_field(name=f'▫️ Removing Players During a Session (DM)\n{commandPrefix}campaign timer remove @player', value="Remove a player from the roster after you have already prepared the timer so they can sign up or remove them from the running timer.", inline=False)

    helpEmbedCampaign.add_field(name=f'▫️ Cancelling the Timer (DM)\n{commandPrefix}campaign timer cancel', value="Cancel the prepared timer.", inline=False)

    helpEmbedCampaign.add_field(name=f'▫️ Starting the Timer (DM)\n{commandPrefix}campaign timer start', value="Start the prepared timer.", inline=False)

    helpEmbedCampaign.add_field(name=f'▫️ Stopping the Timer (DM)\n{commandPrefix}campaign timer stop', value="Stop the running timer which creates a session log for it.", inline=False)

    helpEmbedCampaign.add_field(name=f'▫️ Submitting a Campaign Log (DM)\n{commandPrefix}campaign log gameID summary ', value="Submit a campaign log summary for the running timer which you just stopped. See #campaign-rules or the Bot Friend DM Commands Guide for more information.", inline=False)




    numPages = len(helpList)

    for i in range(0, len(helpList)):
        helpList[i].set_footer(text= f"Page {i+1} of {numPages}")

    helpMsg = await ctx.channel.send(embed=helpList[page])
    if page == 0:
        for num in range(0,numPages-1): await helpMsg.add_reaction(numberEmojis[num])

# THIS ERROR MESSAGE WILL NEED TO BE CHANGED TO ACCOMMODATE THE NEW COMMANDS.
    try:
        hReact, hUser = await bot.wait_for("reaction_add", check=helpCheck, timeout=30.0)
    except asyncio.TimeoutError:
        await helpMsg.edit(content=f"Your help menu has timed out! I'll leave this page open for you. Use the first command if you need to cycle through help menu again or use any of the other commands to view a specific help menu:\n```yaml\n{commandPrefix}help gen\n{commandPrefix}help char\n{commandPrefix}help timer1\n{commandPrefix}help timer2\n{commandPrefix}help timer3\n{commandPrefix}help shop\n{commandPrefix}help tp\n{commandPrefix}help guild\n{commandPrefix}help campaign```")
        await helpMsg.clear_reactions()
        await helpMsg.add_reaction('💤')
        return
    else:
        await helpMsg.edit(embed=helpList[int(hReact.emoji[0])])
        await helpMsg.clear_reactions()


if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
        try:
            bot.load_extension(cogs_dir + "." + extension)
        except (discord.ClientException, ModuleNotFoundError):
            print(f'Failed to load extension {extension}.')
            traceback.print_exc()

bot.run(token)
