#v1.2.2
#Imports
import discord
import os
import sys
import dotenv
import json
import certifi
import re
import asyncio

from pymongo import *
from bson.objectid import ObjectId
from random import randint, choice
from discord.ext import commands
from discord.utils import get

dotenv.load_dotenv()

#MongoDB twash
client = MongoClient(str(os.getenv("MON_STRING")), tlsCAFile=certifi.where())
db = client["CRBOT2Dat"]
warnsc = db["warns"]

warnid = "000000000000000000010f2c"
emojismade = False

#Regexes
mentionre = re.compile(r"<@[0-9]+>")
mentionre2 = re.compile(r"<@![0-9]+>")
iUAT = re.compile(r".*#[0-9]{4}")

#stuff

pf = "."
bot = commands.Bot(command_prefix=pf)
with open("dat.json", "r") as f:
    #Load crap from data file
    yeetus = json.loads(f.read())
    curselist = yeetus["curses"]
    answers = yeetus["8ball"]
    quoteslist = yeetus["quotes"]

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
                
        if ((bot.user.name in message.content) or ((str(bot.user.id) + ">") in message.content)) and not message.content.startswith(str(pf)) and ("announcements" not in message.channel.name.lower()):
            #Did you say bot name?
            await message.channel.send("Hello there, I heard my name?")
            #lol 69th line
                
    await bot.process_commands(message)

#test command
@bot.command()
async def test(ctx):
    #test for when I need to do dumb stuff
    pass

#Functions
def g_role(ctx, rname):
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
    if text == "" or text.isspace():
        return True
    
    else:
        return False

#Commands
@bot.command()
async def ping(ctx):
    #ping pong
    await ctx.send("pong")
    
@bot.command()
async def killcr2(ctx):
    #Kill da bot
    if isCuboid(ctx):
        #r u me or r u admin?
        await ctx.send("Ok, Ending...")
        print("Ending...")
        sys.exit()
        
    else:
        await ctx.send("Why are you trying to kill me? :(")
    
@bot.command(aliases=["no-u"])
async def no_u(ctx, person):
    #no u
    if isCB2(person):
        await ctx.send(f"I have been vaccinated against no-u's.")
        
    else:
        await ctx.send(f"No u, {person}")

@bot.command(aliases=["8ball"])
async def magic8ball(ctx):
    #Magic 8-Ball
    global answers
    await ctx.send(choice(answers))
    
@bot.command()
async def quote(ctx):
    #Spews a random quote in chat.
    global quoteslist
    await ctx.send(choice(quoteslist))
    
@bot.command()
async def shoot(ctx, person):
    #SHOOT PERSON BOOM BOOM CHK CHK PEW! POW POW BOOM CRASH POOM BAM!
    if isCB2(person):
        await ctx.send(f"stop trying to shoot me you meanie")
        
    else:
        await ctx.send(f"{ctx.message.author.mention} ( う-´)づ︻╦̵̵̿╤──   \\\\(˚☐˚”)/ {person}")
    
@bot.command()
async def warn(ctx, person, *args):
    #Warn person.
    if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
        if not isMention(person):
            await ctx.send(f"That person is not a mention.")
            
        else:
            reason = " ".join(args)
                
            if isEmpty(reason):
                reason = "no good reason at all"
                
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
    #Remove warn from person.
    if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
        if not isMention(person):
            await ctx.send(f"That person is not a mention.")
            
        else:
            reason = " ".join(args)
                
            if isEmpty(reason):
                reason = "no good reason at all"
                    
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
    #Shows warns of person
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
    if g_role(ctx, ["Admin"]):
        tempd = {
            "_id": ObjectId(warnid)
        }
        warnsc.delete_one(
            {
                "_id": ObjectId(warnid)
            }
        )
        warnsc.insert_one(tempd)

@bot.command()
async def kick(ctx, person, *args):
    #kicky
    if isCB2(str(person)):
        await ctx.send(":(")
        
    else:
        if isMention(person):
            if g_role(ctx, ["Admin", "Sr. Mod"]):
                reason = " ".join(args)
                
                if isEmpty(reason):
                    reason = "no good reason at all"
                    
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
    #get ban'd
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
                reason = " ".join(args)
                
                if isEmpty(reason):
                    reason = "no good reason at all"
                    
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
    #unban ppl
    if isCB2(str(person)):
        await ctx.send("Thanks for the attempt, but I haven't been banned in this server yet :)")
        
    else:
        if isUserAndTag(person):
            if g_role(ctx, ["Admin", "Sr. Mod"]):
                reason = " ".join(args)
                
                if isEmpty(reason):
                    reason = "no good reason at all"
                    
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
    #moot perzen
    if isCB2(str(person)):
        await ctx.send("dood you're a rude guy >:(")
        
    else:
        if isMention(person):
            if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
                reason = " ".join(args)
                    
                if isEmpty(reason):
                    reason = "no good reason at all"
                        
                geeld = ctx.message.guild
                mutedRole = get(
                    #lol 420th line
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
    #unmoot perzen
    if isCB2(str(person)):
        await ctx.send("thanks for trying, but I haven't been muted yet, given how I'm talking to you.")
        
    else:
        if isMention(person):
            if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
                reason = " ".join(args)
                    
                if isEmpty(reason):
                    reason = "no good reason at all"
                        
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
    #tempmoot
    if isCB2(str(person)):
        await ctx.send("stahp go away")
        
    else:
        if isMention(person):
            if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
                
                await mute(ctx, person, *args, silent=True)
                await asyncio.sleep(round(float(time) * 60))
                await unmute(ctx, person, *args, silent=True)  
                await ctx.send(f"{person} has been tempmuted by {ctx.message.author.mention} for {reason} for {time} minutes!")

            else:
                await ctx.send("You don't have the proper permissions to run this command.")

        else:
            await ctx.send("That person isn't a mention.")

#R U N .
bot.run(str(os.getenv("DISCORD_TOKEN")))