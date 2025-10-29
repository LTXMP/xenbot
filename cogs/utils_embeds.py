import discord

async def embed_response(ctx_or_interaction, title="✅ Success", description="", color=discord.Color.blurple()):
    """Send a unified embed for both slash interactions and prefix ctx."""
    embed = discord.Embed(title=title, description=description, color=color)
    footer_user = getattr(ctx_or_interaction, "user", None) or getattr(ctx_or_interaction, "author", None)
    if footer_user:
        embed.set_footer(text=f"Requested by {footer_user}", icon_url=getattr(footer_user.display_avatar, "url", discord.Embed.Empty))
    embed.timestamp = discord.utils.utcnow()

    try:
        # Slash interactions have response object
        if hasattr(ctx_or_interaction, "response") and not ctx_or_interaction.response.is_done():
            await ctx_or_interaction.response.send_message(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)
    except Exception as e:
        print(f"[embed_response] {e}")
