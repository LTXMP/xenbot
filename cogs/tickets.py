import discord, os, json, asyncio
from discord.ext import commands
from datetime import datetime, timezone
from html import escape as h
from .utils_embeds import embed_response

CONFIG_PATH = "data/config.json"
os.makedirs("transcripts", exist_ok=True)

STAFF_ROLE_NAME = "Helper"
TICKETS_CATEGORY = "tickets"

class TicketTypeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support", description="Open a support ticket", emoji="🛠️"),
            discord.SelectOption(label="Buy", description="Open a purchase ticket", emoji="💰"),
        ]
        super().__init__(placeholder="Select Ticket Type...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content=f"Select the **product** for your `{self.values[0]}` ticket:",
            view=ProductSelectView(self.values[0])
        )

class ProductSelect(discord.ui.Select):
    def __init__(self, ticket_type: str):
        self.ticket_type = ticket_type
        products = [
            "Battlefied 6/nemesis","Warzone",
            "Apex","Destiny 2/Zephyr",
            "R6","Aimsync",
            "Savage","Bot source code",
            "Valorant","Smth else"
        ]
        options = [discord.SelectOption(label=p, description=f"{ticket_type} for {p}") for p in products]
        super().__init__(placeholder="Select a product...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        product = self.values[0]
        ttype = self.ticket_type.lower()
        guild = interaction.guild
        staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE_NAME)
        category = discord.utils.get(guild.categories, name=TICKETS_CATEGORY) or await guild.create_category(TICKETS_CATEGORY)

        safe_product = product.replace(" ", "-").lower()
        channel_name = f"{ttype}-{safe_product}"

        if discord.utils.get(guild.channels, name=channel_name):
            return await embed_response(interaction, title="⚠️ Ticket Exists", description=f"A ticket already exists: <#{discord.utils.get(guild.channels, name=channel_name).id}>", color=discord.Color.orange())

        # Unmoderated tickets: opener + staff role (only) — no @everyone
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True),
        }
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        channel = await guild.create_text_channel(
            name=channel_name, category=category, overwrites=overwrites,
            topic=f"{ttype.capitalize()} ticket for {product} | User: {interaction.user}"
        )

        embed = discord.Embed(
            title=f"🎫 {ttype.capitalize()} Ticket — {product}",
            description=f"{interaction.user.mention}, thanks for opening a **{ttype}** ticket for **{product}**.\nUse the button below to **close** when finished.",
            color=discord.Color.green()
        )
        view = TicketControls(interaction.user, product, ttype)
        mention = f"{interaction.user.mention}" + (f" | <@&{staff_role.id}>" if staff_role else "")
        await channel.send(content=mention, embed=embed, view=view)
        await embed_response(interaction, title="🎫 Ticket Created", description=f"Channel: {channel.mention}", color=discord.Color.green())

class ProductSelectView(discord.ui.View):
    def __init__(self, ticket_type: str):
        super().__init__(timeout=60)
        self.add_item(ProductSelect(ticket_type))

class TicketControls(discord.ui.View):
    def __init__(self, opener: discord.User, product: str, ticket_type: str):
        super().__init__(timeout=None)
        self.opener = opener; self.product = product; self.ticket_type = ticket_type

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_role = discord.utils.get(interaction.guild.roles, name=STAFF_ROLE_NAME)
        if not (interaction.user == self.opener or (staff_role and staff_role in interaction.user.roles)):
            return await embed_response(interaction, title="❌ Permission Denied", color=discord.Color.red())

        await embed_response(interaction, title="🕐 Closing...", description="Generating HTML transcript & closing shortly.", color=discord.Color.blurple())

        # Build HTML transcript
        messages = [m async for m in interaction.channel.history(limit=None, oldest_first=True)]
        opened_at = messages[0].created_at if messages else datetime.now(timezone.utc)
        generated_at = datetime.now(timezone.utc)

        def msg_html(m: discord.Message) -> str:
            av = m.author.display_avatar.url if m.author.display_avatar else ""
            ts = m.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')
            content = h(m.content) if m.content else "<i>(no text)</i>"
            attach = ""
            if m.attachments:
                attach = '<div class="attachments">Attachments: ' + ", ".join(f'<a href="{a.url}">{h(a.filename)}</a>' for a in m.attachments) + '</div>'
            return f'''
<div class="msg">
  <img class="avatar" src="{h(str(av))}">
  <div>
    <div class="author">{h(m.author.display_name)} <span class="time">{h(ts)}</span></div>
    <div class="content">{content}</div>
    {attach}
  </div>
</div>'''

        head = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Transcript - {h(interaction.channel.name)}</title>
<style>
body {{ background:#0f172a; color:#e5e7eb; font-family:Segoe UI,Inter,Arial; margin:0; padding:24px; }}
.wrap {{ max-width:1000px; margin:auto; }}
.msg {{ display:grid; grid-template-columns:48px 1fr; gap:10px; background:#1e293b; margin-bottom:10px; padding:10px; border-radius:10px; }}
.avatar {{ width:48px; height:48px; border-radius:50%; }}
.author {{ font-weight:600; }}
.time {{ font-size:12px; color:#94a3b8; margin-left:8px; }}
.content {{ white-space:pre-wrap; word-break:break-word; }}
.attachments {{ margin-top:6px; }}
a {{ color:#60a5fa; }}
.badge {{ display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; border:1px solid #1f2937; color:#94a3b8; margin-right:6px; }}
.header {{ background:#0b1220; padding:12px 14px; border-radius:10px; border:1px solid #1f2937; margin-bottom:12px; }}
</style></head><body><div class="wrap">
<div class="header">
  <div><span class="badge">{h(self.ticket_type.capitalize())}</span>
       <span class="badge">Product: {h(self.product)}</span>
       <span class="badge">Opened by: {h(str(self.opener))}</span>
       <span class="badge">Opened: {h(opened_at.strftime('%Y-%m-%d %H:%M:%S UTC'))}</span>
       <span class="badge">Generated: {h(generated_at.strftime('%Y-%m-%d %H:%M:%S UTC'))}</span>
       <span class="badge">Channel: {h(interaction.channel.name)}</span></div>
</div>
"""
        body = "\n".join(msg_html(m) for m in messages)
        tail = "</div></body></html>"
        html_content = head + body + tail

        safe = interaction.channel.name.replace(" ", "_")
        filepath = f"transcripts/{safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        # DM transcript to opener
        try:
            await self.opener.send(embed=discord.Embed(
                title="📄 Your Ticket Transcript (HTML)",
                description=f"**{self.ticket_type.capitalize()}** — **{self.product}**",
                color=discord.Color.blurple()
            ))
            await self.opener.send(file=discord.File(filepath))
        except: pass

        # Send to logging channel
        log_ch = await get_log_channel(interaction.guild)
        if log_ch:
            await log_ch.send(embed=discord.Embed(
                title="🎫 Ticket Closed",
                description=f"**User:** {self.opener.mention}\n**Product:** {self.product}\n**Type:** {self.ticket_type.capitalize()}\n**Closed by:** {interaction.user.mention}",
                color=discord.Color.red()
            ))
            await log_ch.send(file=discord.File(filepath))

        await asyncio.sleep(5)
        await interaction.channel.delete()

async def get_log_channel(guild: discord.Guild):
    if not os.path.exists(CONFIG_PATH): return None
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f: data = json.load(f)
        ch_id = data.get("log_channel")
        return guild.get_channel(ch_id) if ch_id else None
    except: return None

class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketTypeSelect())

class Tickets(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.hybrid_command(name="ticketpanel", description="Send the ticket dropdown panel")
    @commands.has_permissions(administrator=True)
    async def ticketpanel(self, ctx):
        embed = discord.Embed(
            title="🎫 Ticket System",
            description="Need help or ready to buy?\nSelect an option below to open a ticket:",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed, view=TicketPanelView())

async def setup(bot):
    await bot.add_cog(Tickets(bot))
