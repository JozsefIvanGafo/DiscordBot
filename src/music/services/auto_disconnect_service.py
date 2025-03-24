import asyncio
import logging

logger = logging.getLogger('discord')

class AutoDisconnectService:
    def __init__(self, music_cog):
        self.music_cog = music_cog
        self.bot = music_cog.bot
        self.disconnect_timers = {}  # guild_id: task
        self.idle_timeout = 10 #300  # 5 minutes (adjust as needed)
    
    async def start_timer(self, guild_id):
        """Start a timer for disconnecting if a guild becomes inactive"""
        # Clear any existing timers first
        self.clear_timer(guild_id)
        
        # Create a new timer
        self.disconnect_timers[guild_id] = asyncio.create_task(
            self._disconnect_after_timeout(guild_id)
        )
        logger.debug(f"Started auto-disconnect timer for guild {guild_id}")
    
    def clear_timer(self, guild_id):
        """Clear any existing disconnect timer for a guild"""
        if guild_id in self.disconnect_timers:
            timer = self.disconnect_timers.pop(guild_id)
            if not timer.done():
                timer.cancel()
            logger.debug(f"Cleared auto-disconnect timer for guild {guild_id}")
    
    async def _disconnect_after_timeout(self, guild_id):
        """Wait for the timeout period and then disconnect if still inactive"""
        try:
            # Wait for the timeout period
            await asyncio.sleep(self.idle_timeout)
            
            # Check if we should still disconnect
            voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
            if voice_client and not voice_client.is_playing():
                logger.info(f"Auto-disconnecting from guild {guild_id} due to inactivity")
                
                # Get channel to send notification
                music_channel_id = self.music_cog.controller_service.music_channels.get(guild_id)
                if music_channel_id:
                    try:
                        channel = self.bot.get_channel(music_channel_id)
                        if channel:
                            await channel.send("Disconnecting due to inactivity...")
                    except Exception as e:
                        logger.error(f"Error sending disconnect notification: {e}")
                
                # Disconnect from voice channel
                await voice_client.disconnect()
                
                # Clean up resources
                self.music_cog.voice_manager.clear_voice_client(guild_id)
                self.music_cog.queue_manager.clear_guild_data(guild_id)
                
                # Update controller if needed
                if guild_id in self.music_cog.controller_service.controller_messages:
                    await self.music_cog.controller_service.update_controller(guild_id)
        
        except asyncio.CancelledError:
            # Timer was cancelled, no need to do anything
            pass
        except Exception as e:
            logger.error(f"Error in auto-disconnect timer: {e}")
        
        # Make sure the timer is removed from the dictionary
        if guild_id in self.disconnect_timers:
            del self.disconnect_timers[guild_id]