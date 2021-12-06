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

from pymongo import *
from bson.objectid import ObjectId
from random import randint, choice
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv
from Levenshtein import ratio as lsr

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
bot = commands.Bot(command_prefix=pf)
with open("dat.json", "r") as f:
    #Load crap from data file
    yeetus = json.loads(f.read())
    curselist = yeetus["curses"]
    answers = yeetus["8ball"]
    quoteslist = yeetus["quotes"]

@tasks.loop(minutes=1)
async def da_muns():
    tempd = stonksc.find_one(
        {
            "_id": ObjectId(stonksid)
        }
    )
    tempd["instability"] += random.randint(-5, 5)
    tempd["trend"] += tempd["instability"]
    tempd["STANKS!"] += abs(tempd["trend"])
        
    stonksc.delete_one(
        {
            "_id": ObjectId(stonksid)
        }
    )
    stonksc.insert_one(tempd)

@bot.event
async def on_ready():
    #logged in?
    print(f"CRBOT2 has logged on in to Discord as {bot.user}")

#events
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
                #lol 69th line
                
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
    if (ctx.message.author.id == 588132098875850752) or (ctx.message.author.id == 885900826638442546):
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
                "_id": ObjectId(warnid)
            }
        )
        warnsc.insert_one(tempd)
        
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
                        #lol 420th line
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
                await asyncio.sleep(round(float(time) * 60))
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
    perc = round(perc.real)
    
    if perc > 100:
        perc = 100
    await ctx.send(f"{person} x {person2} ship compatibility percentage: {perc}%")

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
        tempd[person.mention] = 100
        
    doughc.delete_one(
        {
            "_id": ObjectId(moneyid)
        }
    )
    doughc.insert_one(tempd)
    await ctx.send(f"{person.mention} has been registered with STONKS!!")

@bot.command(aliases=["reset-stonks"])
async def reset_stonks(ctx):
    if isCuboid(ctx):
        tempd = stonksc.find_one(
            {
                "_id": ObjectId(stonksid)
            }
        )
        tempd["STANKS!"] = 1
        tempd["trend"] = 0
        tempd["instability"] = 0
            
        stonksc.delete_one(
            {
                "_id": ObjectId(stonksid)
            }
        )
        stonksc.insert_one(tempd)
        await ctx.send("STONKS! has been resetted!")
        
    else:
        await ctx.send("You don't have the proper permissions to run that command.")

#R U N .
da_muns.start()
bot.run(str(os.getenv("DISCORD_TOKEN")))