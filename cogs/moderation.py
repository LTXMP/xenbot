import discord, json, os
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from .utils_embeds import embed_response

WARN_FILE = "data/warnings.json"
MUTE_FILE = "data/mutes.json"
LINK_FILE = "data/link_protection.json"
CONFIG_PATH = "data/config.json"

ALLOWED_ROLES = [
    "Administrator",
    "Moderator"
]

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        os.makedirs("data", exist_ok=True)
        for f in [WARN_FILE, MUTE_FILE, LINK_FILE]:
            if not os.path.exists(f):
                with open(f, "w", encoding="utf-8") as file:
                    json.dump({}, file)
        self.check_mutes.start()

    # --- helpers ---
    def read_json(self, path):
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    def write_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

    async def has_mod_role(self, member): return any(r.name in ALLOWED_ROLES for r in member.roles)

    async def get_log_channel(self, guild):
        if not os.path.exists(CONFIG_PATH): return None
        with open(CONFIG_PATH, "r", encoding="utf-8") as f: data = json.load(f)
        ch_id = data.get("log_channel"); return guild.get_channel(ch_id) if ch_id else None

    async def log_embed(self, guild, title, desc, color):
        ch = await self.get_log_channel(guild)
        if ch:
            embed = discord.Embed(title=title, description=desc, color=color)
            embed.timestamp = datetime.utcnow()
            await ch.send(embed=embed)

    def parse_duration(self, text: str) -> int:
        try:
            n, u = int(text[:-1]), text[-1]
            return n * (60 if u=="m" else 3600 if u=="h" else 86400 if u=="d" else 0)
        except: return 0

    # --- warnings ---
    @commands.hybrid_command(name="warn", description="Warn a user")
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if not await self.has_mod_role(ctx.author):
            return await embed_response(ctx, title="❌ Permission Denied", color=discord.Color.red())
        data = self.read_json(WARN_FILE)
        data.setdefault(str(member.id), []).append({"reason": reason, "moderator": ctx.author.id, "time": datetime.utcnow().isoformat()})
        self.write_json(WARN_FILE, data)
        await embed_response(ctx, title="⚠️ User Warned", description=f"{member.mention} warned for **{reason}**", color=discord.Color.orange())
        await self.log_embed(ctx.guild, "⚠️ User Warned", f"**User:** {member.mention}\n**Reason:** {reason}\n**Moderator:** {ctx.author.mention}", discord.Color.orange())

    @commands.hybrid_command(name="warnings", description="View warnings for a user")
    async def warnings(self, ctx, member: discord.Member):
        if not await self.has_mod_role(ctx.author):
            return await embed_response(ctx, title="❌ Permission Denied", color=discord.Color.red())
        warns = self.read_json(WARN_FILE).get(str(member.id), [])
        if not warns:
            return await embed_response(ctx, title="ℹ️ No Warnings", description=f"{member.mention} has no warnings.", color=discord.Color.blurple())
        embed = discord.Embed(title=f"⚠️ Warnings for {member}", color=discord.Color.gold())
        for i, w in enumerate(warns, 1):
            embed.add_field(name=f"#{i} • {w['time'][:19].replace('T',' ')}", value=f"**Reason:** {w['reason']}", inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="clearwarnings", description="Clear all warnings for a user")
    async def clearwarnings(self, ctx, member: discord.Member):
        if not await self.has_mod_role(ctx.author):
            return await embed_response(ctx, title="❌ Permission Denied", color=discord.Color.red())
        data = self.read_json(WARN_FILE)
        if str(member.id) in data:
            del data[str(member.id)]
            self.write_json(WARN_FILE, data)
            await embed_response(ctx, title="🧹 Cleared Warnings", description=f"All warnings cleared for {member.mention}", color=discord.Color.green())
            await self.log_embed(ctx.guild, "🧹 Warnings Cleared", f"{ctx.author.mention} cleared warnings for {member.mention}", discord.Color.green())
        else:
            await embed_response(ctx, title="ℹ️ No Warnings", description=f"{member.mention} has no warnings.", color=discord.Color.blurple())

    # --- lock ---
    @commands.hybrid_command(name="lock", description="Lock this channel for @everyone (read-only, invites allowed)")
    async def lock(self, ctx):
        if not await self.has_mod_role(ctx.author):
            return await embed_response(ctx, title="❌ Permission Denied", color=discord.Color.red())
        channel = ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        overwrite.add_reactions = False
        overwrite.view_channel = True
        overwrite.read_message_history = True
        overwrite.create_instant_invite = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await embed_response(ctx, title="🔒 Channel Locked", description=f"{channel.mention} is now read-only for @everyone.", color=discord.Color.blurple())
        await self.log_embed(ctx.guild, "🔒 Channel Locked", f"{ctx.author.mention} locked {channel.mention}", discord.Color.blurple())

    # --- link protection ---
    @commands.hybrid_command(name="linkprotection", description="Toggle link blocking in this channel")
    async def linkprotection(self, ctx):
        if not await self.has_mod_role(ctx.author):
            return await embed_response(ctx, title="❌ Permission Denied", color=discord.Color.red())
        data = self.read_json(LINK_FILE); cid = str(ctx.channel.id)
        if cid in data: 
            del data[cid]; state, color = "disabled", discord.Color.red()
        else:
            data[cid] = True; state, color = "enabled", discord.Color.green()
        self.write_json(LINK_FILE, data)
        await embed_response(ctx, title="🔗 Link Protection", description=f"Link protection **{state}** in {ctx.channel.mention}", color=color)
        await self.log_embed(ctx.guild, "🔗 Link Protection Toggled", f"{ctx.author.mention} **{state}** link protection in {ctx.channel.mention}", color)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot: return
        # Skip ticket channels by prefix (support-/buy-). Adjust if you use different naming.
        if message.channel.name.startswith(("support-", "buy-")):
            return
        data = self.read_json(LINK_FILE)
        if str(message.channel.id) not in data:
            return
        if "http://" in message.content or "https://" in message.content:
            if await self.has_mod_role(message.author):
                return
            try:
                await message.delete()
                await message.channel.send(
                    embed=discord.Embed(title="🚫 Link Removed", description=f"{message.author.mention}, links are not allowed here.", color=discord.Color.red()),
                    delete_after=6
                )
            except: pass

    # --- mutes ---
    @commands.hybrid_command(name="mute", description="Mute a user for 10m, 1h, 1d")
    async def mute(self, ctx, member: discord.Member, duration: str, *, reason="No reason provided"):
        if not await self.has_mod_role(ctx.author):
            return await embed_response(ctx, title="❌ Permission Denied", color=discord.Color.red())
        seconds = self.parse_duration(duration)
        if not seconds:
            return await embed_response(ctx, title="❌ Invalid Duration", description="Use 10m, 1h, or 1d.", color=discord.Color.red())
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted", reason="Timed mutes")
            for ch in ctx.guild.channels:
                await ch.set_permissions(mute_role, send_messages=False, speak=False, add_reactions=False)
        await member.add_roles(mute_role, reason=reason)
        until = datetime.utcnow() + timedelta(seconds=seconds)
        mutes = self.read_json(MUTE_FILE); mutes[str(member.id)] = {"until": until.isoformat(), "guild": ctx.guild.id}
        self.write_json(MUTE_FILE, mutes)
        await embed_response(ctx, title="🔇 User Muted", description=f"{member.mention} muted for `{duration}`\nReason: {reason}", color=discord.Color.orange())
        await self.log_embed(ctx.guild, "🔇 User Muted", f"**User:** {member.mention}\n**Duration:** {duration}\n**Reason:** {reason}\n**Moderator:** {ctx.author.mention}", discord.Color.orange())

    @commands.hybrid_command(name="unmute", description="Unmute a user")
    async def unmute(self, ctx, member: discord.Member):
        if not await self.has_mod_role(ctx.author):
            return await embed_response(ctx, title="❌ Permission Denied", color=discord.Color.red())
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role and mute_role in member.roles:
            await member.remove_roles(mute_role)
            mutes = self.read_json(MUTE_FILE); mutes.pop(str(member.id), None); self.write_json(MUTE_FILE, mutes)
            await embed_response(ctx, title="🔊 User Unmuted", description=f"{member.mention} has been unmuted.", color=discord.Color.green())
            await self.log_embed(ctx.guild, "🔊 User Unmuted", f"{member.mention} unmuted by {ctx.author.mention}", discord.Color.green())
        else:
            await embed_response(ctx, title="ℹ️ Not Muted", description=f"{member.mention} is not muted.", color=discord.Color.blurple())

    @tasks.loop(minutes=1)
    async def check_mutes(self):
        mutes = self.read_json(MUTE_FILE); changed = False
        for uid, info in list(mutes.items()):
            until = datetime.fromisoformat(info["until"])
            if datetime.utcnow() >= until:
                guild = self.bot.get_guild(info["guild"])
                if not guild: del mutes[uid]; changed = True; continue
                member = guild.get_member(int(uid))
                if member:
                    mute_role = discord.utils.get(guild.roles, name="Muted")
                    if mute_role and mute_role in member.roles:
                        await member.remove_roles(mute_role)
                        await self.log_embed(guild, "🔊 Auto Unmute", f"{member.mention} auto-unmuted.", discord.Color.green())
                del mutes[uid]; changed = True
        if changed: self.write_json(MUTE_FILE, mutes)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
