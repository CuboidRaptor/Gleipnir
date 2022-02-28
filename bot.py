#Logging
import logging

with open("latest.log", "w") as f: pass

logging.basicConfig(
    level=logging.DEBUG,
    filename="latest.log",
    format="[%(levelname)s]: %(message)s"
)
logging.debug("1.3.0.0")

#Imports
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

#MongoDB twash
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
doughc = db["money"]
stonksc = db["STONKS!"]
pointsc = db["points"]
unmutec = db["unmutes"]

pointsid = "620cfe72f63ae0339129c774"
warnid = "000000000000000000010f2c"
moneyid = "0000000000000000000aa289"
stonksid = "61bf8fc2ad877a0d31f685ea"
unmuteid = "621928f67c8347a08690da13"
emojismade = False

msgst = {}
# Endpoints: https://kawaii.red/api/gif/endpoints/token=token/

kawaiit = str(os.getenv("KAWAII"))

#Regexes
logging.debug("Defining regexes...")
mentionre = re.compile(r"(.*<@[0-9]+>.*)|(.*<@![0-9]+>.*)")
iUAT = re.compile(r".*#[0-9]{4}")
iRPr = re.compile(r"[0-9]+d[0-9]+")

#stuff
logging.debug("Defining bot constants...")
pf = "."
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=pf,
    strip_after_prefix=True,
    intents=intents
)
with open("dat.json", "r") as f:
    #Load crap from data file
    logging.debug("Loading from JSON datafile...")
    yeetus = json.loads(f.read())
    curselist = yeetus["curses"]
    answers = yeetus["8ball"]
    quoteslist = yeetus["quotes"]

isSwear = r"\|\|" + ("((" + ")|(".join(curselist) + "))") + r"\|\|"
#print(isSwear)
isSwear = re.compile(isSwear)

@tasks.loop(minutes=1)
async def da_muns():
    #Fluctuates STONKS! price
    logging.debug("Changing STONKS! price")
    tempd = await stonksc.find_one(
        {
            "_id": ObjectId(stonksid)
        }
    )
    
    tempd["inc"], tempd["STANKS!"], tempd["trend"] = float(tempd["inc"]), float(tempd["STANKS!"]), float(tempd["trend"])
    
    tempd["inc"] += random.random() * 12
    tempd[
        "STANKS!"
    ] = bround(
        abs(
            (
                (
                    random.random() * 10
                ) + 1
            ) * math.sin(
                tempd[
                    "inc"
                ] * (
                    (
                        random.random() * 4
                    ) + 1
                )
            ) + 6
        ),
        3
    )
    tempd["STANKS!"] += int(tempd["trend"])
    
    #lol 69th line
    if tempd["STANKS!"] < 1:
        tempd["STANKS!"] = 1 + random.random() / 2
        
    tempd["STANKS!"] = abs(tempd["STANKS!"])

    await stonksc.replace_one(
        {
            "_id": ObjectId(stonksid)
        },
        tempd,
        upsert=True
    )

@tasks.loop(minutes=18)
async def allowance():
    logging.debug("Giving allowance...")
    tempd = await doughc.find_one(
        {
            "_id": ObjectId(moneyid)
        }
    )
    for item in tempd:
        if item != "_id":
            tempd[item][0] += 0.625

    await doughc.replace_one(
        {
            "_id": ObjectId(moneyid)
        },
        tempd,
        upsert=True
    )

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

#events

@bot.event
async def on_ready():
    #logged in?
    logging.debug("call: on_ready()")
    print(f"CRBOT2 has logged on in to Discord as {bot.user}")
    
    #Remove accidental allowance
    await asyncio.sleep(1)
    tempd = await doughc.find_one(
        {
            "_id": ObjectId(moneyid)
        }
    )
    for item in tempd:
        if item != "_id":
            tempd[item][0] -= 0.625

    await doughc.replace_one(
        {
            "_id": ObjectId(moneyid)
        },
        tempd,
        upsert=True
    )

@bot.event
async def on_member_join(member):
    logging.debug("call: on_member_join()")
    try:
        embed = discord.Embed(
            title=f"Thank you for joining!",
            description="Have fun!"
        )
        embed.set_image(url=kawaii("happy"))

        await member.send("""Hello there!
This is an automated message.:robot: 
I am **CRBOT2**, the bot made by **Cuboid_Raptor#7340**.
I have DM'd you to say, welcome to Cuboid's Café!:coffee: 
I sincerely hope you have a great time in the server!:laughing:
You can also interact with me in the server, do be sure to use *[.]* as a command prefix.""",
            embed=embed
        )
    except discord.errors.HTTPException:
        logging.warning("HTTPException when DMing new user")

    channel = get(member.guild.text_channels, name="📢events-announcements📢")

    embed = discord.Embed(
        title=f"{member.mention} has joined!",
        description="yay and stuff"
    )
    embed.set_image(url=kawaii("wave"))

    await channel.send(f"*{member.mention} is here! We hope you have a nice time here, {member.mention}!*")
    await channel.send(embed=embed)
    
@bot.event
async def on_member_remove(member):
    logging.debug("call: on_member_remove()")

    embed = discord.Embed(
        title=f"Oh no! {member.mention} has left.",
        description="\\:'\\("
    )
    embed.set_image(url=kawaii("cry"))

    channel = get(member.guild.text_channels, name="📢events-announcements📢")
    await channel.send(
        f"*{member.mention} has left. Goodbye, {member.mention}*",
        embed=embed
    )

@bot.event
async def on_message(message):
    #When someone messages
    logging.debug("call: on_message()")
    if message.author == bot.user:
        #Is the bot messaging.
        return

    if message.author.bot:
        return #Prevent bots from running commands.

    tingy = isSwear.sub("", str(message.content).lower().replace("```brainfuck", "```bf"))

    for word in curselist:
        if word in tingy:
            #you swore, idot.
            print("somebody swore uh oh")
            await message.delete()
            await message.channel.send(f"Don't swear, {message.author.mention}")
            return

    if ((bot.user.name in message.content) or ((str(bot.user.id) + ">") in message.content)) and not message.content.startswith(str(pf)) and ("announcements" not in message.channel.name.lower()):
        #Did you say bot name?
        await message.channel.send("Hello there, I heard my name?")

    try:
        dif = mtime.time() - msgst[message.author.id]

    except KeyError:
        dif = 7 #Could be any number >0.5

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

    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        embed = discord.Embed(
            title="Error",
            description="Unknown Command",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        embed = discord.Embed(
            title="Error",
            description="You're missing an argument!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error",
            description="Insufficient permissions!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            title="Error",
            description=str(error),
            color=discord.Color.red()
        )
        embed.set_footer(text="Is this a bug? Report it to help make this bot better!")
        await ctx.send(embed=embed)

#test command
@bot.command()
async def test(ctx):
    """Test command for testing code. Doesn't do anything at the moment."""
    logging.debug("call: test()")
    pass

#Functions
def d(n):
    #precision
    logging.debug("call: d()")
    return Decimal(str(n))

def bround(n, a=0):
    #better rounding
    logging.debug("call: bround()")
    if a == 0:
        return int(round(d(str(n)), a))
    
    else:
        return float(round(d(str(n)), a))

def g_role(ctx, rname):
    #Checks if ctx.message.author has any one of the roles in [rname]
    logging.debug("call: g_role()")
    role_t = []
    for item in rname:
        role_t.append(get(ctx.guild.roles, name=str(item)) in ctx.message.author.roles)
        
    out = role_t[0]
    for item in role_t[1:]:
        out = out or item
        
    return out

def isCuboid(ctx):
    #Is message author in ctx me (Cuboid)?
    logging.debug("call: isCuboid()")
    if ctx.message.author.id == 588132098875850752:
        return True
    
    else:
        return False
    
def isMention(text):
    #Is text a mention?
    logging.debug("call: isMention()")
    global mentionre
    return mentionre.match(text) != None
    
def idFromMention(mention):
    #Get User ID from mention
    logging.debug("call: idFromMention()")
    if mention.startswith("<@!"):
        return str(mention)[3:-1]
    
    else:
        return str(mention)[2:-1]
    
def isCB2(text):
    #Is text CRBOT2
    logging.debug("call: isCB2()")
    text = text.strip()
    if (text == str(bot.user.name)) or (text == str(bot.user)) or (text == "<@" + str(bot.user.id) + ">") or (text == "<@!" + str(bot.user.id) + ">"):
        return True
    
    else:
        return False
    
def isUserAndTag(text):
    #Checks if the string contains a username and tag
    logging.debug("call: isUserAndTag()")
    global iUAT
    if iUAT.match(text.strip()) == None:
        return False
    
    else:
        if len(text.split("#")) != 2:
            return False
        
        else:
            return True
        
def isEmpty(text):
    #Checks if string is empty
    logging.debug("call: isEmpty()")
    if text == "" or text.isspace():
        return True
    
    else:
        return False
    
def reasonRet(arr):
    #Returns reason from *args
    logging.debug("call: reasonRet()")
    reason = " ".join(arr)
                    
    if isEmpty(reason):
        reason = "no good reason at all"
        
    return reason

def rollParse(string):
    #Parses roll number
    logging.debug("call: rollParse()")
    global iRPr
    if iRPr.match(string) == None:
        return False
    
    elif len(string.lower().split("d")) != 2:
        return False
    
    else:
        return string.lower().split("d")
    
def numform(n, a=0):
    #Adds commas and round number.
    logging.debug("call: numform()")
    return "{:,}".format(bround(float(n), a))

def containsEveryone(message):
    #Check if message contains @everyone pings.
    logging.debug("call: containsEveryone()")
    return ("@everyone" in message) or ("@here" in message)

def kawaii(sub):
    #Gets GIF from kawaii.red
    logging.debug("call: kawaii()")
    r = requests.get(f"https://kawaii.red/api/gif/{sub}/token={kawaiit}/")
    return str(r.json()['response'])

def fullName(author):
    #Returns name + tag from user/Member object
    logging.debug("call: fullName()")
    return author.name + "#" + author.discriminator

async def err(ctx, msg, clr=(255, 7, 1), title="Error"):
    embed = discord.Embed(
        title=title,
        description=str(msg),
        color=discord.Color.from_rgb(*clr)
    )
    await ctx.send(embed=embed)
    logging.error(msg)

def prod(n):
    p = 1
    for i in n:
        p *= i

    return p

#Commands
@bot.command()
async def ping(ctx):
    """pings, this is just for tests"""
    logging.debug("call: ping()")
    await ctx.send("pong")
    
@bot.command(aliases=["killswitch"])
async def killcr2(ctx):
    """Kills CRBOT2. Only Cuboid_Raptor#7340 can run this command."""
    logging.debug("call: killcr2()")
    if isCuboid(ctx):
        #r u me?
        await ctx.send("Ok, Ending...")
        print("Ending...")
        sys.exit()
        
    else:
        await err(
            ctx,
            "Why are you trying to kill me? :(",
            clr=(89, 10, 1),
            title="Rude."
        )
    
@bot.command(aliases=["no-u"])
async def no_u(ctx, person):
    """No you, people."""
    logging.debug("call: no_u()")
    if containsEveryone(person):
        await ctx.send(f"***\\*GASP\\****")
        
    elif isCB2(person):
        await ctx.send(f"I have been vaccinated against no-u's.")
        
    else:
        await ctx.send(f"No u, {person}")

@bot.command(aliases=["8ball"])
async def magic8ball(ctx):
    """Magic 8ball. Ask it questions."""
    logging.debug("call: magic8ball()")
    global answers
    await ctx.send(choice(answers))
    
@bot.command()
async def quote(ctx):
    """Draws from my quotesbook and prints in chat."""
    logging.debug("call: quote()")
    global quoteslist
    await ctx.send(choice(quoteslist))

@bot.command()
async def shoot(ctx, person):
    """Shoot people. Idk y."""
    logging.debug("call: shoot()")

    if isMention(person):
        if int(ctx.message.author.id) == int(idFromMention(person)):
            await ctx.send("Aw c'mon, don't kill yourself.")
            return

    else:
        if person.strip() == ctx.message.author.name:
            await ctx.send("Aw c'mon, don't kill yourself.")
            return

    if ("@everyone" in person) or ("@here" in person):
        await ctx.send("Mass genocide isn't allowed yet. Try again later.")
        return

    if isCB2(person):
        await ctx.send("I pull out a handheld CIWS and shoot you. Who's the shooter now?")
        return

    if isMention(person):
        person = await bot.fetch_user(int(idFromMention(person)))
        person = person.name

    embed = discord.Embed(
        title=f"{ctx.message.author.name} has shot {person}!",
        description="oof",
    )
    embed.set_image(url=kawaii("shoot"))

    await ctx.send(embed=embed)
    
@bot.command()
@commands.has_guild_permissions(kick_members=True)
async def warn(ctx, person, *reason):
    """Warn people."""
    logging.debug("call: warn()")
    if isCB2(person):
        await ctx.send("I HAVEN'T DONE ANYTHING!")
        
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

            await ctx.send(f"{person} has been warned by {ctx.message.author.mention} for {reason}!")

@bot.command()
@commands.has_guild_permissions(kick_members=True)
async def rmwarn(ctx, person, *reason):
    """Remove warn from people."""
    logging.debug("call: rmwarn()")
    if isCB2(person):
        await ctx.send("I haven't been warned yet. I wouldn't warn myself.")
        
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

            await ctx.send(f"A warn has been removed from {person} by {ctx.message.author.mention} for {reason}!")

@bot.command()
async def warns(ctx, person):
    """Shows warns of people"""
    logging.debug("call: warns()")
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
            await ctx.send(f"{person} has " + out + " warn!")
            
        else:
            await ctx.send(f"{person} has " + out + " warns!")

@bot.command()
async def warnclear(ctx):
    """Clears all warns globally. Only Cuboid_Raptor#7340 can run this command."""
    logging.debug("call: warnclear()")
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
        await ctx.send("All global warns have been cleared.")
        print("All global warns have been cleared.")
        
    else:
        await err(ctx, "You don't have the proper permissions to run this command.")

@bot.command()
@commands.has_guild_permissions(kick_members=True)
async def kick(ctx, person, *reason):
    """kicky"""
    logging.debug("call: kick()")
    if isCB2(str(person)):
        await ctx.send(":(")
        
    else:
        if isMention(person):
            reason = reasonRet(reason)

            user = await ctx.message.guild.query_members(user_ids=[str(idFromMention(person))])
            user = user[0]
            await user.kick(reason=reason)
            await ctx.send(f"{person} was kicked by {ctx.message.author.mention} for {reason}!")

        else:
            await err(ctx, "That person isn't a mention.")

@bot.command()
@commands.has_guild_permissions(ban_members=True)
async def ban(ctx, person, *reason):
    """make ppl get ban'd"""
    logging.debug("call: ban()")
    if isCB2(str(person)):
        await ctx.send("""██╗░░██╗
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
                await ctx.send("(if that person does exist, notify Cuboid_Raptor#7340)")
                return

            await user.ban(reason=reason)
            await ctx.send(f"{person} was banned by {ctx.message.author.mention} for {reason}!")

        else:
            await err(ctx, "That person isn't a mention.")

@bot.command()
@commands.has_guild_permissions(ban_members=True)
async def unban(ctx, person, *reason):
    """Unban people."""
    logging.debug("call: unban()")
    if isCB2(str(person)):
        await ctx.send("Thanks for the attempt, but I haven't been banned in this server yet :)")
        
    else:
        if isUserAndTag(person):
            reason = reasonRet(reason)

            mname, mdisc = person.split("#")

            banned_users = await ctx.message.guild.bans()
            for ban_entry in banned_users:
                user = ban_entry.user

                if (user.name, user.discriminator) == (mname, mdisc):
                    await ctx.message.guild.unban(user)
                    await ctx.message.channel.send(f"{user.mention} has been unbanned by {ctx.message.author.mention} for {reason}!")

        else:
            await err(ctx, "That person isn't a Username and Tag seperated by \"#\".")

@bot.command()
@commands.has_guild_permissions(kick_members=True)
async def mute(ctx, person, silent=False, *reason):
    """Mute people until unmuted."""
    logging.debug("call: mute()")

    if isCB2(str(person)):
        if not silent:
            await ctx.send("dood you're a rude guy >:(")
        
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
                    await ctx.send(f"{person} has been muted by {ctx.message.author.mention} for {reason}!")

            else:
                await err(ctx, "You don't have the proper permissions to run this command.")

        else:
            if not silent:
                await err(ctx, "That person isn't a mention.")

@bot.command()
@commands.has_guild_permissions(kick_members=True)
async def unmute(ctx, person, silent=False, *reason):
    """Unmute people."""
    logging.debug("call: unmute()")
    if isCB2(str(person)):
        if not silent:
            await ctx.send("thanks for trying, but I haven't been muted yet, given how I'm talking to you.")
        
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
                    await ctx.send("No one has been muted in this server yet.")
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
                        await ctx.send("That person is already unmuted.")

                    return
                
                if not silent:
                    await ctx.send(f"{person} has been unmuted by {ctx.message.author.mention} for {reason}!")

            else:
                if not silent:
                    await err(ctx, "You don't have the proper permissions to run this command.")

        else:
            if not silent:
                await err(ctx, "That person isn't a mention.")

@bot.command()
@commands.has_guild_permissions(kick_members=True)
async def tempmute(ctx, person, time, *reason):
    """Temporarily mute people."""
    logging.debug("call: tempmute()")
    if isCB2(str(person)):
        await ctx.send("stahp go away")
        
    else:
        if isMention(person):
            if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
                reason = reasonRet(reason)
                    
                await mute(ctx, person, *args, silent=True)
                await ctx.send(f"{person} has been tempmuted by {ctx.message.author.mention} for {reason} for {time} minutes!")
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

@bot.command()
async def roll(ctx, roll):
    """Roll die."""
    logging.debug("call: roll()")
    if not rollParse(roll):
        await err(ctx, "That isn't a valid dice to roll.")
        
    else:
        proll = rollParse(roll)
        proll[0], proll[1] = proll[0].replace(",", ""), proll[1].replace(",", "")
        s = 0
        try:
            for i in range(0, int(proll[0])):
                s += random.randint(1, int(proll[1]))
                
            await ctx.send(f"{ctx.message.author.mention} rolled {roll} and got {s}")
            
        except ValueError:
            await err(ctx, "That isn't a valid roll.")

@bot.command()
async def ship(ctx, person, person2=None):
    """Ship ship ship"""
    logging.debug("call: ship()")
    if person2 == None:
        person2 = ctx.message.author.mention

    if isCB2(person) or isCB2(person2):
        await ctx.send("bruh why")
        
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
        await ctx.send(
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

@bot.command(aliases=["open-account"])
async def open_account(ctx):
    """Open STONKS! account"""
    logging.debug("call: open_account()")
    person = ctx.message.author

    tempd = await doughc.find_one(
        {
            "_id": ObjectId(moneyid)
        }
    )
    try:
        stupid = tempd[person.mention]
        del stupid
        await err(ctx, "You already have a STONKS! account.")
        return

    except KeyError:
        tempd[person.mention] = [100, 0]

    await doughc.replace_one(
        {
            "_id": ObjectId(moneyid)
        },
        tempd,
        upsert=True
    )
    await ctx.send(f"{person.mention} has been registered with STONKS!!")

@bot.command(aliases=["reset-stonks"])
async def reset_stonks(ctx, silent=False):
    """Reset STONKS! Only Cuboid_Raptor#7340 can run this command"""
    logging.debug("call: reset_stonks()")
    if isCuboid(ctx):
        tempd = await stonksc.find_one(
            {
                "_id": ObjectId(stonksid)
            }
        )
        tempd["STANKS!"] = 1
        tempd["inc"] = 0

        await stonksc.replace_one(
            {
                "_id": ObjectId(stonksid)
            },
            tempd,
            upsert=True
        )
        if silent == False:
            await ctx.send("STONKS! has been resetted!")
            print("STONKS! has been resetted!")
        
    else:
        err(ctx, "You don't have the proper permissions to run that command.")

@bot.command(aliases=["erase-stonks"])
async def erase_stonks(ctx, silent=False):
    logging.debug("call: erase_stonks()")
    """Erase all global STONKS! from shareholders. Only Cuboid_Raptor#7340"""
    if isCuboid(ctx):
        tempd = await doughc.find_one(
            {
                "_id": ObjectId(moneyid)
            }
        )
        for item in tempd:
            if item != "_id":
                tempd[item][1] = 0

        await doughc.replace_one(
            {
                "_id": ObjectId(moneyid)
            },
            tempd,
            upsert=True
        )
        
        if silent == False:
            await ctx.send("All global STONKS! records have been erased.")
    
    else:
        err(ctx, "You don't have the proper permissions to run that command")

@bot.command(aliases=["stonks-price"])
async def stonks_price(ctx, silent=False):
    """Print current STONKS! price"""
    logging.debug("call: stonks_price()")

    temp = await stonksc.find_one(
        {
            "_id": ObjectId(stonksid)
        }
    )

    if silent == False:
        await ctx.send(
            "The current STONKS! price is: " + str(
                numform(
                    temp["STANKS!"],
                    3
                )
            ) + " Cuboid Dollars!"
        )
        
    else:
        return float(
            temp["STANKS!"]
        )

@bot.command(aliases=["erase-money"])
async def erase_money(ctx, silent=False):
    """Erase all money, globally. Only Cuboid_Raptor#7340 can run this command."""
    logging.debug("call: erase_money()")
    if isCuboid(ctx):
        tempd = await doughc.find_one(
            {
                "_id": ObjectId(moneyid)
            }
        )
        for item in tempd:
            if item != "_id":
                tempd[item][0] = 100

        await doughc.replace_one(
            {
                "_id": ObjectId(moneyid)
            },
            tempd,
            upsert=True
        )
        
        if silent == False:
            await ctx.send("All global money records have been erased.")
    
    else:
        err(ctx, "You don't have the proper permissions to run that command.")

@bot.command(aliases=["reset-finance"])
async def reset_finance(ctx):
    """Reset all finances. Dangerous command. Ony can be user by Cuboid_Raptor#7340."""
    logging.debug("call: reset_finance()")
    if isCuboid(ctx):
        await reset_stonks(ctx, silent=True)
        await erase_stonks(ctx, silent=True)
        await erase_money(ctx, silent=True)
        await ctx.send("All finances have been globally reset.")
        
    else:
        await err(ctx, "You don't have the proper permissions to run that command.")

@bot.command()
async def wallet(ctx, silent=False):
    """Shows current amount of money if you have a registered account."""
    logging.debug("call: wallet()")
    tempd = await doughc.find_one(
        {
            "_id": ObjectId(moneyid)
        }
    )
    for item in tempd:
        if item == ctx.message.author.mention:
            if silent == False:
                await ctx.send(f"You have ${numform(tempd[item][0], 3)} and {numform(tempd[item][1], 3)} STONKS!")
                return
            
            else:
                return [tempd[item][0], tempd[item][1]]
            
    await err(ctx, "You haven't signed up for STONKS! yet.\nUse .open-account to do that.")

@bot.command()
async def buy(ctx, amount):
    """Buy some STONKS! from STONKS!."""
    logging.debug("call: buy()")
    try:
        amount = int(bround(float(amount)))
        if amount < 1:
            await err(ctx, f"bruh u can't buy {amount} STONKS!.")
            return
        
    except ValueError:
        await err(ctx, f"bruh u can't buy \"{amount}\" STONKS!.")
        return
        
    sp = await stonks_price(ctx, silent=True)
    sp *= amount
    sp = bround(sp, 3)
    if (await wallet(ctx, silent=True))[0] < sp:
        await err(ctx, "You don't have enough money.")
        
    else:
        tempd = await doughc.find_one(
            {
                "_id": ObjectId(moneyid)
            }
        )
        for item in tempd:
            if item == ctx.message.author.mention:
                tempd[item][0] -= sp
                tempd[item][1] += amount

        await doughc.replace_one(
            {
                "_id": ObjectId(moneyid)
            },
            tempd,
            upsert=True
        )
        
        tempd = await stonksc.find_one(
            {
                "_id": ObjectId(stonksid)
            }
        )
        
        tempd["trend"] += (random.random() / 10) * amount

        await stonksc.replace_one(
            {
                "_id": ObjectId(stonksid)
            },
            tempd,
            upsert=True
        )
            
        await ctx.send(f"You have bought {numform(amount, 3)} STONKS! for ${numform(sp, 3)}!")

@bot.command()
async def sell(ctx, amount):
    """Sell some STONKS! from STONKS!."""
    logging.debug("call: sell()")
    try:
        amount = int(bround(float(amount)))
        if amount < 1:
            await err(ctx, f"bruh u can't sell {amount} STONKS!.")
            return
        
    except ValueError:
        await err(ctx, f"bruh u can't sell \"{amount}\" STONKS!.")
        return
        
    sp = await stonks_price(ctx, silent=True)
    sp *= amount
    sp = bround(sp, 3)
    
    if (await wallet(ctx, silent=True))[1] < amount:
        await err(ctx, "You don't have enough STONKS! to sell.")
        
    else:
        tempd = await doughc.find_one(
            {
                "_id": ObjectId(moneyid)
            }
        )
        for item in tempd:
            if item == ctx.message.author.mention:
                if (tempd[item][0] + sp) > 2000000000:
                    await err(ctx, "You have hit the money limit. Try giving some away.")
                    return
                
                tempd[item][0] += sp
                tempd[item][1] -= amount

        await doughc.replace_one(
            {
                "_id": ObjectId(moneyid)
            },
            tempd,
            upsert=True
        )
        
        tempd = await stonksc.find_one(
            {
                "_id": ObjectId(stonksid)
            }
        )
        
        tempd["trend"] -= (random.random() / 10) * amount

        await stonksc.replace_one(
            {
                "_id": ObjectId(stonksid)
            },
            tempd,
            upsert=True
        )
        
        await ctx.send(f"You have sold {numform(amount, 3)} STONKS! for ${numform(sp, 3)}!")

@bot.command()
async def give(ctx, person, amount):
    """give da STONKS! muns to someone else"""
    logging.debug("call: give()")
    if isMention(person):
        person = f"<@{idFromMention(person)}>"
        try:
            amount = bround(float(amount), 3)
            if amount < 1:
                await err(ctx, f"bruh u can't give \\<$1.")
                return
            
        except ValueError:
            await err(ctx, f"bruh u can't give $\"{amount}\".")
            return
        
        if (await wallet(ctx, silent=True))[0] < amount:
            await err(ctx, "You don't have enough money to give.")
            
        else:
            tempd = await doughc.find_one(
                {
                    "_id": ObjectId(moneyid)
                }
            )
            
            try:
                this_is_a_stupid_variable = tempd[person]
                del this_is_a_stupid_variable
                
            except KeyError as error:
                await err(ctx, "That person hasn't signed up for STONKS! yet.")
                return
            
            for item in tempd:
                if item == ctx.message.author.mention:
                    tempd[item][0] -= amount
                    
                elif item == person:
                    if (tempd[item][0] + amount) > 2000000000:
                        await ctx.send("Your target hit the money limit. Try giving some to someone else.")
                        
                        for item in tempd:
                            if item == ctx.message.author.mention:
                                tempd[item][0] += amount
                                
                        return
                    
                    tempd[item][0] += amount

            await doughc.replace_one(
                {
                    "_id": ObjectId(moneyid)
                },
                tempd,
                upsert=True
            )
            
            await ctx.send(f"You have given ${numform(amount, 3)} to {person}")
            
    else:
        await err(ctx, "That person isn't a mention.")

@bot.command()
async def points(ctx, user=None, silent=False):
    """Show number of points of others, or yourself."""
    logging.debug("call: points()")
    if user == None:
        isSelf = True
        user = ctx.message.author.id

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
            await ctx.send("You have " + out)

        else:
            temp = await bot.fetch_user(user)
            await ctx.send(f"{temp.name} has " + out)
            del temp

    else:
        return tempd[str(user)]

@bot.command(aliases=["lb"])
async def leaderboard(ctx):
    """Leaderboard function for points."""
    logging.debug("call: leaderboard()")
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
        yay = "#" + str(places.index(str(ctx.message.author.id)) + 1)

    except ValueError:
        yay = "Last"

    output += f"{ctx.message.author.name} - {curp} cp (Place " + yay + ")"

    await ctx.send(output)

@bot.command()
async def givepoints(ctx, person, point):
    """Give points to others."""
    logging.debug("call: give()")

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

    tempd[str(ctx.message.author.id)] -= int(point)

    if tempd[str(ctx.message.author.id)] < 0:
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

    await ctx.send(f"{point} cp have been sent to {person}!")

@bot.command()
async def coinflip(ctx):
    logging.debug("call: coinflip()")
    if random.randint(0, 1):
        await ctx.send("You flipped a coin and got heads!")

    else:
        await ctx.send("You flipped a coin and got tails!")

@bot.command()
async def joke(ctx):
    """Prints a random corny joke."""
    logging.debug("call: joke()")
    j = await Jokes()
    jk = await j.get_joke(
        blacklist=[
            "nsfw",
            "racist",
            "sexist"
        ]
    )

    if jk["type"] == "single":
        await ctx.send(jk["joke"])

    else:
        await ctx.send(jk["setup"])
        await asyncio.sleep(1)
        await ctx.send(jk["delivery"])

@bot.command(aliases=["colour", "clr"])
async def color(ctx, hexcode):
    """Display a hex code colour."""
    logging.debug("call: color()")

    ohex = str(hexcode).upper()
    hexcode = ohex.lstrip("\\").lstrip("#").lower()

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

    ohex = ohex.lstrip("\\").lstrip("#")

    ohex = "\\#" + ohex

    #RGB
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

    #CMYK
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

    #HSL
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
    hsl = (
        bround(
            (
                hsl[0] / 100
            ) * 360
        ),
        hsl[2],
        hsl[1]
    )

    #HSV
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
    hsv = (
        bround(
            (
                hsv[0] / 100
            ) * 360
        ),
        hsv[2],
        hsv[1]
    )

    #YIQ
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

    await ctx.send(embed=embed)

@bot.command(aliases=["new-ticket", "new_ticket"])
async def newticket(ctx, *topic):
    """Opens new ticket."""
    logging.debug("call: newticket()")
    args = topic
    del topic
    if len(args) < 1:
        topic = "unknown topic"

    else:
        topic = " ".join(args)

    ticket_channel = await ctx.guild.create_text_channel(
        f"ticket-{ctx.message.author.name}-{topic}",
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
    await ctx.send(embed=embed)

@bot.command(aliases=["close-ticket", "close_ticket"])
async def closeticket(ctx):
    """Closes ticket."""
    logging.debug("call: closeticket()")
    if "ticket-" in ctx.channel.name:
        await ctx.channel.delete()

    else:
        embed = discord.Embed(
            title="Ticket Guy",
            description="Please run this in the ticket channel you want to close!",
            color = discord.Color.from_rgb(112, 6, 2)
        )
        await ctx.send(embed=embed)

@bot.command()
async def kill(ctx, person):
    """Kill people to death. Why do I add these features?"""
    logging.debug("call: kill()")

    if isMention(person):
        if int(ctx.message.author.id) == int(idFromMention(person)):
            await ctx.send("Suicide has yet to be enabled.")
            return

    else:
        if person.strip() == ctx.message.author.name:
            await ctx.send("Suicide has yet to be enabled.")
            return

    if ("@everyone" in person) or ("@here" in person):
        await ctx.send("You should see a psychologist about the fact that you want to kill everyone.")
        return

    if isCB2(person):
        await ctx.send("I am deeply saddened by this.")
        return

    if isMention(person):
        person = await bot.fetch_user(int(idFromMention(person)))
        person = person.name

    else:
        pass

    embed = discord.Embed(
        title=f"{ctx.message.author.name} has murdered {person}!",
        description="that sucks",
    )
    embed.set_image(url=kawaii("kill"))

    await ctx.send(embed=embed)

@bot.command()
async def slap(ctx, person):
    """Slap person. I'm just using Kawaii, ok? I'M BORED."""
    logging.debug("call: slap()")

    if isMention(person):
        if int(ctx.message.author.id) == int(idFromMention(person)):
            await ctx.send("why self-harm tho")
            return

    else:
        if person.strip() == ctx.message.author.name:
            await ctx.send("why self-harm tho")
            return

    if ("@everyone" in person) or ("@here" in person):
        await ctx.send("There's too many people to slap.")
        return

    if isCB2(person):
        await ctx.send("I have not wronged you yet (I hope).")
        return

    if isMention(person):
        person = await bot.fetch_user(int(idFromMention(person)))
        person = person.name

    else:
        pass

    embed = discord.Embed(
        title=f"{ctx.message.author.name} has slapped {person} really hard!",
        description="ouch bro",
    )
    embed.set_image(url=kawaii("slap"))

    await ctx.send(embed=embed)

#R U N .
da_muns.start()
allowance.start()
umloop.start()
bot.run(str(os.getenv("DISCORD_TOKEN")))