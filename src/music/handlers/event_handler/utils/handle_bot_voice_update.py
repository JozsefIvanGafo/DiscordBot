import discord
import logging

logger = logging.getLogger('discord')

async def handle_bot_voice_update(self, member, before, after):
        """Handle the bot's own voice state updates"""
        try:
            # Bot left a voice channel
            if before.channel is not None and after.channel is None:
                guild_id = before.channel.guild.id
                
                # Update the controller instead of removing it
                await self.music_cog.controller_service.update_controller(guild_id)
                
                # Clear data
                self.music_cog.voice_manager.clear_voice_client(guild_id)
                self.music_cog.queue_manager.clear_guild_data(guild_id)
                
                # Clear any auto-disconnect timers
                self.music_cog.auto_disconnect_service.clear_timer(guild_id)
                
                # Don't delete the controller message reference
                # It should remain accessible for users to interact with
            
            # Bot was moved to a different channel
            elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
                guild_id = after.channel.guild.id
                logger.info(f"Bot was moved to a different voice channel in guild {guild_id}")
                
                # Check if the channel is empty except for bots
                human_members = [m for m in after.channel.members if not m.bot]
                if len(human_members) == 0:
                    # Start disconnect timer if moved to an empty channel
                    await self.music_cog.auto_disconnect_service.start_timer(guild_id)
                else:
                    # Clear any existing timer since humans are present
                    self.music_cog.auto_disconnect_service.clear_timer(guild_id)
        except Exception as e:
            logger.error(f"Error handling bot voice update: {e}", exc_info=True)