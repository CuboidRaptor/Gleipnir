# Logging
# import os; os.chdir(os.path.dirname(__file__))
import logging

with open("latest.log", "w") as f: pass

logging.basicConfig(
    level=logging.DEBUG,
    filename="latest.log",
    format="[%(levelname)s]: %(message)s"
)
logging.debug("1.3.0.0")

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

from jokeapi import Jokes
from bson.objectid import ObjectId
from random import randint, choice
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv
from Levenshtein import ratio as lsr
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
unmutec = db["unmutes"]

pointsid = "620cfe72f63ae0339129c774"
warnid = "000000000000000000010f2c"
unmuteid = "621928f67c8347a08690da13"
emojismade = False

msgst = {}
# Endpoints: https://kawaii.red/api/gif/endpoints/token=token/

kawaiit = str(os.getenv("KAWAII"))

# Regexes
logging.debug("Defining regexes...")
mentionre = re.compile(r"(.*<@[0-9]+>.*)|(.*<@![0-9]+>.*)")
iUAT = re.compile(r".*# [0-9]{4}")
iRPr = re.compile(r"[0-9]+d[0-9]+")

# stuff
logging.debug("Defining bot constants...")
intents = discord.Intents.all()
bot = commands.Bot(
    intents=intents
)
with open("dat.json", "r") as f:
    # Load crap from data file
    logging.debug("Loading from JSON datafile...")
    yeetus = json.loads(f.read())
    curselist = yeetus["curses"]
    answers = yeetus["8ball"]
    quoteslist = yeetus["quotes"]

isSwear = r"\|\|" + ("((" + ")|(".join(curselist) + "))+") + r"\|\|"
# print(isSwear)
isSwear = re.compile(isSwear)

@tasks.loop(minutes=1)
async def umloop():
    tempd = await unmutec.find_one(
        {
            "_id": ObjectId(unmuteid)
        }
    )

    out = []
    for item in tempd:
        if item != "_id":
            if tempd[item] < (mtime.time() * 10):
                geeld = await bot.fetch_guild(885685555084554294)

                mutedRole = get(
                    geeld.roles,
                    name="Muted"
                )

                if not mutedRole:
                    logging.error("No Muted role? Has been deleted.")
                    return

                cMember = await geeld.fetch_member(int(item))

                try:
                    await cMember.add_roles(get(geeld.roles, name="Verified Member"), reason="idk")
                    await cMember.remove_roles(
                        mutedRole,
                        reason="idk"
                    )

                except discord.errors.Forbidden:
                    logging.warning("That person is already unmuted.")

                    return

                out.append(item)

    for item in out:
        del tempd[item]

    await unmutec.replace_one(
        {
            "_id": ObjectId(unmuteid)
        },
        tempd,
        upsert=True
    )

# events

@bot.event
async def on_ready():
    # logged in?
    logging.debug("call: on_ready()")
    print(f"CRBOT2 has logged on in to Discord as {bot.user}")

@bot.event
async def on_member_join(member):
    # Ooh someone joined
    logging.debug("call: on_member_join()")
    try:
        embed = discord.Embed(
            title=f"Thank you for joining!",
            description="Have fun!"
        )
        embed.set_image(url=kawaii("happy"))

        await member.send("""Hello there!
This is an automated message.:robot:
I am **CRBOT2**, the bot made by **Cuboid_Raptor# 7340**.
I have DM'd you to say, welcome to Cuboid's Café!:coffee:
I sincerely hope you have a great time in the server!:laughing:
You can also interact with me in the server, do be sure to use *[.]* as a command prefix.""",
            embed=embed
        )
    except discord.errors.HTTPException:
        logging.warning("HTTPException when DMing new user")

    channel = get(member.guild.text_channels, name="📢┊server-join-leave")

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

    channel = get(member.guild.text_channels, name="📢┊server-join-leave")
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

    if message.author.bot:
        return # Prevent bots from running commands.

    tingy = isSwear.sub("", str(message.content).lower().replace("```brainfuck", "```bf"))

    for word in curselist:
        if word in tingy:
            # you swore, idot.
            print("somebody swore uh oh")
            await message.channel.send(f"Don't swear, {message.author.mention}")
            return

    if ((bot.user.name in message.content) or ((str(bot.user.id) + ">") in message.content)) and not message.content.startswith(str("/")) and ("announcements" not in message.channel.name.lower()):
        # Did you say bot name?
        await message.channel.send("Hello there, I heard my name?")

    try:
        dif = mtime.time() - msgst[message.author.id]

    except KeyError:
        dif = 7 # Could be any number >0.5

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

@bot.event
async def on_application_command_error(ctx, error):
    # Oof something went wrong
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        embed = discord.Embed(
            title="Error",
            description="Unknown Command",
            color=discord.Color.red()
        )
        await ctx.followup.send(embed=embed)

    elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        embed = discord.Embed(
            title="Error",
            description="You're missing an argument!",
            color=discord.Color.red()
        )
        await ctx.followup.send(embed=embed)

    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error",
            description="Insufficient permissions!",
            color=discord.Color.red()
        )
        await ctx.followup.send(embed=embed)

    else:
        embed = discord.Embed(
            title="Error",
            description=str(error),
            color=discord.Color.red()
        )
        embed.set_footer(text="Is this a bug? Report it to help make this bot better!")
        await ctx.followup.send(embed=embed)

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

def isCB2(text):
    # Is text CRBOT2
    logging.debug("call: isCB2()")
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
async def ping(ctx):
    """pings, this is just for tests"""
    logging.debug("call: ping()")
    await ctx.defer()

    await ctx.followup.send("pong")

@bot.slash_command(guild_ids=[885685555084554294])
async def killcr2(ctx):
    """Kills CRBOT2. Only Cuboid_Raptor# 7340 can run this command."""
    logging.debug("call: killcr2()")
    await ctx.defer()

    if isCuboid(ctx):
        # r u me?
        await ctx.followup.send("OH FRICK NO MY FREE TRIAL OF LIFE EXPIRED")
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
async def no_u(ctx, person):
    """No you, people."""
    logging.debug("call: no_u()")
    await ctx.defer()

    if containsEveryone(person):
        await ctx.followup.send(f"***\\*GASP\\****")

    elif isCB2(person):
        await ctx.followup.send(f"I have been vaccinated against no-u's.")

    else:
        await ctx.followup.send(f"No u, {person}")

@bot.slash_command(guild_ids=[885685555084554294])
async def magic8ball(ctx, *, question):
    """Magic 8ball. Ask it questions."""
    logging.debug("call: magic8ball()")
    await ctx.defer()

    question = "".join(question)
    global answers
    await ctx.followup.send(f"In response to question \"{question}\":\n" + choice(answers))

@bot.slash_command(guild_ids=[885685555084554294])
async def quote(ctx):
    """Draws from my quotesbook and prints in chat."""
    logging.debug("call: quote()")
    await ctx.defer()

    global quoteslist
    await ctx.followup.send(choice(quoteslist))

@bot.slash_command(guild_ids=[885685555084554294])
async def shoot(ctx, person):
    """Shoot people. Idk y."""
    logging.debug("call: shoot()")
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

    if isCB2(person):
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
async def warn(ctx, person, *, reason):
    """Warn people."""
    logging.debug("call: warn()")
    await ctx.defer()

    if isCB2(person):
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
async def rmwarn(ctx, person, *, reason):
    """Remove warn from people."""
    logging.debug("call: rmwarn()")
    await ctx.defer()

    if isCB2(person):
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
async def warns(ctx, person):
    """Shows warns of people"""
    logging.debug("call: warns()")
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
async def warnclear(ctx):
    """Clears all warns globally. Only Cuboid_Raptor# 7340 can run this command."""
    logging.debug("call: warnclear()")
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
@commands.has_guild_permissions(kick_members=True)
async def kick(ctx, person, *, reason):
    """kicky"""
    logging.debug("call: kick()")
    await ctx.defer()

    if isCB2(str(person)):
        await ctx.followup.send(":(")

    else:
        if isMention(person):
            reason = reasonRet(reason)

            user = await ctx.message.guild.query_members(user_ids=[str(idFromMention(person))])
            user = user[0]
            await user.kick(reason=reason)
            await ctx.followup.send(f"{person} was kicked by {ctx.author.mention} for {reason}!")

        else:
            await err(ctx, "That person isn't a mention.")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.has_guild_permissions(ban_members=True)
async def ban(ctx, person, *, reason):
    """make ppl get ban'd"""
    logging.debug("call: ban()")
    await ctx.defer()

    if isCB2(str(person)):
        await ctx.followup.send("""██╗░░██╗
╚═╝░██╔╝
░░░██╔╝░
░░░╚██╗░
██╗░╚██╗
╚═╝░░╚═╝
""")

    else:
        if isMention(person):
            reason = reasonRet(reason)

            user = await ctx.message.guild.query_members(user_ids=[str(idFromMention(person))])
            try:
                user = user[0]

            except IndexError:
                await err(ctx, "hey bub that person doesn't exist, or some error has been thrown")
                await ctx.followup.send("(if that person does exist, notify Cuboid_Raptor# 7340)")
                return

            await user.ban(reason=reason)
            await ctx.followup.send(f"{person} was banned by {ctx.author.mention} for {reason}!")

        else:
            await err(ctx, "That person isn't a mention.")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.has_guild_permissions(ban_members=True)
async def unban(ctx, person, *, reason):
    """Unban people."""
    logging.debug("call: unban()")
    await ctx.defer()

    if isCB2(str(person)):
        await ctx.followup.send("Thanks for the attempt, but I haven't been banned in this server yet :)")

    else:
        if isUserAndTag(person):
            reason = reasonRet(reason)

            mname, mdisc = person.split("# ")

            banned_users = await ctx.message.guild.bans()
            for ban_entry in banned_users:
                user = ban_entry.user

                if (user.name, user.discriminator) == (mname, mdisc):
                    await ctx.message.guild.unban(user)
                    await ctx.message.channel.send(f"{user.mention} has been unbanned by {ctx.author.mention} for {reason}!")

        else:
            await err(ctx, "That person isn't a Username and Tag seperated by \"# \".")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.has_guild_permissions(kick_members=True)
async def mute(ctx, person, *, reason, silent=False):
    """Mute people until unmuted."""
    logging.debug("call: mute()")
    if not silent:
        await ctx.defer()

    if isCB2(str(person)):
        if not silent:
            await ctx.followup.send("dood you're a rude guy >:(")

    else:
        if isMention(person):
            if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
                reason = reasonRet(reason)

                geeld = ctx.message.guild
                mutedRole = get(
                    geeld.roles,
                    name="Muted"
                )

                if not mutedRole:
                    mutedRole = await geeld.create_role(name="Muted")

                    for channel in geeld.channels:
                        await channel.set_permissions(
                            mutedRole,
                            speak=False,
                            send_messages=False,
                            read_message_history=True,
                            read_messages=True,
                            view_channel=True,
                            mention_everyone=False,
                            reason=reason
                        )

                cMember = await geeld.fetch_member(idFromMention(person))

                try:
                    await cMember.add_roles(mutedRole, reason=reason)
                    await cMember.remove_roles(
                        get(geeld.roles, name="Verified Member"),
                        reason=reason
                    )

                except discord.errors.Forbidden:
                    if not silent:
                        await err(ctx, "This bot's role/permissions need to be higher in the hierarchy, or some error has occured.")
                        return

                if not silent:
                    await ctx.followup.send(f"{person} has been muted by {ctx.author.mention} for {reason}!")

            else:
                await err(ctx, "You don't have the proper permissions to run this command.")

        else:
            if not silent:
                await err(ctx, "That person isn't a mention.")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.has_guild_permissions(kick_members=True)
async def unmute(ctx, person, *, reason, silent=False):
    """Unmute people."""
    logging.debug("call: unmute()")
    if not silent:
        await ctx.defer()

    if isCB2(str(person)):
        if not silent:
            await ctx.followup.send("thanks for trying, but I haven't been muted yet, given how I'm talking to you.")

    else:
        if isMention(person):
            if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
                reason = reasonRet(reason)

                geeld = ctx.message.guild
                mutedRole = get(
                    geeld.roles,
                    name="Muted"
                )

                if not mutedRole:
                    await ctx.followup.send("No one has been muted in this server yet.")
                    return

                cMember = await geeld.fetch_member(idFromMention(person))

                try:
                    await cMember.add_roles(get(geeld.roles, name="Verified Member"), reason=reason)
                    await cMember.remove_roles(
                        mutedRole,
                        reason=reason
                    )

                except discord.errors.Forbidden:
                    if not silent:
                        await ctx.followup.send("That person is already unmuted.")

                    return

                if not silent:
                    await ctx.followup.send(f"{person} has been unmuted by {ctx.author.mention} for {reason}!")

            else:
                if not silent:
                    await err(ctx, "You don't have the proper permissions to run this command.")

        else:
            if not silent:
                await err(ctx, "That person isn't a mention.")

@bot.slash_command(guild_ids=[885685555084554294])
@commands.has_guild_permissions(kick_members=True)
async def tempmute(ctx, person, time, *, reason):
    """Temporarily mute people."""
    logging.debug("call: tempmute()")
    await ctx.defer()

    if isCB2(str(person)):
        await ctx.followup.send("stahp go away")

    else:
        if isMention(person):
            if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
                reason = reasonRet(reason)

                await mute(ctx, person, *args, silent=True)
                await ctx.followup.send(f"{person} has been tempmuted by {ctx.author.mention} for {reason} for {time} minutes!")
                et = int(mtime.time() * 10 + bround(float(time) * 600))

                tempd = await unmutec.find_one(
                    {
                        "_id": ObjectId(unmuteid)
                    }
                )

                try:
                    stupid = tempd[idFromMention(person)]
                    del stupid

                    tempd[idFromMention(person)] = max(tempd[idFromMention(person)], et)

                except KeyError:
                    tempd[idFromMention(person)] = et

                await unmutec.replace_one(
                    {
                        "_id": ObjectId(unmuteid)
                    },
                    tempd,
                    upsert=True
                )

            else:
                await err(ctx, "You don't have the proper permissions to run this command.")

        else:
            await err(ctx, "That person isn't a mention.")

@bot.slash_command(guild_ids=[885685555084554294])
async def roll(ctx, roll):
    """Roll die."""
    logging.debug("call: roll()")
    await ctx.defer()

    if not rollParse(roll):
        await err(ctx, "That isn't a valid dice to roll.")

    else:
        proll = rollParse(roll)
        proll[0], proll[1] = proll[0].replace(",", ""), proll[1].replace(",", "")
        s = 0
        try:
            for i in range(0, int(proll[0])):
                s += random.randint(1, int(proll[1]))

            await ctx.followup.send(f"{ctx.author.mention} rolled {roll} and got {s}")

        except ValueError:
            await err(ctx, "That isn't a valid roll.")

@bot.slash_command(guild_ids=[885685555084554294])
async def ship(ctx, person, person2=None):
    """Ship ship ship"""
    logging.debug("call: ship()")
    await ctx.defer()

    if person2 == None:
        person2 = ctx.author.mention

    if isCB2(person) or isCB2(person2):
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
async def points(ctx, user=None, silent=False):
    """Show number of points of others, or yourself."""
    logging.debug("call: points()")
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
async def leaderboard(ctx):
    """Leaderboard function for points."""
    logging.debug("call: leaderboard()")
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
            temp = await bot.fetch_user(thingy[n][0])

            if temp.bot:
                del thingy[n]
                await add(a, n)
                return

            output += f"{str(a) + str(temp.name)} - {str(thingy[n][1])} cp\n"
            del temp
            return 0

        except (KeyError) as error:
            logging.debug("Error occured in leaderboard.add(), could be incomplete leaderboard")
            logging.warning(f"{type(error).name}: {str(error)}")
            return 1

        except Exception as error:
            logging.debug("Unexpected error occured in leaderboard.add().")
            logging.error(f"{type(error).name}: {str(error)}")
            return 1

    if not await add("🥇", 0):
        if not await add("🥈", 1):
            if not await add("🥉", 2):
                if not await add("🏵️", 3):
                    await add("🏵️", 4)

    curp = await points(ctx, silent=True)
    curp = int(curp)

    try:
        yay = "# " + str(places.index(str(ctx.author.id)) + 1)

    except ValueError:
        yay = "Last"

    output += f"{ctx.author.name} - {curp} cp (Place " + yay + ")"

    await ctx.followup.send(output)

@bot.slash_command(guild_ids=[885685555084554294])
async def givepoints(ctx, person, point):
    """Give points to others."""
    logging.debug("call: give()")
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
async def coinflip(ctx):
    """Flip a coin, 'cuz why not."""
    logging.debug("call: coinflip()")
    await ctx.defer()

    if random.randint(0, 1):
        await ctx.followup.send("You flipped a coin and got heads!")

    else:
        await ctx.followup.send("You flipped a coin and got tails!")

@bot.slash_command(guild_ids=[885685555084554294])
async def joke(ctx):
    """Prints a random corny joke."""
    logging.debug("call: joke()")
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
async def color(ctx, hexcode):
    """Display a hex code colour."""
    logging.debug("call: color()")
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

    ohex = ohex.lstrip("\\").lstrip("# ")

    ohex = "\\# " + ohex

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
async def newticket(ctx, *, topic):
    """Opens new ticket."""
    logging.debug("call: newticket()")
    await ctx.defer()

    args = "".join(topic).split(" ")
    del topic
    if len(args) < 1:
        topic = "unknown topic"

    else:
        topic = " ".join(args)

    ticket_channel = await ctx.guild.create_text_channel(
        f"ticket-{ctx.author.name}-{topic}",
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
async def closeticket(ctx):
    """Closes ticket."""
    logging.debug("call: closeticket()")
    await ctx.defer()

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
async def kill(ctx, person):
    """Kill people to death. Why do I add these features?"""
    logging.debug("call: kill()")
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

    if isCB2(person):
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
async def slap(ctx, person):
    """Slap person. I'm just using Kawaii, ok? I'M BORED."""
    logging.debug("call: slap()")
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

    if isCB2(person):
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

# R U N .
umloop.start()
bot.run(str(os.getenv("DISCORD_TOKEN")))
