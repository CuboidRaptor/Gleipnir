#Imports
import discord
import os
import sys
import dotenv

from discord.ext import commands

#stuff
dotenv.load_dotenv()
    
bot = commands.Bot()

#Commands
@bot.slash_comand()
async def ping(ctx):
    #ping pong
    await ctx.send("pong")
    
@bot.slash_comand()
async def killcr2(ctx):
    #Kill da bot
    sys.exit()
    
#R U N .
bot.run(str(os.getenv("DISCORD_TOKEN")))