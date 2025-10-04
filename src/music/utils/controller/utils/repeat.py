import discord
import logging

logger = logging.getLogger('discord')

async def repeat_callback(view, interaction):
    """Toggle repeat mode through: off -> one -> all -> off"""
    guild_id = view.guild_id
    
    # Toggle repeat mode
    new_mode = view.music_cog.queue_manager.toggle_repeat(guild_id)
    
    # Create response with emoji
    mode_emojis = {
        'off': '⏹️',
        'one': '🔂',
        'all': '🔁'
    }
    
    mode_descriptions = {
        'off': 'Repeat OFF',
        'one': 'Repeat One Song',
        'all': 'Repeat All'
    }
    
    # Acknowledge interaction
    await interaction.response.send_message(
        f"{mode_emojis[new_mode]} **{mode_descriptions[new_mode]}**",
        ephemeral=True
    )
    
    # Update controller to reflect new repeat state
    await view.music_cog.controller_service.update_controller(guild_id)
    
    logger.info(f"Repeat mode set to '{new_mode}' in guild {guild_id}")
