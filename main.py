# ==========================================================
# XenBot Main File (Render-Ready)
# ==========================================================
import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from keep_alive import keep_alive
import threading

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
bot.remove_command("help")

# ----------------------------------------------------------
# Load all cogs
# ----------------------------------------------------------
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if not filename.endswith(".py") or filename.startswith("utils_"):
            continue
        try:
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"✅ Loaded cog: {filename}")
        except Exception as e:
            print(f"❌ Failed to load cog {filename}: {e}")

# ----------------------------------------------------------
# Bot Ready Event
# ----------------------------------------------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"✅ Slash commands synced to guild {GUILD_ID} ({len(synced)} cmds)")
    except Exception as e:
        print(f"⚠️ Slash command sync failed: {e}")

# ----------------------------------------------------------
# Run Flask in separate thread (so Render sees a port)
# ----------------------------------------------------------
def run_flask():
    keep_alive()

threading.Thread(target=run_flask).start()

# ----------------------------------------------------------
# Start Discord bot
# ----------------------------------------------------------
async def main():
    async with bot:
        await load_cogs()
        print("🚀 Attempting Discord login ...")
        try:
            await bot.start(TOKEN)
        except discord.LoginFailure:
            print("❌ Invalid Discord token or wrong environment variable name.")
        except discord.HTTPException as e:
            print(f"❌ Discord HTTP error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Discord login error: {type(e).__name__} - {e}")

if __name__ == "__main__":
    asyncio.run(main())
