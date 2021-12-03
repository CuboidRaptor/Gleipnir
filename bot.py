#Imports
import discord
import os
import sys
import dotenv
import json
import certifi
import re

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
                
        if ((bot.user.name in message.content) or ((str(bot.user.id) + ">") in message.content)) and not message.content.startswith(str(pf)):
            #Did you say bot name?
            await message.channel.send("Hello there, I heard my name?")
                
    await bot.process_commands(message)

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
    if (ctx.message.author.id == 588132098875850752) or (ctx.message.author.id == 885900826638442546):
        return True
    
    else:
        return False
    
def isMention(text):
    if text.strip().startswith("<@") and text.strip().endswith(">"):
        mentionre = re.compile(r"<@([0-9]+)>")
        mentionre2 = re.compile(r"<@!([0-9]+)>")
        if mentionre.match(text) == None:
            out = False
        
        else:
            out = True
            
        if mentionre2.match(text) == None:
            out = out or False
        
        else:
            out = out or True
            
        return out

#Commands
@bot.command()
async def ping(ctx):
    #ping pong
    await ctx.send("pong")
    
@bot.command()
async def killcr2(ctx):
    #lol 69th line
    #Kill da bot
    if g_role(ctx, ["Admin"]) or isCuboid(ctx):
        #r u me or r u admin?
        await ctx.send("Ok, Ending...")
        print("Ending...")
        sys.exit()
        
    else:
        await ctx.send("Why are you trying to kill me? :(")
    
@bot.command(aliases=["no-u"])
async def no_u(ctx, person):
    #no u
    await ctx.send(f"No u, {person}")
    
@bot.command()
async def test(ctx):
    #test for when I need to do dumb stuff
    pass

@bot.command(aliases=["8ball"])
async def magic8ball(ctx):
    global answers
    await ctx.send(choice(answers))
    
@bot.command()
async def quote(ctx):
    global quoteslist
    await ctx.send(choice(quoteslist))
    
@bot.command()
async def shoot(ctx, person):
    await ctx.send(f"{ctx.message.author.mention} ( う-´)づ︻╦̵̵̿╤──   \\\\(˚☐˚”)/ {person}")
    
@bot.command()
async def warn(ctx, person):
    if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
        if not isMention(person):
            await ctx.send(f"That person is not a mention.")
            
        else:
            tempd = warnsc.find_one(
                {
                    "_id": ObjectId("000000000000000000010f2c")
                }
            )
            try:
                tempd[str(person)] += 1
                
            except KeyError:
                tempd[str(person)] = 1
                
            warnsc.delete_one(
                {
                    "_id": ObjectId("000000000000000000010f2c")
                }
            )
            warnsc.insert_one(tempd)
            
            await ctx.send(f"{person} has been warned by {ctx.message.author.mention}!")
        
    else:
        await ctx.send(f"You do not have the sufficient permissions to run this command.")
    
@bot.command()
async def rmwarn(ctx, person):
    if g_role(ctx, ["Admin", "Sr. Mod", "Mod"]):
        if not isMention(person):
            await ctx.send(f"That person is not a mention.")
            
        else:
            tempd = warnsc.find_one(
                {
                    "_id": ObjectId("000000000000000000010f2c")
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
                    "_id": ObjectId("000000000000000000010f2c")
                }
            )
            warnsc.insert_one(tempd)
            
            await ctx.send(f"A warn has been removed from {person} by {ctx.message.author.mention}!")
        
    else:
        await ctx.send(f"You do not have the sufficient permissions to run this command.")
    
#R U N .
bot.run(str(os.getenv("DISCORD_TOKEN")))