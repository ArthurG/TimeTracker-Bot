from sheetFunctions import *  # calls all the functions I coded to access and modify the spreadsheet.

import discord  # for discord API access
from discord.ext import commands
import asyncio
import json
import tempfile
from io import BytesIO

import datetime  # time parser

version = "1.3"

with open('config.txt') as json_file:
    data = json.load(json_file)

    prefix = data['prefix']
    description = data['description'] + version
    token = data['token']  # token of the bot
    botActivity = data['botActivity'] + version
    colour = int(data['color'])
    timezoneoffset = int(data['timezoneoffset'])  # time offset (difference in second to greenwich time/GMT)
    timeout = float(data['timeout'])

# calculates the hour display based on the timezone :
hourout = timezoneoffset/3600
if hourout < 0:
    stringTimeOffset = str(hourout)
else:
    stringTimeOffset = str(f"+{hourout}")


bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix), description=description)
bot.remove_command('help')

# DISCORD #


@bot.event  # when the bot is connected and ready to run commands.
async def on_ready():
    print(f"Timetracker bot version {version}")
    print('Logged in successfully !')
    print(f"Bot username : {bot.user.name}")
    print(f"Bot id : {bot.user.id}")
    await bot.change_presence(activity=discord.Game(name=botActivity))
    print('------')


@bot.command(name='ping', aliases=["p", "pong", "pingpong"])
async def ping(ctx):
    """
    a simple ping command used to check if the bot is online
    """
    embed = discord.Embed(title="PONG :ping_pong: ", description="I'm online ! :signal_strength:", colour=colour, timestamp=datetime.datetime.utcnow())
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.set_footer(text=bot.user.name + ' - requested by ' + str(ctx.author), icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed)
    log(f"{str(ctx.author)} pinged the bot.")


@bot.command(name="help", aliases=["h", "aide", "commands"])
async def help(ctx):
    """
    displays the list of available commands
    """
    embed = discord.Embed(title="HELP :question:", description="The list of all available commands !", colour=colour, timestamp=datetime.datetime.utcnow())
    embed.add_field(name='Information commands :closed_book:', value=f'''**{prefix}ping** : check if the bot is up and fonctional
    **{prefix}help** : displays this message
    **{prefix}about** : displays informations about the bot
    **{prefix}activity** (or {prefix}a) : adds an activity. `Syntax : !a [label][dateStart*][hourStart*][dateEnd*][hourEnd] (* = optional)`''', inline=False)
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.set_footer(text=bot.user.name + ' - requested by ' + str(ctx.author), icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed)
    log(f"{str(ctx.author)} asked for help about the bot.")


@bot.command(name="about", aliases=["info", "i", "information", "informations"])
async def about(ctx):
    """
    displays informations about the Bot
    """
    embed = discord.Embed(title="ABOUT :information_source:", description="Informations about the bot", colour=colour, timestamp=datetime.datetime.utcnow())
    embed.add_field(name="Bot info", value=bot.user.name + " version " + version, inline=False)
    embed.add_field(name="Creator info", value="created by HerbeMalveillante#0252.\nhttps://github.com/HerbeMalveillante\nhttps://herbemalveillante.itch.io/", inline=False)
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.set_footer(text=bot.user.name + " - requested by "+str(ctx.author), icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed)
    log(f'{str(ctx.author)} asked for informations about the bot')


@bot.command(name="activity", aliases=["a"])
async def activity(ctx, *, activityText=None):
    # adding the activity and keeping the id in memory for eventual deletion
    epoch = analyzeUserEntry(activityText)
    activityObj = Activity(epoch[0], epoch[1], epoch[2])
    id = activityObj.id

    embed = discord.Embed(title=":art: Activity added !", description=f"Click on the reaction within {timeout}s to cancel :put_litter_in_its_place:", colour=colour, timestamp=datetime.datetime.utcnow())
    embed.add_field(name=":label: Label :", value=f"`{activityObj.label}`", inline=False)
    try:
        datestartGMT = datetime.datetime.utcfromtimestamp(activityObj.startDate + timezoneoffset)
        dateendGMT = datetime.datetime.utcfromtimestamp(activityObj.endDate + timezoneoffset)
    except:
        datestartGMT = "Error !"
        dateendGMT = "Error !"
    embed.add_field(name=":hourglass_flowing_sand: Start time :", value=f"`{activityObj.startDate}` ({datestartGMT} GMT{stringTimeOffset})", inline=False)
    embed.add_field(name=":hourglass: End time : ", value=f"`{activityObj.endDate}` ({dateendGMT} GMT{stringTimeOffset})", inline=False)
    embed.add_field(name=":floppy_disk: Id : ", value=f"`{activityObj.id}`", inline=False)
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.set_footer(text=bot.user.name + " - requested by "+str(ctx.author), icon_url=ctx.author.avatar_url)

    message = await ctx.send(embed=embed)

    addActivity(activityObj)

    # message = await ctx.send("Hello, please click the reaction within 60 seconds")
    await message.add_reaction("🚮")
    def check(r,u):
        return u.id == ctx.author.id and r.message.channel.id == ctx.channel.id and str(r.emoji) == "🚮"
    try:
        reaction, user = await bot.wait_for("reaction_add", check=check, timeout=timeout)
    except asyncio.TimeoutError:
        log(f"The delay to delete the activity of ID {id} has expired")
        return
    else:
        if str(reaction.emoji == "🚮"):
            delActivity(id)

            embed = discord.Embed(title=":put_litter_in_its_place: Entry deleted !", description=f"entry id : {id}")
            embed.add_field(name=":question: Why was my entry incorrect ?", value=f"If your entry displayed errors in its fields, it may be because you did not respect the exact syntax (no spaces between date and month / hours in format 11:20AM). Please contact me ({prefix}about command) if you can't find why isn't your command working.", inline=False)
            embed.set_thumbnail(url=bot.user.avatar_url)
            embed.set_footer(text=bot.user.name + " - requested by "+str(ctx.author), icon_url=ctx.author.avatar_url)

            return await ctx.send(embed=embed)


@bot.command(name="activitylist", aliases=["activityList", "al", "AL", "ActivityList"])
async def activitylist(ctx, days=7):
    activitytime = activitiesList(days)
    embed = discord.Embed(title=f"Activity list for the past {days} days :", description="the 15 most popular activites are displayed. Click on the reaction to get a file with the complete list.", colour=colour, timestamp=datetime.datetime.utcnow())

    stringActTime = ""
    for i in range(len(activitytime)):
        stringActTime += str(i+1)+ " : " + activitytime[i][0] + " - " + secondConverter(activitytime[i][1]) + "\n"

    buffer = BytesIO(stringActTime.encode("utf8"))

    for i in range(len(activitytime)):
        if i < 15:
            stringDesc = ""
            stringDesc += f"`{secondConverter(activitytime[i][1])}` spent"
            embed.add_field(name=f"{i+1} - {activitytime[i][0]}", value=stringDesc, inline=False)
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.set_footer(text=bot.user.name + " - requested by "+str(ctx.author), icon_url=ctx.author.avatar_url)

    message = await ctx.send(embed=embed)

    await message.add_reaction("📁")
    def check(r, u):
        return u.id == ctx.author.id and r.message.channel.id == ctx.channel.id and str(r.emoji) == "📁"
    try:
        reaction, user = await bot.wait_for("reaction_add", check=check, timeout=timeout)
    except asyncio.TimeoutError:
        log("The delay to download the file has expired")
        return
    else:
        if str(reaction.emoji == "📁"):



            return await ctx.send("", file = discord.File(fp=buffer, filename="activitylist.txt"))


bot.run(token)  # Any line below this will run if the bot crashes completely (very unlikely to happen but still).
log("Oops, the bot crashed... Discord servers may have issues right now.")
