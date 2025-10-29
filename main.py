import discord
from discord.ext import commands
import os, asyncio
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# 🔧 Change this to your server ID (right-click server → Copy ID)
GUILD_ID = 1383030583839424584 # <--- 🔧 CHANGE THIS

intents = discord.Intents.all()

# Supports slash + prefix commands
bot = commands.Bot(command_prefix=",", intents=intents)
bot.remove_command("help")  # disables default help to allow your custom one

# -----------------------------------------------------
# Load all cogs (async-safe)
# -----------------------------------------------------
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if not filename.endswith(".py") or filename.startswith("utils_"):
            continue  # skip helper files
        try:
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"✅ Loaded cog: {filename}")
        except Exception as e:
            print(f"❌ Failed to load cog {filename}: {e}")

# -----------------------------------------------------
# On Ready Event
# -----------------------------------------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")

    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"✅ Slash commands synced to guild {GUILD_ID} ({len(synced)} cmds)")
    except Exception as e:
        print(f"⚠️ Slash command sync failed: {e}")

# -----------------------------------------------------
# Main async runner
# -----------------------------------------------------
async def main():
    async with bot:
        await load_cogs()
        keep_alive()  # start the Flask server
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
