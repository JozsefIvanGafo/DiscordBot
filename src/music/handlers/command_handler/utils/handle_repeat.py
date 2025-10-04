import discord
import logging

logger = logging.getLogger('discord')

async def handle_repeat(handler, ctx):
    """Handle repeat command - toggle through repeat modes"""
    guild_id = ctx.guild.id
    
    # Check if user is in a voice channel
    if not ctx.author.voice:
        await ctx.respond("You need to be in a voice channel to use this command!", ephemeral=True)
        return
    
    # Toggle repeat mode
    new_mode = handler.music_cog.queue_manager.toggle_repeat(guild_id)
    
    # Create response message with emoji
    mode_emojis = {
        'off': '⏹️',
        'one': '🔂',
        'all': '🔁'
    }
    
    mode_descriptions = {
        'off': 'Repeat is now **OFF**',
        'one': 'Repeating **current song** 🔂',
        'all': 'Repeating **entire queue** 🔁'
    }
    
    embed = discord.Embed(
        title=f"{mode_emojis[new_mode]} Repeat Mode",
        description=mode_descriptions[new_mode],
        color=discord.Color.blue()
    )
    
    await ctx.respond(embed=embed)
    
    # Update controller to reflect new repeat state
    await handler.music_cog.controller_service.update_controller(guild_id)
    
    logger.info(f"Repeat mode set to '{new_mode}' in guild {guild_id}")
