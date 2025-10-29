import discord, json, os
from discord.ext import commands
from .utils_embeds import embed_response

CONFIG_PATH = "data/config.json"

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({"log_channel": None, "welcome_channel": None, "farewell_channel": None}, f)

    def read_config(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def write_config(self, data):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    async def get_log_channel(self, guild):
        data = self.read_config()
        ch_id = data.get("log_channel")
        return guild.get_channel(ch_id) if ch_id else None

    @commands.hybrid_command(name="setlog", description="Set the central logging channel")
    @commands.has_permissions(administrator=True)
    async def setlog(self, ctx, channel: discord.TextChannel):
        data = self.read_config()
        data["log_channel"] = channel.id
        self.write_config(data)
        await embed_response(ctx, title="🪵 Log Channel Set", description=f"Logs will go to {channel.mention}", color=discord.Color.green())

    @commands.Cog.listener()
    async def on_member_join(self, member):
        ch = await self.get_log_channel(member.guild)
        if ch:
            embed = discord.Embed(title="👋 Member Joined", description=f"{member.mention} joined.", color=discord.Color.green())
            await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        ch = await self.get_log_channel(member.guild)
        if ch:
            embed = discord.Embed(title="🚪 Member Left", description=f"**{member}** left.", color=discord.Color.red())
            await ch.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logging(bot))
