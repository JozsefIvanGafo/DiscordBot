import discord
import logging
logger = logging.getLogger('discord')
async def force_disconnect(self, guild_id):
        """Force disconnect from voice in a specific guild"""
        try:
            voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
            if voice_client:
                await voice_client.disconnect()
                self.music_cog.voice_manager.clear_voice_client(guild_id)
                self.music_cog.queue_manager.clear_guild_data(guild_id)
                
                # Update controller if needed
                await self.music_cog.controller_service.update_controller(guild_id)
                
                logger.info(f"Force disconnected from voice in guild {guild_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error force disconnecting: {e}", exc_info=True)
            return False