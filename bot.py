#v1.2.2
#Imports
import discord
import os
import sys
import json
import certifi
import re
import asyncio
import random
import math

from pymongo import *
from bson.objectid import ObjectId
from random import randint, choice
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv
from Levenshtein import ratio as lsr
from decimal import Decimal

load_dotenv()

#MongoDB twash
client = MongoClient(str(os.getenv("MON_STRING")), tlsCAFile=certifi.where())
db = client["CRBOT2Dat"]
warnsc = db["warns"]
doughc = db["money"]
stonksc = db["STONKS!"]

warnid = "000000000000000000010f2c"
moneyid = "0000000000000000000aa289"
stonksid = "000000000000000000066a44"
emojismade = False

#Regexes
mentionre = re.compile(r"<@[0-9]+>")
mentionre2 = re.compile(r"<@![0-9]+>")
iUAT = re.compile(r".*#[0-9]{4}")
iRPr = re.compile(r"[0-9]+d[0-9]+")

#stuff

pf = "."
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=pf,
    strip_after_prefix=True,
    intents=intents
)
with open("dat.json", "r") as f:
    #Load crap from data file
    yeetus = json.loads(f.read())
    curselist = yeetus["curses"]
    answers = yeetus["8ball"]
    quoteslist = yeetus["quotes"]

@tasks.loop(minutes=1)
async def da_muns():
    #Fluctuates STONKS! price
    tempd = stonksc.find_one(
        {
            "_id": ObjectId(stonksid)
        }
    )
    
    tempd["inc"] += random.random() * 12
    tempd["STANKS!"] = bround(abs(((random.random() * 10) + 1) * math.sin(tempd["inc"] * ((random.random() * 4) + 1)) + 6), 3)
    tempd["STANKS!"] += int(tempd["trend"])
    
    #lol 69th line
    if tempd["STANKS!"] < 1:
        tempd["STANKS!"] = 1 + random.random() / 2
        
    tempd["STANKS!"] = abs(tempd["STANKS!"])
        
    stonksc.delete_one(
        {
            "_id": ObjectId(stonksid)
        }
    )
    stonksc.insert_one(tempd)

@tasks.loop(minutes=18)
async def allowance():
    tempd = doughc.find_one(
        {
            "_id": ObjectId(moneyid)
        }
    )
    for item in tempd:
        if item != "_id":
            tempd[item][0] += 0.625
            
    doughc.delete_one(
        {
            "_id": ObjectId(moneyid)
        }
    )
    doughc.insert_one(tempd)

@bot.event
async def on_ready():
    #logged in?
    print(f"CRBOT2 has logged on in to Discord as {bot.user}")
    
    #Remove accidental allowance
    await asyncio.sleep(1)
    tempd = doughc.find_one(
        {
            "_id": ObjectId(moneyid)
        }
    )
    for item in tempd:
        if item != "_id":
            tempd[item][0] -= 0.625
            
    doughc.delete_one(
        {
            "_id": ObjectId(moneyid)
        }
    )
    doughc.insert_one(tempd)

#events
@bot.event
async def on_member_join(member):
    await member.send("""Hello there!
This is an automated message.:robot: 
I am **CRBOT2**, the bot made by **Cuboid_Raptor#7340**.
I have DM'd you to say, welcome to Cuboid's Café!:coffee: 
I sincerely hope you have a great time in the server!:laughing:
You can also interact with me in the server, do be sure to use *[.]* as a command prefix.

We also have many sister servers, servers which you can join as well.
If you are interested in becoming a sister server, DM <@718106301196009544> ig.

* https://discord.gg/8Fhkj7k7aN
* https://discord.gg/aVvtgaqWPN
* https://discord.gg/hVwzNST69k
* https://discord.gg/RkPMG9Rs6k

||P.S. the STONKS! market fluctuates regularly||""")
    channel = get(member.guild.text_channels, name="📢events-announcements📢")
    await channel.send(f"*{member.mention} is here! We hope you have a nice time here, {member.mention}!*")
    
@bot.event
async def on_member_remove(member):
    channel = get(member.guild.text_channels, name="📢events-announcements📢")
    await channel.send(f"*{member.mention} has left. Goodbye, {member.mention}*")

@bot.event
async def on_message(message):
    #When someone messages
    if message.author == bot.user:
        #Is the bot messaging.
        return
    
    else:
        global curselist
        for item in curselist:
            if item in str(message.content).lower().replace("```brainfuck", "```bf"):
                #you swore, idot.
                print("somebody swore uh oh")
                await message.delete()
                await message.channel.send(f"Don't swear, {message.author.mention}")
                
        if ((bot.user.name in message.content) or ((str(bot.user.id) + ">") in message.content)) and not message.content.startswith(str(pf)) and ("announcements" not in message.channel.name.lower()):
            #Did you say bot name?
            await message.channel.send("Hello there, I heard my name?")
                
    await bot.process_commands(message)

#test command
@bot.command()
async def test(ctx):
    """Test command for testing code. Doesn't do anything at the moment."""
    #test for when I need to do dumb stuff
    pass

#Functions
def d(n):
    #precision
    return Decimal(str(n))

def bround(n, a=0):
    #better rounding, I was too lazy to swap names so here is a keyword name
    #(FYI afaik this is bad pratice but I'm LAZ.)
    #I was too lazy to type the "Y".
    if a == 0:
        return int(round(d(n), a))
    
    else:
        return float(round(d(n), a))

def g_role(ctx, rname):
    #Checks if ctx.message.author has any one of the roles in [rname]
    role_t = []
    for item in rname:
        role_t.append(get(ctx.guild.roles, name=str(item)) in ctx.message.author.roles)
        
    out = role_t[0]
    for item in role_t[1:]:
        out = out or item
        
    return out

def isCuboid(ctx):
    #Is message author in ctx me (Cuboid)?
    if (ctx.message.author.id == 588132098875850752):
        return True
    
    else:
        return False
    
def isMention(text):
    #Is text a mention?
    global mentionre, mentionre2
    if mentionre.match(text) == None:
        out = False
    
    else:
        out = True
        
    if mentionre2.match(text) == None:
        out = out or False
    
    else:
        out = out or True
        
    return out
    
def idFromMention(mention):
    #Get User ID from mention
    if mention.startswith("<@!"):
        return str(mention)[3:-1]
    
    else:
        return str(mention)[2:-1]
    
def isCB2(text):
    #Is text CRBOT2
    text = text.strip()
    if (text == str(bot.user.name)) or (text == str(bot.user)) or (text == "<@" + str(bot.user.id) + ">") or (text == "<@!" + str(bot.user.id) + ">"):
        return True
    
    else:
        return False
    
def isUserAndTag(text):
    #Checks if the string contains a username and tag
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
    if text == "" or text.isspace():
        return True
    
    else:
        return False
    
def reasonRet(arr):
    #Returns reason from *args
    reason = " ".join(arr)
                    
    if isEmpty(reason):
        reason = "no good reason at all"
        
    return reason

def rollParse(string):
    #Parses roll number
    global iRPr
    if iRPr.match(string) == None:
        return False
    
    elif len(string.lower().split("d")) != 2:
        return False
    
    else:
        return string.lower().split("d")

#Commands
@bot.command()
async def ping(ctx):
    """pings, this is just for tests"""
    await ctx.send("pong")
    
@bot.command()
async def killcr2(ctx):
    """Kills CRBOT2. Only Cuboid_Raptor#7340 can run this command."""
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
    if isCB2(person):
        await ctx.send(f"I have been vaccinated against no-u's.")
        
    else:
        await ctx.send(f"No u, {person}")

@bot.command(aliases=["8ball"])
async def magic8ball(ctx):
    """Magic 8ball. Ask it questions."""
    global answers
    await ctx.send(choice(answers))
    
@bot.command()
async def quote(ctx):
    """Draws from my quotesbook and prints in chat."""
    global quoteslist
    await ctx.send(choice(quoteslist))
    
@bot.command()
async def shoot(ctx, person):
    """Thingy that allows you to joke shoot people."""
    if isCB2(person):
        await ctx.send(f"stop trying to shoot me you meanie")
    
    elif (ctx.message.author.mention == person) or (ctx.message.author.name == person):
        await ctx.send(f"Don't commit suicide, {ctx.message.author.mention}")
    
    else:
        await ctx.send(f"{ctx.message.author.mention} ( う-´)づ︻╦̵̵̿╤──   \\\\(˚☐˚”)/ {person}")
    
@bot.command()
async def warn(ctx, person, *args):
    """Warn people."""
    if isCB2(person):
        await ctx.send("I HAVEN'T DONE ANYTHING!")
        
    else:
        if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
            if not isMention(person):
                await ctx.send(f"That person is not a mention.")
                
            else:
                reason = reasonRet(args)
                    
                tempd = warnsc.find_one(
                    {
                        "_id": ObjectId(warnid)
                    }
                )
                try:
                    tempd[str(person)] += 1
                    
                except KeyError:
                    tempd[str(person)] = 1
                    
                warnsc.delete_one(
                    {
                        "_id": ObjectId(warnid)
                    }
                )
                warnsc.insert_one(tempd)
                
                await ctx.send(f"{person} has been warned by {ctx.message.author.mention} for {reason}!")
            
        else:
            await ctx.send(f"You do not have the sufficient permissions to run this command.")
    
@bot.command()
async def rmwarn(ctx, person, *args):
    """Remove warn from people."""
    if isCB2(person):
        await ctx.send("I haven't been warned yet. I wouldn't warn myself.")
        
    else:
        if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
            if not isMention(person):
                await ctx.send(f"That person is not a mention.")
                
            else:
                reason = reasonRet(args)
                        
                tempd = warnsc.find_one(
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
                    
                warnsc.delete_one(
                    {
                        "_id": ObjectId(warnid)
                    }
                )
                warnsc.insert_one(tempd)
                
                await ctx.send(f"A warn has been removed from {person} by {ctx.message.author.mention} for {reason}!")
            
        else:
            await ctx.send(f"You do not have the sufficient permissions to run this command.")
        
@bot.command()
async def warns(ctx, person):
    """Shows warns of people"""
    if not isMention(person):
        await ctx.send(f"That person is not a mention.")
        
    else:
        tempd = warnsc.find_one(
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
    if isCuboid(ctx):
        tempd = {
            "_id": ObjectId(warnid)
        }
        warnsc.delete_one(
            {
                #lol 420th line
                "_id": ObjectId(warnid)
            }
        )
        warnsc.insert_one(tempd)
        await ctx.send("All global warns have been cleared.")
        print("All global warns have been cleared.")
        
    else:
        await ctx.send("You don't have the proper permissions to run this command.")

@bot.command()
async def kick(ctx, person, *args):
    """kicky"""
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
    if not rollParse(roll):
        await ctx.send("That isn't a valid dice to roll.")
        
    else:
        proll = rollParse(roll)
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
    if person2 == None:
        person2 = ctx.message.author.mention
    
    personn, person2n = person, person2
    try:
        if isMention(person):
            personn = await bot.fetch_user(idFromMention(personn))
            
            personn = personn.name
            
        if isMention(person2):
            person2n = await bot.fetch_user(idFromMention(person2n))
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
        
    elif perc >= 90:
        compat = "Amazing!"
        
    await ctx.send("\n".join([string, f"Compatibility score: {compat}"]))

@bot.command(aliases=["open-account"])
async def open_account(ctx):
    """Open STONKS! account"""
    person = ctx.message.author
    
    tempd = doughc.find_one(
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
        
    doughc.delete_one(
        {
            "_id": ObjectId(moneyid)
        }
    )
    doughc.insert_one(tempd)
    await ctx.send(f"{person.mention} has been registered with STONKS!!")

@bot.command(aliases=["reset-stonks"])
async def reset_stonks(ctx, silent=False):
    """Reset STONKS! Only Cuboid_Raptor#7340 can run this command"""
    if isCuboid(ctx):
        tempd = stonksc.find_one(
            {
                "_id": ObjectId(stonksid)
            }
        )
        tempd["STANKS!"] = 1
        tempd["inc"] = 0
            
        stonksc.delete_one(
            {
                "_id": ObjectId(stonksid)
            }
        )
        stonksc.insert_one(tempd)
        if silent == False:
            await ctx.send("STONKS! has been resetted!")
            print("STONKS! has been resetted!")
        
    else:
        await ctx.send("You don't have the proper permissions to run that command.")

@bot.command(aliases=["erase-stonks"])
async def erase_stonks(ctx, silent=False):
    """Erase all global STONKS! from shareholders. Only Cuboid_Raptor#7340"""
    if isCuboid(ctx):
        tempd = doughc.find_one(
            {
                "_id": ObjectId(moneyid)
            }
        )
        for item in tempd:
            if item != "_id":
                tempd[item][1] = 0
                
        doughc.delete_one(
            {
                "_id": ObjectId(moneyid)
            }
        )
        doughc.insert_one(tempd)
        
        if silent == False:
            await ctx.send("All global STONKS! records have been erased.")
    
    else:
        await ctx.send("You don't have the proper permissions to run that command")

@bot.command(aliases=["stonks-price"])
async def stonks_price(ctx, silent=False):
    """Print current STONKS! price"""
    if silent == False:
        await ctx.send(
            "The current STONKS! price is: " + str(
                stonksc.find_one(
                    {
                        "_id": ObjectId(stonksid)
                    }
                )["STANKS!"]
            ) + " Cuboid Dollars!"
        )
        
    else:
        return float(
            stonksc.find_one(
                {
                    "_id": ObjectId(stonksid)
                }
            )["STANKS!"]
        )

@bot.command(aliases=["erase-money"])
async def erase_money(ctx, silent=False):
    """Erase all money, globally. Only Cuboid_Raptor#7340 can run this command."""
    if isCuboid(ctx):
        tempd = doughc.find_one(
            {
                "_id": ObjectId(moneyid)
            }
        )
        for item in tempd:
            if item != "_id":
                tempd[item][0] = 100
                
        doughc.delete_one(
            {
                "_id": ObjectId(moneyid)
            }
        )
        doughc.insert_one(tempd)
        
        if silent == False:
            await ctx.send("All global money records have been erased.")
    
    else:
        await ctx.send("You don't have the proper permissions to run that command.")

@bot.command(aliases=["reset-finance"])
async def reset_finance(ctx):
    """Reset all finances. Dangerous command. Ony can be user by Cuboid_Raptor#7340."""
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
    tempd = doughc.find_one(
        {
            "_id": ObjectId(moneyid)
        }
    )
    for item in tempd:
        if item == ctx.message.author.mention:
            if silent == False:
                await ctx.send(f"You have ${tempd[item][0]} and {tempd[item][1]} STONKS!")
                return
            
            else:
                return [tempd[item][0], tempd[item][1]]
            
    await ctx.send("You haven't signed up for STONKS! yet.\nUse .open-account to do that.")

@bot.command()
async def buy(ctx, amount):
    """Buy some STONKS! from STONKS!."""
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
    if (await wallet(ctx, silent=True))[0] < sp:
        await ctx.send("You don't have enough money.")
        
    else:
        tempd = doughc.find_one(
            {
                "_id": ObjectId(moneyid)
            }
        )
        for item in tempd:
            if item == ctx.message.author.mention:
                tempd[item][0] -= sp
                tempd[item][1] += amount
                
        doughc.delete_one(
            {
                "_id": ObjectId(moneyid)
            }
        )
        doughc.insert_one(tempd)
        
        tempd = stonksc.find_one(
            {
                "_id": ObjectId(stonksid)
            }
        )
        
        tempd["trend"] += (random.random() / 2) + 0.75
            
        stonksc.delete_one(
            {
                "_id": ObjectId(stonksid)
            }
        )
        stonksc.insert_one(tempd)
            
        await ctx.send(f"You have bought {amount} STONKS! for ${sp}!")

@bot.command()
async def sell(ctx, amount):
    """Sell some STONKS! from STONKS!."""
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
    if (await wallet(ctx, silent=True))[1] < amount:
        await ctx.send("You don't have enough STONKS! to sell.")
        
    else:
        tempd = doughc.find_one(
            {
                "_id": ObjectId(moneyid)
            }
        )
        for item in tempd:
            if item == ctx.message.author.mention:
                tempd[item][0] += sp
                tempd[item][1] -= amount
                
        doughc.delete_one(
            {
                "_id": ObjectId(moneyid)
            }
        )
        doughc.insert_one(tempd)
        
        tempd = stonksc.find_one(
            {
                "_id": ObjectId(stonksid)
            }
        )
        
        tempd["trend"] -= (random.random() / 2) + 0.75
            
        stonksc.delete_one(
            {
                "_id": ObjectId(stonksid)
            }
        )
        stonksc.insert_one(tempd)
        
        await ctx.send(f"You have sold {amount} STONKS! for ${sp}!")

#R U N .
da_muns.start()
allowance.start()
bot.run(str(os.getenv("DISCORD_TOKEN")))