# Logging
# import os; os.chdir(os.path.dirname(__file__))
import logging

with open("latest.log", "w") as f: pass

logging.basicConfig(
    level=logging.DEBUG,
    filename="latest.log",
    format="[%(levelname)s]: %(message)s"
)
logging.debug("1.4.0.2")

# Imports
logging.debug("Importing...")
import discord
import os
import sys
import certifi
import re
import asyncio
import random
import math
import time as mtime
import requests
import motor.motor_asyncio
import colorsys
import traceback

from jokeapi import Jokes
from bson.objectid import ObjectId
from random import randint, choice
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv
from decimal import Decimal

try:
    import ujson as json

except (ModuleNotFoundError, ImportError):
    try:
        import simplejson as json

    except (ModuleNotFoundError, ImportError):
        import json

logging.debug("Loading environment...")
load_dotenv()

# Getting run mode
logging.debug("Asking for mode and parsing...")
list = [
    "Debug",
    "Regular"
]
list2 = [item[0].upper() for item in list]
mode = str(
    input(
        "".join(
            [
                f"[{item[0].upper()}]{item} " for item in list
            ]
        )
    )
)[0].upper()
if mode not in list2:
    print("Invalid mode.")
    sys.exit()

# MongoDB twash
logging.debug("Defining MongoDB Constants...")
client = motor.motor_asyncio.AsyncIOMotorClient(
    str(
        os.getenv(
            "MON_STRING"
        )
    ),
    tlsCAFile=certifi.where()
)
db = client["CRBOT2Dat"]
warnsc = db["warns"]
pointsc = db["points"]
countsc = db["count"]
snipesc = db["snipes"]

pointsid = "620cfe72f63ae0339129c774"
warnid = "000000000000000000010f2c"
countid = "625da77a041a143613c03918"
snipeid = "62858c9d61724b7e6d4c8be8"
esnipeid = "628644be441599814d71a07a"
emojismade = False

msgst = {}
# Endpoints: https://kawaii.red/api/gif/endpoints/token=token/

kawaiit = str(os.getenv("KAWAII"))

# Regexes
logging.debug("Defining regexes...")
mentionre = re.compile(r"(.*<@[0-9]+>.*)|(.*<@![0-9]+>.*)")
iUAT = re.compile(r".*# [0-9]{4}")
iRPr = re.compile(r"[0-9]+d[0-9]+")
gifSwear = re.compile(r"(https?\:\/\/tenor\.com\/view\/.+)|(https\:\/\/giphy\.com\/gifs\/.+)")

# stuff
logging.debug("Defining bot constants...")
intents = discord.Intents.all()
pf = "-"
bot = commands.Bot(
    command_prefix=pf,
    strip_after_prefix=True,
    intents=intents
)
with open("dat.json", "r") as f:
    # Load crap from data file
    logging.debug("Loading from JSON datafile...")
    yeetus = json.loads(f.read())
    curselist = yeetus["curses"]
    answers = yeetus["8ball"]
    quoteslist = yeetus["quotes"]
    no_ulist = yeetus["no u"]
    ruleslist = yeetus["rules"]
    faqlist = yeetus["faq"]

    del yeetus

proxyv = False

isSwear = r"\|\|" + ("((.*" + ".*)|(.*".join(curselist) + ".*))+") + r"\|\|"
# print(isSwear)
isSwear = re.compile(isSwear)
globalCD = 2

# events

@bot.event
async def on_ready():
    # logged in?
    logging.debug("call: on_ready()")
    print(f"Gleipnir has logged on in to Discord as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="with Cuboid's brain cells"))

@bot.event
async def on_member_join(member):
    # Ooh someone joined
    logging.debug("call: on_member_join()")
    try:
        embed = discord.Embed(
            title=f"Thank you for joining Cuboid's Café!",
            description="""Hello there!
This is an automated message.:robot:
I am **Gleipnir**, the bot made by **Cuboid_Raptor#7340**.
I have DM'd you to say, welcome to Cuboid's Café!:coffee:
I sincerely hope you have a great time in the server!:laughing:
You can also interact with me in the server, do be sure to use slash commands,
I have loads of weird things. Need a sarcastic joke with hints of dark humour? `/joke`.
Want to slap someone with an anime GIF? `/slap`.
You can see a full list when you type `/`, but I digress.
Basically, have fun!

Or I will slap you.


Really hard."""
        )
        embed.set_image(url=kawaii("happy"))

        await member.send(
            embed=embed
        )
    except discord.errors.HTTPException:
        logging.warning("HTTPException when DMing new user")

    channel = get(member.guild.text_channels, id=885689981119647764)

    embed = discord.Embed(
        title=f"{member.mention} has joined!",
        description="yay and stuff"
    )
    embed.set_image(url=kawaii("wave"))

    await channel.send(f"*{member.mention} is here! We hope you have a nice time here, {member.mention}!*")
    await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    # oof someone left :'(
    logging.debug("call: on_member_remove()")

    embed = discord.Embed(
        title=f"Oh no! {member.mention} has left.",
        description="\\:'\\("
    )
    embed.set_image(url=kawaii("cry"))

    channel = get(member.guild.text_channels, id=885689981119647764)
    await channel.send(
        f"*{member.mention} has left. Goodbye, {member.mention}*",
        embed=embed
    )

@bot.listen("on_message")
async def on_message_listener(message):
    # When someone messages
    logging.debug("call: on_message()")
    if message.author == bot.user:
        # Is the bot messaging.
        return

    if message.channel.id == 955239604007628820:
        # Is message in count channel?
        tempd = await countsc.find_one(
            {
                "_id": ObjectId(countid)
            }
        )

        if (message.content != str(tempd["num"])) or (message.author.id == tempd["lastid"]):
            # Incorrect message.
            await message.delete()
            await message.author.send(random.choice(no_ulist) + random.choice(["", "."]))

        else:
            # Correct message.
            tempd["num"] += 1
            tempd["lastid"] = message.author.id

            await countsc.replace_one(
                {
                    "_id": ObjectId(countid)
                },
                tempd,
                upsert=True
            )

    else:
        # Not in count channel? Is it in announcements or no category?
        temp = message.channel.category
        if (not temp) or (temp.id == 885897220707205210):
            # No category or announcements.
            pass

        else:
            if random.randint(1, 1000) <= 1:
                await message.channel.send("r/woosh", reference=message)

    if "c%diagnostics%" in message.content:
        # diagnostics
        await message.channel.send("testing... 1 2 3 testing...")

    if gifSwear.search(message.content) == None:
        tingy = isSwear.sub("", str(message.content).lower().replace("```brainfuck", "```bf"))
        if message.channel.id != 976592452997750795:
            for word in curselist:
                if word in tingy:
                    # you swore, idot.
                    print("somebody swore uh oh")
                    await message.channel.send(f"Don't swear, {message.author.mention}")
                    return

    if ((bot.user.name in message.content) or ((str(bot.user.id) + ">") in message.content)) and not message.content.startswith(str("/")) and ("announcements" not in message.channel.name.lower()):
        # Did you say bot name?
        if message.channel.id != 955239604007628820:
            await message.channel.send("Hello there, I heard my name?")

    if (message.channel.id != 976592452997750795) and (message.channel.id != 955239604007628820):
        try:
            dif = mtime.time() - msgst[message.author.id]

        except KeyError:
            dif = 2 # Could be any number >1

        if dif > 1:
            tempd = await pointsc.find_one(
                {
                    "_id": ObjectId(pointsid)
                }
            )

            try:
                tempd[str(message.author.id)] += 10

            except KeyError:
                tempd[str(message.author.id)] = 10

            await pointsc.replace_one(
                {
                    "_id": ObjectId(pointsid)
                },
                tempd,
                upsert=True
            )

            msgst[message.author.id] = mtime.time()

    if message.channel.id == 991059083018772480:
        try:
            await message.delete()

        except Exception as error:
            logging.error(f"`await message.delete()` Error: {type(error).__name__}: {str(error)}")

        try:
            await message.author.send("You have been kicked because you were captured by the bot trap. If you aren't a bot, I don't even know what to say.")

        except Exception as error:
            logging.error(f"`await message.author.send(...)` Error: {type(error).__name__}: {str(error)}")

        await message.author.kick(reason="Bot Trap")

    if proxyv:
        if isCuboid(message):
            temp = message.content
            await message.delete()
            await message.channel.send(temp)
            del temp

@bot.event
async def on_message_delete(message):
    #Snipe log
    if not message.author.bot:
        tempd = await snipesc.find_one(
            {
                "_id": ObjectId(snipeid)
            }
        )
        tempd[str(message.channel.id)] = [message.content, message.author.id, message.id, message.created_at.hour, message.created_at.minute]
        await snipesc.replace_one(
            {
                "_id": ObjectId(snipeid)
            },
            tempd,
            upsert=True
        )

@bot.event
async def on_message_edit(message_before, message_after):
    #Esnipe log
    if not message_before.author.bot:
        tempd = await snipesc.find_one(
            {
                "_id": ObjectId(esnipeid)
            }
        )
        tempd[str(message_before.channel.id)] = [message_before.content, message_after.content, message_before.author.id, message_before.id, message_before.created_at.hour, message_before.created_at.minute]
        await snipesc.replace_one(
            {
                "_id": ObjectId(esnipeid)
            },
            tempd,
            upsert=True
        )

if mode != "D":
    @bot.event
    async def on_application_command_error(ctx, error, prefixed=False):
        # Oof something went wrong
        if ctx.channel.id == 955239604007628820:
            logging.error(str(error))
            return

        if isinstance(error, discord.ext.commands.errors.CommandNotFound):
            embed = discord.Embed(
                title="Error",
                description="Unknown Command",
                color=discord.Color.red()
            )
            if prefixed:
                await ctx.send(embed=embed)

            else:
                await ctx.followup.send(embed=embed)

        elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            embed = discord.Embed(
                title="Error",
                description="You're missing an argument!",
                color=discord.Color.red()
            )
            if prefixed:
                await ctx.send(embed=embed)

            else:
                await ctx.followup.send(embed=embed)

        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Error",
                description="Insufficient permissions!",
                color=discord.Color.red()
            )
            if prefixed:
                await ctx.send(embed=embed)

            else:
                await ctx.followup.send(embed=embed)

        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Error",
                description=f"Command still on cooldown! Wait a few seconds to use this command!",
                color=discord.Color.red()
            )
            if prefixed:
                await ctx.send(embed=embed)

            else:
                await ctx.followup.send(embed=embed)

        else:
            embed = discord.Embed(
                title="Error",
                description=str(error),
                color=discord.Color.red()
            )
            embed.set_footer(text="Is this a bug? Report it to help make this dipsh- I mean, bot, better!")

            if prefixed:
                await ctx.send(embed=embed)

            else:
                await ctx.followup.send(embed=embed)

    @bot.event
    async def on_command_error(ctx, error):
        await on_application_command_error(ctx, error, prefixed=True)

# Functions
def d(n):
    # precision
    logging.debug("call: d()")
    return Decimal(str(n))

def bround(n, a=0):
    # better rounding
    logging.debug("call: bround()")
    if a == 0:
        return int(round(d(str(n)), a))

    else:
        return float(round(d(str(n)), a))

def g_role(ctx, rname):
    # Checks if ctx.author has any one of the roles in [rname]
    logging.debug("call: g_role()")
    role_t = []
    for item in rname:
        role_t.append(get(ctx.guild.roles, name=str(item)) in ctx.author.roles)

    out = role_t[0]
    for item in role_t[1:]:
        out = out or item

    return out

def isCuboid(ctx):
    # Is message author in ctx me (Cuboid)?
    logging.debug("call: isCuboid()")
    if ctx.author.id == 588132098875850752:
        return True

    else:
        return False

def isMention(text):
    # Is text a mention?
    logging.debug("call: isMention()")
    global mentionre
    return mentionre.match(text) != None

def idFromMention(mention):
    # Get User ID from mention
    logging.debug("call: idFromMention()")
    if mention.startswith("<@!"):
        return str(mention)[3:-1]

    else:
        return str(mention)[2:-1]

def isGP2(text):
    # Is text Gleipnir
    logging.debug("call: isGP2()")
    text = text.strip()
    if (text == str(bot.user.name)) or (text == str(bot.user)) or (text == "<@" + str(bot.user.id) + ">") or (text == "<@!" + str(bot.user.id) + ">"):
        return True

    else:
        return False

def isUserAndTag(text):
    # Checks if the string contains a username and tag
    logging.debug("call: isUserAndTag()")
    global iUAT
    if iUAT.match(text.strip()) == None:
        return False

    else:
        if len(text.split("# ")) != 2:
            return False

        else:
            return True

def isEmpty(text):
    # Checks if string is empty
    logging.debug("call: isEmpty()")
    if text == "" or text.isspace():
        return True

    else:
        return False

def reasonRet(arr):
    # Returns reason from *args
    logging.debug("call: reasonRet()")
    reason = "".join(arr)

    if isEmpty(reason):
        reason = "no good reason at all"

    return reason

def rollParse(string):
    # Parses roll number
    logging.debug("call: rollParse()")
    global iRPr
    if iRPr.match(string) == None:
        return False

    elif len(string.lower().split("d")) != 2:
        return False

    else:
        return string.lower().split("d")

def numform(n, a=0):
    # Adds commas and round number.
    logging.debug("call: numform()")
    return "{:,}".format(bround(float(n), a))

def containsEveryone(message):
    # Check if message contains @everyone pings.
    logging.debug("call: containsEveryone()")
    return ("@everyone" in message) or ("@here" in message)

def kawaii(sub):
    # Gets GIF from kawaii.red
    logging.debug("call: kawaii()")
    r = requests.get(f"https://kawaii.red/api/gif/{sub}/token={kawaiit}/")
    return str(r.json()['response'])

def fullName(author):
    # Returns name + tag from user/Member object
    logging.debug("call: fullName()")
    return author.name + "# " + author.discriminator

async def err(
    ctx,
    msg,
    clr=(
        255,
        7,
        1
    ),
    title="Error"
):
    embed = discord.Embed(
        title=title,
        description=str(msg),
        color=discord.Color.from_rgb(*clr)
    )
    await ctx.followup.send(embed=embed)
    logging.error(msg)

def prod(n):
    p = 1
    for i in n:
        p *= i

    return p

# Commands
@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def ping(ctx):
    """pings, this is just for tests"""
    logging.debug("call: ping()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    await ctx.followup.send("pong")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def killgp2(ctx):
    """Kills Gleipnir. Only Cuboid_Raptor# 7340 can run this command."""
    logging.debug("call: killgp2()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    if isCuboid(ctx):
        # r u me?
        try:
            await ctx.followup.send("OH FRICK NO MY FREE TRIAL OF LIFE EXPIRED")

        except discord.errors.NotFound:
            logging.warning("Interaction likely failed when running killswitch, ignoring...")

        print("Closing...")
        sys.exit()

    else:
        await err(
            ctx,
            "Why are you trying to kill me? :(",
            clr=(89, 10, 1),
            title="Rude."
        )

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def no_u(ctx, person):
    """No you, people."""
    logging.debug("call: no_u()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    if containsEveryone(person):
        await ctx.followup.send(f"***\\*GASP\\****")

    elif isGP2(person):
        await ctx.followup.send(f"I have been vaccinated against no-u's.")

    else:
        await ctx.followup.send(f"No u, {person}")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def magic8ball(ctx, *, question):
    """Magic 8ball. Ask it questions."""
    logging.debug("call: magic8ball()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    question = "".join(question)
    global answers
    await ctx.followup.send(f"In response to question \"{question}\":\n" + choice(answers))

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def quote(ctx):
    """Draws from my quotesbook and prints in chat."""
    logging.debug("call: quote()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    global quoteslist
    await ctx.followup.send(choice(quoteslist))

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def shoot(ctx, person):
    """Shoot people. Idk y."""
    logging.debug("call: shoot()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    if isMention(person):
        if int(ctx.author.id) == int(idFromMention(person)):
            await ctx.followup.send("Aw c'mon, don't kill yourself.")
            return

    else:
        if person.strip() == ctx.author.name:
            await ctx.followup.send("Aw c'mon, don't kill yourself.")
            return

    if ("@everyone" in person) or ("@here" in person):
        await ctx.followup.send("Mass genocide isn't allowed yet. Try again later.")
        return

    if isGP2(person):
        await ctx.followup.send("I pull out a handheld CIWS and shoot you. Who's the shooter now?")
        return

    if isMention(person):
        person = await bot.fetch_user(int(idFromMention(person)))
        person = person.name

    embed = discord.Embed(
        title=f"{ctx.author.name} has shot {person}!",
        description="oof",
    )
    embed.set_image(url=kawaii("shoot"))

    await ctx.followup.send(embed=embed)

@bot.slash_command(guild_ids=[885685555084554294])
@commands.has_guild_permissions(kick_members=True)
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def warn(ctx, person, *, reason):
    """Warn people."""
    logging.debug("call: warn()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    if isGP2(person):
        await ctx.followup.send("I HAVEN'T DONE ANYTHING!")

    else:
        if not isMention(person):
            await err(ctx, f"That person is not a mention.")

        else:
            reason = reasonRet(reason)

            tempd = await warnsc.find_one(
                {
                    "_id": ObjectId(warnid)
                }
            )
            try:
                tempd[str(person)] += 1

            except KeyError:
                tempd[str(person)] = 1

            await warnsc.replace_one(
                {
                    "_id": ObjectId(warnid)
                },
                tempd,
                upsert=True
            )

            await ctx.followup.send(f"{person} has been warned by {ctx.author.mention} for {reason}!")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.has_guild_permissions(kick_members=True)
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def rmwarn(ctx, person, *, reason):
    """Remove warn from people."""
    logging.debug("call: rmwarn()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    if isGP2(person):
        await ctx.followup.send("I haven't been warned yet. I wouldn't warn myself.")

    else:
        if not isMention(person):
            await err(ctx, f"That person is not a mention.")

        else:
            reason = reasonRet(reason)

            tempd = await warnsc.find_one(
                {
                    "_id": ObjectId(warnid)
                }
            )
            try:
                tempd[str(person)] -= 1
                if tempd[str(person)] < 0:
                    tempd[str(person)] = 0

                    await err(ctx, f"{person} doesn't have any warns.")
                    return

            except KeyError:
                await err(ctx, f"{person} doesn't have any warns.")
                return

            await warnsc.replace_one(
                {
                    "_id": ObjectId(warnid)
                },
                tempd,
                upsert=True
            )

            await ctx.followup.send(f"A warn has been removed from {person} by {ctx.author.mention} for {reason}!")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def warns(ctx, person):
    """Shows warns of people"""
    logging.debug("call: warns()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    if not isMention(person):
        await err(ctx, f"That person is not a mention.")

    else:
        tempd = await warnsc.find_one(
            {
                "_id": ObjectId(warnid)
            }
        )
        out = str(tempd[str(person)])
        if not bool(int(out) - 1):
            await ctx.followup.send(f"{person} has " + out + " warn!")

        else:
            await ctx.followup.send(f"{person} has " + out + " warns!")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def warnclear(ctx):
    """Clears all warns globally. Only Cuboid_Raptor# 7340 can run this command."""
    logging.debug("call: warnclear()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    if isCuboid(ctx):
        tempd = {
            "_id": ObjectId(warnid)
        }
        await warnsc.replace_one(
            {
                "_id": ObjectId(warnid)
            },
            tempd,
            upsert=True
        )
        await ctx.followup.send("All global warns have been cleared.")
        print("All global warns have been cleared.")

    else:
        await err(ctx, "You don't have the proper permissions to run this command.")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def roll(ctx, roll):
    """Roll die."""
    logging.debug("call: roll()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    if not rollParse(roll):
        await err(ctx, "That isn't a valid dice to roll.")

    else:
        proll = rollParse(roll)
        proll[0], proll[1] = proll[0].replace(",", ""), proll[1].replace(",", "")

        if (int(proll[0]) > 32767) or (int(proll[1]) > 32767):
            await ctx.followup.send(f"Your roll is too big, my server will explode")
            return

        s = 0
        try:
            for i in range(0, int(proll[0])):
                s += random.randint(1, int(proll[1]))

            await ctx.followup.send(f"{ctx.author.mention} rolled {roll} and got {s}")

        except ValueError:
            await err(ctx, "That isn't a valid roll.")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def ship(ctx, person, person2=None):
    """Ship ship ship"""
    logging.debug("call: ship()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    if person2 == None:
        person2 = ctx.author.mention

    if isGP2(person) or isGP2(person2):
        await ctx.followup.send("bruh why")

    else:

        personn, person2n = person, person2
        if isMention(person):
            personn = int(idFromMention(personn))

        else:
            try:
                personn = int(personn)

            except ValueError:
                personn = prod([ord(i) for i in personn])

            personn = personn % 1000000000000000000

        if isMention(person2):
            person2n = int(idFromMention(person2n))

        else:
            try:
                person2n = int(person2n)

            except ValueError:
                person2n = prod([ord(i) for i in person2n])

            person2n = person2n % 1000000000000000000

        perc = (abs(personn - person2n) + 100) % 101

        string = f"{person} x {person2} ship compatibility percentage: {perc}%"
        if perc < 10:
            compat = "Terrible. :("

        elif perc >= 10 and perc < 25:
            compat = "Pretty Bad."

        elif perc >= 25 and perc < 50:
            compat = "Meh."

        elif perc == 69:
            compat = "( ͡° ͜ʖ ͡°)"

        elif perc >= 50 and perc < 75:
            compat = "Okay."

        elif perc >= 75 and perc < 90:
            compat = "Pretty Good!"

        else:
            compat = "Amazing!"

        n1 = bround(perc / 10)
        n2 = bround(10 - n1)
        await ctx.followup.send(
            "\n".join(
                [
                    string,
                    f"\\|" + "".join(
                        [
                            "▓" for i in range(
                                0,
                                n1
                            )
                        ]
                    ) + "".join(
                        [
                            " " for i in range(
                                0,
                                n2 * 3
                            )
                        ]
                    ) + "\\|",
                    f"Compatibility score: {compat}"
                ]
            )
        )

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def points(ctx, user=None, silent=False):
    """Show number of points of others, or yourself."""
    logging.debug("call: points()")
    if ctx.channel.id == 955239604007628820:
        return

    if not silent:
        await ctx.defer()

    if user == None:
        isSelf = True
        user = ctx.author.id

    elif not isMention(user):
        if not silent:
            await err(ctx, "That person isn't a mention.")

        else:
            logging.info("That person isn't a mention (callback from points())")

        return

    else:
        isSelf = False
        user = idFromMention(user)

    tempd = await pointsc.find_one(
        {
            "_id": ObjectId(pointsid)
        }
    )

    try:
        out = f"{tempd[str(user)]} cp"

    except KeyError:
        out = "0 points"

    if not silent:
        if isSelf:
            await ctx.followup.send("You have " + out)

        else:
            temp = await bot.fetch_user(user)
            await ctx.followup.send(f"{temp.name} has " + out)
            del temp

    else:
        return tempd[str(user)]

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def leaderboard(ctx):
    """Leaderboard function for points."""
    logging.debug("call: leaderboard()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    global output, thingy
    tempd = await pointsc.find_one(
        {
            "_id": ObjectId(pointsid)
        }
    )
    del tempd["_id"]
    thingy = [[k, v] for k, v in tempd.items()]
    thingy = sorted(thingy, key=lambda x: x[1])[::-1]
    places = []

    for item in thingy:
        places.append(item[0])

    output = ""
    async def add(a, n):
        global output, thingy
        try:
            try:
                temp = await bot.fetch_user(thingy[n][0])

            except discord.errors.NotFound:
                del thingy[n]
                await add(a, n)
                return

            if temp.bot:
                del thingy[n]
                await add(a, n)
                return

            output += f"{str(a) + str(temp.name)} - {str(thingy[n][1])} cp\n"
            del temp
            return 0

        except KeyError as error:
            logging.debug("Error occured in leaderboard.add(), could be incomplete leaderboard")
            logging.warning(f"{type(error).name}: {str(error)}")

    if not await add("🥇", 0):
        if not await add("🥈", 1):
            if not await add("🥉", 2):
                if not await add("🏵️", 3):
                    await add("🏵️", 4)

    curp = await points(ctx, silent=True)
    curp = int(curp)

    try:
        yay = "#" + str(places.index(str(ctx.author.id)) + 1)

    except ValueError:
        yay = "Last"

    output += f"{ctx.author.name} - {curp} cp (Place " + yay + ")"

    await ctx.followup.send(output)

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def givepoints(ctx, person, point):
    """Give points to others."""
    logging.debug("call: give()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    point = bround(point)

    tempd = await pointsc.find_one(
        {
            "_id": ObjectId(pointsid)
        }
    )

    if not isMention(person):
        await err(ctx, "That person isn't a mention.")
        return

    hasp = await points(ctx, silent=True)

    if hasp < point:
        await err(ctx, "You cannot afford to send that many Cuboid Points.")
        return

    tempd[str(ctx.author.id)] -= int(point)

    if tempd[str(ctx.author.id)] < 0:
        logging.error("PANIC!!!!! CALCULATIONS DON'T MAKE SENSE")
        raise ValueError("WTF")
        return

    try:
        tempd[str(idFromMention(person))] += int(point)

    except KeyError:
        tempd[str(idFromMention(person))] = int(point)

    await pointsc.replace_one(
        {
            "_id": ObjectId(pointsid)
        },
        tempd,
        upsert=True
    )

    await ctx.followup.send(f"{point} cp have been sent to {person}!")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def coinflip(ctx):
    """Flip a coin, 'cuz why not."""
    logging.debug("call: coinflip()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    if random.randint(0, 1):
        await ctx.followup.send("You flipped a coin and got heads!")

    else:
        await ctx.followup.send("You flipped a coin and got tails!")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def joke(ctx):
    """Prints a random corny joke."""
    logging.debug("call: joke()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    j = await Jokes()
    jk = {}

    while jk == {}:
        jk = await j.get_joke(
            blacklist=[
                "nsfw",
                "racist",
                "sexist"
            ]
        )

    if jk["type"] == "single":
        await ctx.followup.send(jk["joke"])

    else:
        jsetup = await ctx.followup.send(jk["setup"])
        await asyncio.sleep(1)
        await jsetup.edit(jk["setup"] + "\n" + jk["delivery"])

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def color(ctx, hexcode):
    """Display a hex code colour."""
    logging.debug("call: color()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    ohex = str(hexcode).upper()
    hexcode = ohex.lstrip("\\").lstrip("# ").lower()

    if len(hexcode) != 6:
        await err(ctx, "An error occured, and your hex code could not be processed.")
        logging.warning("Invalid hexcode.")
        return

    try:
        temp = int(hexcode, 16)
        del temp

    except ValueError:
        await err(ctx, "That isn't a valid hex code.")
        return

    if hexcode == "ffffff":
        hexcode = "fffeff"

    elif hexcode == "000000":
        hexcode = "000001"

    ohex = ohex.lstrip("\\").lstrip("#").lstrip(" ")

    ohex = "\\#" + ohex

    # RGB
    yee = tuple(
        int(
            hexcode[i:i+2],
            16
        ) for i in (
            0,
            2,
            4
        )
    )
    rgb2 = tuple(
        int(
            ohex[2:][i:i+2],
            16
        ) for i in (
            0,
            2,
            4
        )
    )

    # CMYK
    cmyk = (0, 0, 0, 100)
    if rgb2 == (0, 0, 0):
        pass

    else:
        c = 1 - rgb2[0] / 255
        m = 1 - rgb2[1] / 255
        y = 1 - rgb2[2] / 255

        min_cmy = min(c, m, y)
        c = (c - min_cmy) / (1 - min_cmy)
        m = (m - min_cmy) / (1 - min_cmy)
        y = (y - min_cmy) / (1 - min_cmy)
        k = min_cmy

        cmyk = tuple(
            map(
                lambda a: bround(
                    a * 100
                ),
                (
                    c,
                    m,
                    y,
                    k
                )
            )
        )

    # HSL
    hsl = tuple(
        map(
            lambda a: bround(
                a * 100
            ),
            colorsys.rgb_to_hls(
                *map(
                    lambda a: float(
                        bround(
                            a / 255,
                            2
                        )
                    ),
                    rgb2
                )
            )
        )
    )
    hsl = str(
        (
            str(
                bround(
                    (
                        hsl[0] / 100
                    ) * 360
                )
            ) + "°",
            hsl[2],
            hsl[1]
        )
    ).replace("'", "")

    # HSV
    hsv = tuple(
        map(
            lambda a: bround(
                a * 100
            ),
            colorsys.rgb_to_hsv(
                *map(
                    lambda a: float(
                        bround(
                            a / 255,
                            2
                        )
                    ),
                    rgb2
                )
            )
        )
    )
    hsv = str(
        (
            str(
                bround(
                    (
                        hsv[0] / 100
                    ) * 360
                )
            ) + "°",
            hsv[2],
            hsv[1]
        )
    ).replace("'" ,"")

    # YIQ
    yiq = tuple(
        map(
            lambda a: bround(
                a * 100,
                3
            ),
            colorsys.rgb_to_yiq(
                *map(
                    lambda a: float(
                        bround(
                            a / 255,
                            2
                        )
                    ),
                    rgb2
                )
            )
        )
    )

    embed = discord.Embed(
        title=f"Colour hex code: {ohex}",
        description=f"""rgb{rgb2}
cmyk{cmyk}
hsl{hsl}
hsv{hsv}
yiq{yiq}""",
        color=discord.Color.from_rgb(
            *yee
        )
    )
    embed.set_image(
        url=f"https://singlecolorimage.com/get/{hexcode}/200x200.png"
    )

    await ctx.followup.send(embed=embed)

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, 30, commands.BucketType.user)
async def newticket(ctx, *, topic):
    """Opens new ticket."""
    logging.debug("call: newticket()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    args = "".join(topic).split(" ")
    del topic
    if len(args) < 1:
        topic = "unknown topic"

    else:
        topic = " ".join(args)

    ticket_channel = await ctx.guild.create_text_channel(
        f"️🎫┊️ticket-{ctx.author.name}-{topic}",
        category=get(
            bot.get_guild(
                885685555084554294
            ).categories,
            id=946871757854363699
        )
    )
    await ticket_channel.set_permissions(
        ctx.guild.get_role(
            ctx.guild.id
        ),
        send_messages=False,
        read_messages=False
    )

    for role in ctx.guild.roles:
        if role.permissions.manage_guild:
            await ticket_channel.set_permissions(
                role,
                send_messages=True,
                read_messages=True,
                add_reactions=True,
                embed_links=True,
                attach_files=True,
                read_message_history=True,
                external_emojis=True
            )

    await ticket_channel.set_permissions(
        ctx.author,
        send_messages=True,
        read_messages=True,
        add_reactions=True,
        embed_links=True,
        attach_files=True,
        read_message_history=True,
        external_emojis=True
    )
    embed = discord.Embed(
        title="Ticket Guy",
        description=f"Your ticket has been created for {topic}.",
        color=discord.Color.from_rgb(1, 254, 170)
    )
    await ctx.followup.send(embed=embed)

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def closeticket(ctx):
    """Closes ticket."""
    logging.debug("call: closeticket()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    #print(ctx.channel.name)
    if "ticket-" in ctx.channel.name:
        await ctx.channel.delete()

    else:
        embed = discord.Embed(
            title="Ticket Guy",
            description="Please run this in the ticket channel you want to close!",
            color = discord.Color.from_rgb(112, 6, 2)
        )
        await ctx.followup.send(embed=embed)

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def kill(ctx, person):
    """Kill people to death. Why do I add these features?"""
    logging.debug("call: kill()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    if isMention(person):
        if int(ctx.author.id) == int(idFromMention(person)):
            await ctx.followup.send("Suicide has yet to be enabled.")
            return

    else:
        if person.strip() == ctx.author.name:
            await ctx.followup.send("Suicide has yet to be enabled.")
            return

    if ("@everyone" in person) or ("@here" in person):
        await ctx.followup.send("You should see a psychologist about the fact that you want to kill everyone.")
        return

    if isGP2(person):
        await ctx.followup.send("I am deeply saddened by this.")
        return

    if isMention(person):
        person = await bot.fetch_user(int(idFromMention(person)))
        person = person.name

    else:
        pass

    embed = discord.Embed(
        title=f"{ctx.author.name} has murdered {person}!",
        description="that sucks",
    )
    embed.set_image(url=kawaii("kill"))

    await ctx.followup.send(embed=embed)

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def slap(ctx, person):
    """Slap person. I'm just using Kawaii, ok? I'M BORED."""
    logging.debug("call: slap()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    if isMention(person):
        if int(ctx.author.id) == int(idFromMention(person)):
            await ctx.followup.send("why self-harm tho")
            return

    else:
        if person.strip() == ctx.author.name:
            await ctx.followup.send("why self-harm tho")
            return

    if ("@everyone" in person) or ("@here" in person):
        await ctx.followup.send("There's too many people to slap.")
        return

    if isGP2(person):
        await ctx.followup.send("I have not wronged you yet (I hope).")
        return

    if isMention(person):
        person = await bot.fetch_user(int(idFromMention(person)))
        person = person.name

    else:
        pass

    embed = discord.Embed(
        title=f"{ctx.author.name} has slapped {person} really hard!",
        description="ouch bro",
    )
    embed.set_image(url=kawaii("slap"))

    await ctx.followup.send(embed=embed)

@bot.slash_command(guild_ids=[885685555084554294])
@commands.has_guild_permissions(ban_members=True)
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def rules_refresh(ctx):
    """Refresh rules in Discord by JSON file"""
    logging.debug("call: rules_refresh()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer(ephemeral=True)

    guild = get(bot.guilds, id=885685555084554294)
    channel = get(guild.text_channels, id=885886027150020620)

    await channel.purge(limit=5)

    out = ""
    for i, v in enumerate(ruleslist):
        out += f"{i+1}. {v}\n\n"

    out += "\n***TL;DR*** __Just don't be an idiot.__"

    embed = discord.Embed(
        title="Rules, I guess.",
        description=out,
        color=0x01FEAA
    )

    await channel.send(embed=embed)
    await ctx.followup.send("Rules have been refreshed!")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.has_guild_permissions(ban_members=True)
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def faq_refresh(ctx):
    """Refresh FAQ in Discord by JSON file"""
    logging.debug("call: faq_refresh()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer(ephemeral=True)

    guild = get(bot.guilds, id=885685555084554294)
    channel = get(guild.text_channels, id=949085184047853589)

    await channel.purge(limit=5)

    out = ""
    for i, v in enumerate(faqlist):
        temp = "\n".join(v) + "\n\n"
        out += f"{i+1}.\n{temp}"

    embed = discord.Embed(
        title="FAQ/Info ¯\_(ツ)_/¯",
        description=out,
        color=0x01FEAA
    )

    await channel.send(embed=embed)
    await ctx.followup.send("FAQ has been refreshed!")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def snipe(ctx):
    """Snipe last deleted message"""
    logging.debug("call: snipe()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    tempd = await snipesc.find_one(
        {
            "_id": ObjectId(snipeid)
        }
    )

    try:
        temp = tempd[str(ctx.channel.id)]

        userName = (await bot.fetch_user(temp[1])).name

        embed = discord.Embed(
            title=f"Message sent by {userName} sniped >:)",
            description=temp[0]
                .replace("@everyone", "`@everyone`")
                .replace("@here", "`@here`"),
            color=0x01FEAA
        )
        if len(str(temp[3])) < 2:
            temp3 = f"0{str(temp[3])}"

        else:
            temp3 = temp[3]

        if len(str(temp[4])) < 2:
            temp4 = f"0{str(temp[4])}"

        else:
            temp4 = temp[4]

        embed.set_footer(text=f"Message with msgID \"{temp[2]}\" sent at {temp3}:{temp4} UTC+0000")

        await ctx.followup.send(embed=embed)

    except KeyError:
        await ctx.followup.send("No snipe could be found in this channel.")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def esnipe(ctx):
    """Esnipe last edited message"""
    logging.debug("call: esnipe()")
    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer()

    tempd = await snipesc.find_one(
        {
            "_id": ObjectId(esnipeid)
        }
    )

    try:
        temp = tempd[str(ctx.channel.id)]

        userName = (await bot.fetch_user(temp[2])).name

        embed = discord.Embed(
            title=f"Message edited by {userName} esniped >:)",
            description=f"{temp[0]}\n↓\n{temp[1]}",
            color=0x01FEAA
        )
        if len(str(temp[4])) < 2:
            temp4 = f"0{str(temp[4])}"

        else:
            temp4 = temp[4]

        if len(str(temp[5])) < 2:
            temp5 = f"0{str(temp[5])}"

        else:
            temp5 = temp[5]

        embed.set_footer(text=f"Message with msgID \"{temp[3]}\" sent at {temp4}:{temp5} UTC+0000")

        await ctx.followup.send(embed=embed)

    except KeyError:
        await ctx.followup.send("No esnipe could be found in this channel.")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def toggleautoproxy(ctx):
    """shhhhhhhhh this is a secret"""
    logging.debug("call: proxy()")

    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer(ephemeral=True)

    global proxyv

    if not isCuboid(ctx):
        await ctx.followup.send("hey you can't do that")
        return

    proxyv = not proxyv
    if proxyv:
        await ctx.followup.send("Proxied!")

    else:
        await ctx.followup.send("Unproxied!")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def proxysay(ctx, text):
    """shhhhhhhhhhhhh this is also a secret"""
    logging.debug("call: proxysay()")

    if ctx.channel.id == 955239604007628820:
        return

    await ctx.defer(ephemeral=True)

    if not isCuboid(ctx):
        await ctx.followup.send("hey you can't do that")
        return

    await ctx.followup.send("0")
    await ctx.send(text)

# Prefixed stuff, generally shortcuts for when saying something

@bot.command()
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def rule(ctx, num=0):
    """Print one or all rules."""
    logging.debug("call: rule()")
    if ctx.channel.id == 955239604007628820:
        return

    if not num:
        out = ""
        for i, v in enumerate(ruleslist):
            out += f"{i+1}. {v}\n"

        out += "\n***TL;DR*** __Don't be an idiot.__"

        embed = discord.Embed(
            title="Rules",
            description=out,
            color=0x01FEAA
        )

        await ctx.send(embed=embed)

    elif (num > len(ruleslist)) or (num < 0):
        await ctx.send("There's no rule with that number?")

    else:
        await ctx.send(f">>> {ruleslist[num-1]}")

@bot.command()
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def faq(ctx, num=0):
    """Print one or all FAQ stuff."""
    logging.debug("call: faq()")
    if ctx.channel.id == 955239604007628820:
        return

    if not num:
        out = ""
        for i, v in enumerate(faqlist):
            temp = "\n".join(v) + "\n\n"
            out += f"{i+1}.\n{temp}"

        embed = discord.Embed(
            title="FAQ/Info",
            description=out,
            color=0x01FEAA
        )

        await ctx.send(embed=embed)

    elif (num > len(faqlist)) or (num < 0):
        await ctx.send("There's no FAQ entry with that number?")

    else:
        await ctx.send(f">>> " + "\n".join(faqlist[num-1]))

@bot.command()
@commands.cooldown(1, globalCD, commands.BucketType.user)
async def format(ctx):
    """How to format code."""
    logging.debug("call: format()")
    if ctx.channel.id == 955239604007628820:
        return

    embed = discord.Embed(
        title="How to format code and stuff.",
        description="""__**To format code:**__
\\`\\`\\`<language name>
<code or something>
\\`\\`\\`

__**Example ig:**__
\\`\\`\\`python
import foo

print("bar")
\\`\\`\\`

__**Will display as:**__
```python
import foo

print("bar")
```""",
        color=0x01FEAA
    )

    await ctx.send(embed=embed)

@bot.command(aliases=["_-"])
async def exceptions(ctx):
    # Prevent things like "-_-" from triggering a command error
    return

# R U N .
bot.run(
    str(
        os.getenv(
            "DISCORD_TOKEN"
        )
    )
)
