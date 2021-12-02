import interactions
import os
import dotenv

dotenv.load_dotenv()
bot = interactions.Client(token=str(os.getenv("DISCORD_TOKEN")))