import discord, json, os
from discord.ext import commands
from .utils_embeds import embed_response

CONFIG_PATH = "data/config.json"

class AutoMessages(commands.Cog):
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

    @commands.hybrid_command(name="setwelcome", description="Set the welcome channel")
    @commands.has_permissions(administrator=True)
    async def setwelcome(self, ctx, channel: discord.TextChannel):
        data = self.read_config()
        data["welcome_channel"] = channel.id
        self.write_config(data)
        await embed_response(ctx, title="🎉 Welcome Channel Set", description=f"Welcome messages → {channel.mention}", color=discord.Color.green())

    @commands.hybrid_command(name="setfarewell", description="Set the farewell channel")
    @commands.has_permissions(administrator=True)
    async def setfarewell(self, ctx, channel: discord.TextChannel):
        data = self.read_config()
        data["farewell_channel"] = channel.id
        self.write_config(data)
        await embed_response(ctx, title="👋 Farewell Channel Set", description=f"Farewell messages → {channel.mention}", color=discord.Color.orange())

    @commands.Cog.listener()
    async def on_member_join(self, member):
        ch_id = self.read_config().get("welcome_channel")
        if ch_id:
            ch = member.guild.get_channel(ch_id)
            if ch:
                embed = discord.Embed(
                    title="🎉 Welcome!",
                    description=f"Welcome to Xenfigs enjoy your stay :)\n{member.mention}",
                    color=discord.Color.green()
                )
                try: embed.set_thumbnail(url=member.display_avatar.url)
                except: pass
                await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        ch_id = self.read_config().get("farewell_channel")
        if ch_id:
            ch = member.guild.get_channel(ch_id)
            if ch:
                await ch.send(embed=discord.Embed(
                    title="👋 Goodbye!",
                    description=f"{member.mention} has left.",
                    color=discord.Color.red()
                ))

async def setup(bot):
    await bot.add_cog(AutoMessages(bot))
