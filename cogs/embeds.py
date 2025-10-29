import discord
from discord.ext import commands
from .utils_embeds import embed_response

class Embeds(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.hybrid_command(name="embed", description="Send a custom embed")
    async def embed(self, ctx, title: str, description: str, color: str = "blue"):
        color_map = {
            "blue": discord.Color.blurple(), "red": discord.Color.red(),
            "green": discord.Color.green(), "yellow": discord.Color.yellow(),
            "purple": discord.Color.purple(), "orange": discord.Color.orange()
        }
        embed = discord.Embed(title=title, description=description, color=color_map.get(color.lower(), discord.Color.blurple()))
        embed.set_footer(text=f"Sent by {ctx.author}", icon_url=ctx.author.display_avatar.url if ctx.author.display_avatar else discord.Embed.Empty)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Embeds(bot))
