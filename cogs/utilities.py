import discord
from discord.ext import commands
from .utils_embeds import embed_response

class Utilities(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.hybrid_command(name="ping", description="Check bot latency")
    async def ping(self, ctx):
        await embed_response(ctx, title="🏓 Pong!", description=f"Latency: `{round(self.bot.latency*1000)}ms`", color=discord.Color.green())

async def setup(bot):
    await bot.add_cog(Utilities(bot))
