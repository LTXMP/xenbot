import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive  # Safe on Render; optional elsewhere

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # needed for prefix cmds + message listeners

# Global prefix set to comma, plus slash commands
bot = commands.Bot(command_prefix=",", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    await bot.tree.sync()
    print("✅ Slash commands synced")

# ---- Load cogs automatically ----
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

# ---- Optional keep-alive web server (works fine on Render) ----
keep_alive()

# ---- Run the bot ----
bot.run(TOKEN)
