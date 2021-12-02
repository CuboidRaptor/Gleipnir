#Imports
import discord_interactions as discord
import os
import dotenv
import platform

if platform.system() == "Windows":
    #Probs running on my computer, load env
    dotenv.load_dotenv()
    #Otherwise load from heroku config_var
    
bot = discord.Client(token=str(os.getenv("DISCORD_TOKEN")))

@bot.command(
    name="ping",
    description="ping. pong. ping. pong.",
)
async def ping(ctx):
    await ctx.send("pong")