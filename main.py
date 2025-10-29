# ==========================================================
# XenBot Main File
# ==========================================================

import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from keep_alive import keep_alive

# ----------------------------------------------------------
# Load environment variables
# ----------------------------------------------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# 🔧 CHANGE THIS to your Discord server ID
GUILD_ID = 1383030583839424584  # Replace with your actual server ID

# ----------------------------------------------------------
# Discord bot setup
# ----------------------------------------------------------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=",", intents=intents)
bot.remove_command("help")  # Disable default help command so custom one works

# ----------------------------------------------------------
# Load all cogs (async-safe)
# ----------------------------------------------------------
async def load_cogs():
    for filename in os.listdir("./cogs"):
        # Skip helper files or non-Python files
        if not filename.endswith(".py") or filename.startswith("utils_"):
            continue
        try:
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"✅ Loaded cog: {filename}")
        except Exception as e:
            print(f"❌ Failed to load cog {filename}: {e}")

# ----------------------------------------------------------
# Event: Bot ready + Slash command sync
# ----------------------------------------------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")

    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)  # Guild sync = instant
        print(f"✅ Slash commands synced to guild {GUILD_ID} ({len(synced)} cmds)")
    except Exception as e:
        print(f"⚠️ Slash command sync failed: {e}")

# ----------------------------------------------------------
# Main bot start
# ----------------------------------------------------------
keep_alive()  # ✅ start Flask first

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


# ----------------------------------------------------------
# Run bot
# ----------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
