import discord, json, os, random
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone
from .utils_embeds import embed_response

GIVEAWAY_FILE = "data/giveaways.json"
GCFG_FILE = "data/giveaways_config.json"
CONFIG_PATH = "data/config.json"

os.makedirs("data", exist_ok=True)
if not os.path.exists(GIVEAWAY_FILE): json.dump({}, open(GIVEAWAY_FILE, "w", encoding="utf-8"))
if not os.path.exists(GCFG_FILE): json.dump({"purge_days": 7}, open(GCFG_FILE, "w", encoding="utf-8"))

def parse_time(s: str) -> int:
    try:
        u = s[-1]; n = int(s[:-1])
        return n * (60 if u=="m" else 3600 if u=="h" else 86400 if u=="d" else 0)
    except: return 0

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()
        self.purge_giveaways.start()

    # IO helpers
    def read(self):  return json.load(open(GIVEAWAY_FILE, "r", encoding="utf-8"))
    def write(self,d): json.dump(d, open(GIVEAWAY_FILE, "w", encoding="utf-8"), indent=4)
    def read_cfg(self): return json.load(open(GCFG_FILE, "r", encoding="utf-8"))
    def write_cfg(self,c): json.dump(c, open(GCFG_FILE, "w", encoding="utf-8"), indent=4)

    async def log_channel(self, guild):
        if not os.path.exists(CONFIG_PATH): return None
        data = json.load(open(CONFIG_PATH, "r", encoding="utf-8"))
        ch_id = data.get("log_channel")
        return guild.get_channel(ch_id) if ch_id else None

    async def end_giveaway(self, guild: discord.Guild, msg_id: int, ended_by: discord.Member | None = None):
        data = self.read(); g = data.get(str(msg_id))
        if not g: return
        ch = guild.get_channel(g["channel_id"])
        if not ch: return
        try:
            msg = await ch.fetch_message(msg_id)
        except: return

        entrants = []
        for r in msg.reactions:
            if str(r.emoji) == "🎉":
                entrants = [u async for u in r.users() if not u.bot]
                break

        if entrants:
            winners = random.sample(entrants, min(len(entrants), g["winners"]))
            winner_mentions = ", ".join(u.mention for u in winners)
        else:
            winners = []; winner_mentions = "No participants 😢"

        host = guild.get_member(g.get("host"))
        end_embed = discord.Embed(
            title="🎊 Giveaway Ended!",
            description=f"**Prize:** {g['prize']}\n**Winners:** {winner_mentions}\n**Hosted by:** {host.mention if host else 'Unknown'}" + (f"\n**Ended by:** {ended_by.mention}" if ended_by else ""),
            color=discord.Color.gold()
        )
        await msg.edit(embed=end_embed)
        await ch.send(embed=discord.Embed(
            title="🏆 Winners",
            description=f"{winner_mentions}\nPrize: **{g['prize']}**",
            color=discord.Color.green()
        ))

        log = await self.log_channel(guild)
        if log: await log.send(embed=end_embed)

        g["ended"] = True
        g["ended_at"] = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
        data[str(msg_id)] = g; self.write(data)

    @tasks.loop(seconds=30)
    async def check_giveaways(self):
        data = self.read()
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        for mid, info in list(data.items()):
            if info.get("ended"): continue
            if now >= datetime.fromisoformat(info["end_time"]):
                guild = self.bot.get_guild(info["guild_id"])
                if guild: await self.end_giveaway(guild, int(mid))

    @tasks.loop(hours=12)
    async def purge_giveaways(self):
        cfg = self.read_cfg(); days = int(cfg.get("purge_days", 7))
        cutoff = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=days)
        data = self.read(); changed = False
        for mid, info in list(data.items()):
            if info.get("ended") and info.get("ended_at"):
                if datetime.fromisoformat(info["ended_at"]) < cutoff:
                    del data[mid]; changed = True
        if changed: self.write(data)

    # Commands
    @commands.hybrid_command(name="giveaway", description="Start a giveaway (channel, prize, duration, winners).")
    async def giveaway(self, ctx, channel: discord.TextChannel, prize: str, duration: str, winners: int = 1):
        secs = parse_time(duration)
        if not secs:
            return await embed_response(ctx, title="❌ Invalid Duration", description="Use 10m, 1h, or 1d.", color=discord.Color.red())
        end_time = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=secs)
        end_rel = discord.utils.format_dt(end_time, style="R")
        embed = discord.Embed(title="🎉 Giveaway Started!", description=f"**Prize:** {prize}\n**Winners:** {winners}\n**Hosted by:** {ctx.author.mention}\n**Ends:** {end_rel}", color=discord.Color.blurple())
        embed.set_footer(text="React with 🎉 to enter!")
        msg = await channel.send(embed=embed); await msg.add_reaction("🎉")
        data = self.read()
        data[str(msg.id)] = {"channel_id": channel.id, "guild_id": ctx.guild.id, "prize": prize, "winners": winners, "end_time": end_time.isoformat(), "host": ctx.author.id, "ended": False, "created_at": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()}
        self.write(data)
        await embed_response(ctx, title="🎉 Giveaway Live", description=f"Started in {channel.mention} for **{prize}** (ends {end_rel})", color=discord.Color.green())

    @commands.hybrid_command(name="giveawaylist", description="List active giveaways.")
    async def giveawaylist(self, ctx):
        data = self.read(); active = [(mid, g) for mid, g in data.items() if not g.get("ended")]
        if not active:
            return await embed_response(ctx, title="ℹ️ No Active Giveaways", color=discord.Color.blurple())
        embed = discord.Embed(title="🎉 Active Giveaways", color=discord.Color.blurple())
        for mid, g in active:
            ch = ctx.guild.get_channel(g["channel_id"])
            end_rel = discord.utils.format_dt(datetime.fromisoformat(g["end_time"]), style="R")
            embed.add_field(name=f"ID: {mid}", value=f"**Prize:** {g['prize']}\n**Winners:** {g['winners']}\n**Channel:** {ch.mention if ch else '`unknown`'}\n**Ends:** {end_rel}", inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="giveawayinfo", description="Show details of a giveaway by ID.")
    async def giveawayinfo(self, ctx, message_id: str):
        data = self.read(); g = data.get(str(message_id))
        if not g:
            return await embed_response(ctx, title="❌ Giveaway Not Found", color=discord.Color.red())
        ch = ctx.guild.get_channel(g["channel_id"])
        end_rel = discord.utils.format_dt(datetime.fromisoformat(g["end_time"]), style="R")
        embed = discord.Embed(title=f"🎁 Giveaway Info — {message_id}", color=discord.Color.green() if g.get("ended") else discord.Color.blurple())
        embed.add_field(name="Prize", value=g["prize"]); embed.add_field(name="Winners", value=str(g["winners"]))
        embed.add_field(name="Channel", value=ch.mention if ch else "`unknown`")
        embed.add_field(name="Status", value="Ended" if g.get("ended") else "Active")
        embed.add_field(name="Ends", value=end_rel)
        if g.get("ended_at"): embed.add_field(name="Ended At", value=g["ended_at"], inline=False)
        host = ctx.guild.get_member(g.get("host")) if g.get("host") else None
        if host: embed.add_field(name="Host", value=host.mention, inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="setgiveawaypurge", description="Set auto-purge days for ended giveaways (0–365).")
    @commands.has_permissions(administrator=True)
    async def setgiveawaypurge(self, ctx, days: int):
        if days < 0 or days > 365:
            return await embed_response(ctx, title="❌ Invalid Days", description="Choose 0–365.", color=discord.Color.red())
        cfg = self.read_cfg(); cfg["purge_days"] = days; self.write_cfg(cfg)
        await embed_response(ctx, title="🧹 Purge Updated", description=f"Ended giveaways will be purged after **{days}** day(s).", color=discord.Color.green())

    @commands.hybrid_command(name="giveawayend", description="End a giveaway early (by message id).")
    @commands.has_permissions(manage_guild=True)
    async def giveawayend(self, ctx, message_id: str):
        data = self.read(); g = data.get(str(message_id))
        if not g: return await embed_response(ctx, title="❌ Giveaway Not Found", color=discord.Color.red())
        guild = self.bot.get_guild(g["guild_id"])
        await self.end_giveaway(guild, int(message_id), ended_by=ctx.author)
        await embed_response(ctx, title="🛑 Giveaway Ended", description=f"Ended giveaway **{message_id}**.", color=discord.Color.orange())

    @commands.hybrid_command(name="reroll", description="Reroll a giveaway (by message id).")
    async def reroll(self, ctx, message_id: str):
        data = self.read(); g = data.get(str(message_id))
        if not g: return await embed_response(ctx, title="❌ Giveaway Not Found", color=discord.Color.red())
        ch = ctx.guild.get_channel(g["channel_id"])
        if not ch: return await embed_response(ctx, title="⚠️ Channel Missing", color=discord.Color.orange())
        try:
            msg = await ch.fetch_message(int(message_id))
        except:
            return await embed_response(ctx, title="⚠️ Message Fetch Failed", color=discord.Color.orange())

        entrants = []
        for r in msg.reactions:
            if str(r.emoji) == "🎉":
                entrants = [u async for u in r.users() if not u.bot]
                break
        if not entrants:
            return await embed_response(ctx, title="😢 No Entrants", description="Cannot reroll.", color=discord.Color.red())

        new_winner = random.choice(entrants)
        await embed_response(ctx, title="🎉 Rerolled Winner", description=f"{new_winner.mention} for **{g['prize']}**!", color=discord.Color.green())

async def setup(bot):
    await bot.add_cog(Giveaways(bot))
