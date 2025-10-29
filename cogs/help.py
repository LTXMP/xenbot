import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.hybrid_command(name="help", description="Show all commands")
    async def help(self, ctx):
        embed = discord.Embed(title="🤖 Help Menu", description="Prefix is **`,`**. Slash commands also available.", color=discord.Color.blurple())
        embed.add_field(name="🛡️ Moderation", value="`,warn` `,warnings` `,clearwarnings` `,mute` `,unmute` `,lock` `,linkprotection`", inline=False)
        embed.add_field(name="🎫 Tickets", value="`,ticketpanel`", inline=False)
        embed.add_field(name="🎉 Giveaways", value="`,giveaway` `,giveawaylist` `,giveawayinfo` `,giveawayend` `,reroll` `,setgiveawaypurge`", inline=False)
        embed.add_field(name="🪵 Setup", value="`,setlog` `,setwelcome` `,setfarewell`", inline=False)
        embed.add_field(name="🔐 Permissions", value="`,setroleperm` `,removeroleperm` `,listperms`", inline=False)
        embed.add_field(name="📢 Embeds & Utils", value="`,embed` `,ping` `,help` `,cmds`", inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="cmds", description="Show command list (alias of help)")
    async def cmds(self, ctx):
        await self.help(ctx)

async def setup(bot):
    await bot.add_cog(Help(bot))
