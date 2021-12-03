#Imports
import discord
import os
import sys
import dotenv

from discord.ext import commands

#stuff
dotenv.load_dotenv()
    
bot = commands.Bot(command_prefix=".")
curselist = [
    #avert your eyes
    "fuck",
    "shit",
    "bitch",
    "cunt",
    "nigger"
]

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
        #print(message)
        for item in curselist:
            if item in str(message.content).lower().replace("```brainfuck", "```bf"):
                #you swore, idot.
                print("somebody swore uh oh")
                await message.delete()
                await message.channel.send(f"Don't swear, {message.author.mention}")

#Commands
@bot.command(pass_context=True)
async def ping(ctx):
    print("ping")
    await ctx.send("pong")
    
@bot.command(pass_context=True)
async def killcr2(ctx):
    #Kill da bot
    await ctx.send("Ok, Ending...")
    print("Ending...")
    sys.exit()
    
#R U N .
bot.run(str(os.getenv("DISCORD_TOKEN")))