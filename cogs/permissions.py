import discord, json, os
from discord.ext import commands
from .utils_embeds import embed_response

PERMS_FILE = "data/permissions.json"

class Permissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(PERMS_FILE):
            with open(PERMS_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def read_perms(self):
        with open(PERMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def write_perms(self, data):
        with open(PERMS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @commands.hybrid_command(name="setroleperm", description="Allow a role to use a command")
    @commands.has_permissions(administrator=True)
    async def setroleperm(self, ctx, command_name: str, role: discord.Role):
        data = self.read_perms()
        data.setdefault(command_name.lower(), [])
        if role.id not in data[command_name.lower()]:
            data[command_name.lower()].append(role.id)
        self.write_perms(data)
        await embed_response(ctx, title="🔐 Permission Added", description=f"{role.mention} → `/{command_name}`", color=discord.Color.green())

    @commands.hybrid_command(name="removeroleperm", description="Remove a role's access to a command")
    @commands.has_permissions(administrator=True)
    async def removeroleperm(self, ctx, command_name: str, role: discord.Role):
        data = self.read_perms()
        if command_name.lower() in data and role.id in data[command_name.lower()]:
            data[command_name.lower()].remove(role.id)
            self.write_perms(data)
            await embed_response(ctx, title="🧹 Permission Removed", description=f"{role.mention} ✖ `/{command_name}`", color=discord.Color.orange())
        else:
            await embed_response(ctx, title="ℹ️ No Access Found", description=f"{role.mention} did not have access to `/{command_name}`", color=discord.Color.blurple())

    @commands.hybrid_command(name="listperms", description="List command permissions")
    @commands.has_permissions(administrator=True)
    async def listperms(self, ctx):
        data = self.read_perms()
        if not data:
            return await embed_response(ctx, title="🔐 Permissions", description="No custom permissions set.", color=discord.Color.blurple())
        embed = discord.Embed(title="🔐 Command Permissions", color=discord.Color.blurple())
        for cmd, roles in data.items():
            embed.add_field(name=f"/{cmd}", value=", ".join(f"<@&{r}>" for r in roles) or "No roles", inline=False)
        await ctx.send(embed=embed)

    async def can_run(self, command_name, member: discord.Member):
        allowed = self.read_perms().get(command_name.lower())
        if not allowed:
            return True
        return any(r.id in allowed for r in member.roles)

async def setup(bot):
    await bot.add_cog(Permissions(bot))
