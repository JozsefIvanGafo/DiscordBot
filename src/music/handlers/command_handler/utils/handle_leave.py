import discord
import logging

logger = logging.getLogger('discord')

async def handle_leave(self, ctx):
        """Handle leave command"""
        try:
            guild_id = ctx.guild.id
            voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
            
            if voice_client and voice_client.is_connected():
                # Stop playback and clear queue
                await self.music_cog.player_service.stop(guild_id)
                
                # Disconnect from voice
                await voice_client.disconnect()
                self.music_cog.voice_manager.clear_voice_client(guild_id)
                
                # Update controller if needed
                await self.music_cog.controller_service.update_controller(guild_id)
                
                await ctx.respond("Disconnected from voice channel")
            else:
                await ctx.respond("Not currently in a voice channel")
                
        except Exception as e:
            logger.error(f"Error handling leave command: {e}", exc_info=True)
            await ctx.respond("⚠️ There was an error disconnecting from the voice channel.")