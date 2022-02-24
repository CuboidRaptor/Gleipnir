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
import time
import requests
import motor.motor_asyncio

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

pointsid = "620cfe72f63ae0339129c774"
warnid = "000000000000000000010f2c"
moneyid = "0000000000000000000aa289"
stonksid = "61bf8fc2ad877a0d31f685ea"
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
        dif = time.time() - msgst[message.author.id]

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

        msgst[message.author.id] = time.time()

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
    return "{:,}".format(bround(float(n), a))

def containsEveryone(message):
    #Check if message contains @everyone pings.
    return ("@everyone" in message) or ("@here" in message)

def kawaii(sub):
    #Gets GIF from kawaii.red
    r = requests.get(f"https://kawaii.red/api/gif/{sub}/token={kawaiit}/")
    return str(r.json()['response'])

def fullName(author):
    #Returns name + tag from user/Member object
    return author.name + "#" + author.discriminator

#Commands
@bot.command()
async def ping(ctx):
    """pings, this is just for tests"""
    logging.debug("call: ping()")
    await ctx.send("pong")
    
@bot.command()
async def killcr2(ctx):
    """Kills CRBOT2. Only Cuboid_Raptor#7340 can run this command."""
    logging.debug("call: killcr2()")
    if isCuboid(ctx):
        #r u me?
        await ctx.send("Ok, Ending...")
        print("Ending...")
        sys.exit()
        
    else:
        await ctx.send("Why are you trying to kill me? :(")
    
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

    if isMention(person):
        person = await bot.fetch_user(int(idFromMention(person)))
        person = person.name

    else:
        pass

    embed = discord.Embed(
        title=f"{ctx.message.author.name} has shot {person}!",
        description="oof",
    )
    embed.set_image(url=kawaii("shoot"))

    await ctx.send(embed=embed)
    
@bot.command()
async def warn(ctx, person, *args):
    """Warn people."""
    logging.debug("call: warn()")
    if isCB2(person):
        await ctx.send("I HAVEN'T DONE ANYTHING!")
        
    else:
        if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
            if not isMention(person):
                await ctx.send(f"That person is not a mention.")
                
            else:
                reason = reasonRet(args)
                    
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
            
        else:
            await ctx.send(f"You do not have the sufficient permissions to run this command.")
    
@bot.command()
async def rmwarn(ctx, person, *args):
    """Remove warn from people."""
    logging.debug("call: rmwarn()")
    if isCB2(person):
        await ctx.send("I haven't been warned yet. I wouldn't warn myself.")
        
    else:
        if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
            if not isMention(person):
                await ctx.send(f"That person is not a mention.")
                
            else:
                reason = reasonRet(args)
                        
                tempd = await warnsc.find_one(
                    {
                        "_id": ObjectId(warnid)
                    }
                )
                try:
                    tempd[str(person)] -= 1
                    if tempd[str(person)] < 0:
                        tempd[str(person)] = 0
                        
                        await ctx.send(f"{person} doesn't have any warns.")
                        return
                    
                except KeyError:
                    await ctx.send(f"{person} doesn't have any warns.")
                    return

                await warnsc.replace_one(
                    {
                        "_id": ObjectId(warnid)
                    },
                    tempd,
                    upsert=True
                )
                
                await ctx.send(f"A warn has been removed from {person} by {ctx.message.author.mention} for {reason}!")
            
        else:
            await ctx.send(f"You do not have the sufficient permissions to run this command.")
        
@bot.command()
async def warns(ctx, person):
    """Shows warns of people"""
    logging.debug("call: warns()")
    if not isMention(person):
        await ctx.send(f"That person is not a mention.")
        
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
        await ctx.send("You don't have the proper permissions to run this command.")

@bot.command()
async def kick(ctx, person, *args):
    """kicky"""
    logging.debug("call: kick()")
    if isCB2(str(person)):
        await ctx.send(":(")
        
    else:
        if isMention(person):
            if g_role(ctx, ["Admin", "Sr. Mod"]):
                reason = reasonRet(args)
                    
                user = await ctx.message.guild.query_members(user_ids=[str(idFromMention(person))])
                user = user[0]
                await user.kick(reason=reason)
                await ctx.send(f"{person} was kicked by {ctx.message.author.mention} for {reason}!")
            
            else:
                await ctx.send("You don't have the proper permissions to do that.")
            
        else:
            await ctx.send("That person isn't a mention.")

@bot.command()
async def ban(ctx, person, *args):
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
            if g_role(ctx, ["Admin", "Sr. Mod"]):
                reason = reasonRet(args)
                    
                user = await ctx.message.guild.query_members(user_ids=[str(idFromMention(person))])
                try:
                    user = user[0]
                    
                except IndexError:
                    await ctx.send("hey bub that person doesn't exist, or some error has been thrown")
                    await ctx.send("(if that person does exist, notify Cuboid_Raptor#7340)")
                    return
                
                await user.ban(reason=reason)
                await ctx.send(f"{person} was banned by {ctx.message.author.mention} for {reason}!")
            
            else:
                await ctx.send("You don't have the proper permissions to do that.")
            
        else:
            await ctx.send("That person isn't a mention.")

@bot.command()
async def unban(ctx, person, *args):
    """Unban people."""
    logging.debug("call: unban()")
    if isCB2(str(person)):
        await ctx.send("Thanks for the attempt, but I haven't been banned in this server yet :)")
        
    else:
        if isUserAndTag(person):
            if g_role(ctx, ["Admin", "Sr. Mod"]):
                reason = reasonRet(args)
                    
                mname, mdisc = person.split("#")
                
                banned_users = await ctx.message.guild.bans()
                for ban_entry in banned_users:
                    user = ban_entry.user
                    
                    if (user.name, user.discriminator) == (mname, mdisc):
                        await ctx.message.guild.unban(user)
                        await ctx.message.channel.send(f"{user.mention} has been unbanned by {ctx.message.author.mention} for {reason}!")
                        
                    
            
            else:
                await ctx.send("You don't have the proper permissions to do that.")
            
        else:
            await ctx.send("That person isn't a Username and Tag seperated by \"#\".")

@bot.command()
async def mute(ctx, person, *args, **kwargs):
    """Mute people until unmuted."""
    logging.debug("call: mute()")
    if isCB2(str(person)):
        await ctx.send("dood you're a rude guy >:(")
        
    else:
        if isMention(person):
            if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
                reason = reasonRet(args)
                        
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
                    await ctx.send("This bot's role/permissions need to be higher in the hierarchy, or some error has occured.")
                    return
                
                if not kwargs.get(
                    "silent",
                    False
                ):
                    await ctx.send(f"{person} has been muted by {ctx.message.author.mention} for {reason}!")

            else:
                await ctx.send("You don't have the proper permissions to run this command.")

        else:
            await ctx.send("That person isn't a mention.")

@bot.command()
async def unmute(ctx, person, *args, **kwargs):
    """Unmute people."""
    logging.debug("call: unmute()")
    if isCB2(str(person)):
        await ctx.send("thanks for trying, but I haven't been muted yet, given how I'm talking to you.")
        
    else:
        if isMention(person):
            if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
                reason = reasonRet(args)
                        
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
                    await ctx.send("That person is already unmuted.")
                    return
                
                if not kwargs.get(
                    "silent",
                    False
                ):
                    await ctx.send(f"{person} has been unmuted by {ctx.message.author.mention} for {reason}!")

            else:
                await ctx.send("You don't have the proper permissions to run this command.")

        else:
            await ctx.send("That person isn't a mention.")

@bot.command()
async def tempmute(ctx, person, time, *args):
    """Temporarily mute people."""
    logging.debug("call: tempmute()")
    if isCB2(str(person)):
        await ctx.send("stahp go away")
        
    else:
        if isMention(person):
            if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
                reason = reasonRet(args)
                    
                await mute(ctx, person, *args, silent=True)
                await ctx.send(f"{person} has been tempmuted by {ctx.message.author.mention} for {reason} for {time} minutes!")
                await asyncio.sleep(bround(float(time) * 60))
                await unmute(ctx, person, *args, silent=True)  

            else:
                await ctx.send("You don't have the proper permissions to run this command.")

        else:
            await ctx.send("That person isn't a mention.")

@bot.command()
async def roll(ctx, roll):
    """Roll die."""
    logging.debug("call: roll()")
    if not rollParse(roll):
        await ctx.send("That isn't a valid dice to roll.")
        
    else:
        proll = rollParse(roll)
        proll[0], proll[1] = proll[0].replace(",", ""), proll[1].replace(",", "")
        s = 0
        try:
            for i in range(0, int(proll[0])):
                s += random.randint(1, int(proll[1]))
                
            await ctx.send(f"{ctx.message.author.mention} rolled {roll} and got {s}")
            
        except ValueError:
            await ctx.send("That isn't a valid roll.")

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
        try:
            if isMention(person):
                personn = await bot.fetch_user(int(idFromMention(personn)))
                
                personn = personn.name
                
            if isMention(person2):
                person2n = await bot.fetch_user(int(idFromMention(person2n)))
                person2n = person2n.name
                
        except discord.errors.NotFound:
            await ctx.send("Couldn't find names of one or more mentions.")
            return
            
        perc = (lsr(personn, person2n) * 100)
        perc += ((-perc) ** (3 / 4)) + 32
        perc = bround(perc.real)
        
        if perc > 100:
            perc = 100
            
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
            
        await ctx.send("\n".join([string, f"Compatibility score: {compat}"]))

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
        await ctx.send("You already have a STONKS! account.")
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
        await ctx.send("You don't have the proper permissions to run that command.")

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
        await ctx.send("You don't have the proper permissions to run that command")

@bot.command(aliases=["stonks-price"])
async def stonks_price(ctx, silent=False):
    """Print current STONKS! price"""
    logging.debug("call: stonks_price()")
    if silent == False:
        await ctx.send(
            "The current STONKS! price is: " + str(
                numform(
                    await stonksc.find_one(
                        {
                            "_id": ObjectId(stonksid)
                        }
                    )["STANKS!"],
                    3
                )
            ) + " Cuboid Dollars!"
        )
        
    else:
        return float(
            await stonksc.find_one(
                {
                    "_id": ObjectId(stonksid)
                }
            )["STANKS!"]
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
        await ctx.send("You don't have the proper permissions to run that command.")

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
        await ctx.send("You don't have the proper permissions to run that command.")

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
            
    await ctx.send("You haven't signed up for STONKS! yet.\nUse .open-account to do that.")

@bot.command()
async def buy(ctx, amount):
    """Buy some STONKS! from STONKS!."""
    logging.debug("call: buy()")
    try:
        amount = int(bround(float(amount)))
        if amount < 1:
            await ctx.send(f"bruh u can't buy {amount} STONKS!.")
            return
        
    except ValueError:
        await ctx.send(f"bruh u can't buy \"{amount}\" STONKS!.")
        return
        
    sp = await stonks_price(ctx, silent=True)
    sp *= amount
    sp = bround(sp, 3)
    if (await wallet(ctx, silent=True))[0] < sp:
        await ctx.send("You don't have enough money.")
        
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
            await ctx.send(f"bruh u can't sell {amount} STONKS!.")
            return
        
    except ValueError:
        await ctx.send(f"bruh u can't sell \"{amount}\" STONKS!.")
        return
        
    sp = await stonks_price(ctx, silent=True)
    sp *= amount
    sp = bround(sp, 3)
    
    if (await wallet(ctx, silent=True))[1] < amount:
        await ctx.send("You don't have enough STONKS! to sell.")
        
    else:
        tempd = await doughc.find_one(
            {
                "_id": ObjectId(moneyid)
            }
        )
        for item in tempd:
            if item == ctx.message.author.mention:
                if (tempd[item][0] + sp) > 2000000000:
                    await ctx.send("You have hit the money limit. Try giving some away.")
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
async def give(ctx, tgt, amount):
    """give da STONKS! muns to someone else"""
    logging.debug("call: give()")
    if isMention(tgt):
        tgt = f"<@{idFromMention(tgt)}>"
        try:
            amount = bround(float(amount), 3)
            if amount < 1:
                await ctx.send(f"bruh u can't sell {amount} STONKS!.")
                return
            
        except ValueError:
            await ctx.send(f"bruh u can't sell \"{amount}\" STONKS!.")
            return
        
        if (await wallet(ctx, silent=True))[0] < amount:
            await ctx.send("You don't have enough money to give.")
            
        else:
            tempd = await doughc.find_one(
                {
                    "_id": ObjectId(moneyid)
                }
            )
            
            try:
                this_is_a_stupid_variable = tempd["<@" + idFromMention(tgt) + ">"]
                del this_is_a_stupid_variable
                
            except KeyError as error:
                await ctx.send("That person hasn't signed up for STONKS! yet.")
                return
            
            for item in tempd:
                if item == ctx.message.author.mention:
                    tempd[item][0] -= amount
                    
                elif item == tgt:
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
            
            await ctx.send(f"You have given ${numform(amount, 3)} to {tgt}")
            
    else:
        await ctx.send("That person isn't a mention.")

@bot.command()
async def points(ctx, user=None, silent=False):
    """Show number of points of others, or yourself."""
    logging.debug("call: points()")
    if user == None:
        isSelf = True
        user = ctx.message.author.id

    elif not isMention(user):
        if not silent:
            await ctx.send("That person isn't a mention.")

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
async def givepoints(ctx, person, pointa):
    """Give points to others."""
    logging.debug("call: give()")

    pointa = bround(pointa)

    tempd = await pointsc.find_one(
        {
            "_id": ObjectId(pointsid)
        }
    )

    if not isMention(person):
        await ctx.send("That person isn't a mention.")
        return

    hasp = await points(ctx, silent=True)

    if hasp < pointa:
        await ctx.send("You cannot afford to send that many Cuboid Points.")
        return

    tempd[str(ctx.message.author.id)] -= int(pointa)

    if tempd[str(ctx.message.author.id)] < 0:
        logging.error("PANIC!!!!! CALCULATIONS DON'T MAKE SENSE")
        raise ValueError("WTF")
        return

    try:
        tempd[str(idFromMention(person))] += int(pointa)

    except KeyError:
        tempd[str(idFromMention(person))] = int(pointa)

    await pointsc.replace_one(
        {
            "_id": ObjectId(pointsid)
        },
        tempd,
        upsert=True
    )

    await ctx.send(f"{pointa} cp have been sent to {person}!")

@bot.command()
async def coinflip(ctx):
    if random.randint(0, 1):
        await ctx.send("You flipped a coin and got heads!")

    else:
        await ctx.send("You flipped a coin and got tails!")

#R U N .
da_muns.start()
allowance.start()
bot.run(str(os.getenv("DISCORD_TOKEN")))