import logging
import discord

logger = logging.getLogger('discord')

async def handle_music_channel(self, ctx):
    """Set the current channel as the dedicated music channel"""
    try:
        guild_id = ctx.guild.id
        
        # Create a new controller message or update the existing one using the non-interaction method
        result = await self.music_cog.controller_service.setup_persistent_controller(ctx)
        
        return result
        
    except Exception as e:
        logger.error(f"Error setting music channel: {e}", exc_info=True)
        return False
