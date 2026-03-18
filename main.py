from disnake.ext import commands
from disnake import Intents, File, Member, Embed, Color, FFmpegPCMAudio

import logging
import os
from dotenv import load_dotenv

# LOGGING
logger = logging.getLogger("nextcord")
logging.basicConfig(level=logging.INFO)
handler = logging.FileHandler(filename="nextcord.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

# BOT
INTENTS = Intents.all()
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Token not found. Set the BOT_TOKEN env variable")

bot = commands.Bot(command_prefix=".", intents=INTENTS)

# IMPORTING COGS
bot.load_extension("cogs.moderation")
bot.load_extension("cogs.math")
bot.load_extension("cogs.fun")
bot.load_extension("cogs.misc")

bot.run(TOKEN)