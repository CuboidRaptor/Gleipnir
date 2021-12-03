#Imports
import discord
import os
import sys
import dotenv
import json
from random import randint, choice

from discord.ext import commands
from discord.utils import get

#stuff
dotenv.load_dotenv()
    
bot = commands.Bot(command_prefix=".")
with open("dat.json", "r") as f:
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
                
        if bot.user.name in message.content:
            await message.channel.send("Hello there, I heard my name?")
                
    await bot.process_commands(message)

#Functions
def g_role(ctx, rname):
    role_t = get(ctx.guild.roles, name=str(rname))
    if role_t in ctx.message.author.roles:
        return True
    
    else:
        return False

#Commands
@bot.command(pass_context=True)
async def ping(ctx):
    #ping pong
    await ctx.send("pong")
    
@bot.command(pass_context=True)
async def killcr2(ctx):
    #Kill da bot
    if g_role(ctx, "Admin") or (ctx.message.author.id == 588132098875850752) or (ctx.message.author.id == 885900826638442546):
        #r u me or r u admin?
        await ctx.send("Ok, Ending...")
        print("Ending...")
        sys.exit()
        
    else:
        await ctx.send("Why are you trying to kill me? :(")
    
@bot.command(pass_context=True, aliases=["no-u"])
async def no_u(ctx, person):
    #no u
    await ctx.send(f"No u, {person}")
    
@bot.command(pass_context=True)
async def test(ctx):
    #test for when I need to do dumb stuff
    pass

@bot.command(pass_context=True, aliases=["8ball"])
async def magic8ball(ctx):
    global answers
    await ctx.send(choice(answers))
    
#def quote
    
#R U N .
bot.run(str(os.getenv("DISCORD_TOKEN")))