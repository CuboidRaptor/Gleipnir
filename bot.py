#Imports
import discord
import os
import dotenv
import platform

if platform.system() == "Windows":
    #Probs running on my computer, load env
    dotenv.load_dotenv()
    #Otherwise load from heroku config_var
    
bot = discord.Bot()

@bot.slash_comand()
async def ping(ctx):
    await ctx.send("pong")
    
bot.run(str(os.getenv("DISCORD_TOKEN")))