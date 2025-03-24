import logging
import discord
logger = logging.getLogger('discord')
async def check_empty_voice_channel(self, member, before, after):
        """Check if the voice channel is empty and start disconnect timer if needed"""
        try:
            # Check if this event involves a channel that the bot is in
            if before.channel is not None:
                voice_client = self.music_cog.voice_manager.get_voice_client(before.channel.guild.id)
                
                # Make sure this is a channel the bot is in
                if voice_client and voice_client.channel.id == before.channel.id:
                    # Count human members (excluding bots)
                    human_members = [m for m in before.channel.members if not m.bot]
                    
                    # If there are no humans left, start the disconnect timer
                    if len(human_members) == 0:
                        guild_id = before.channel.guild.id
                        logger.info(f"Voice channel empty, starting disconnect timer for guild {guild_id}")
                        await self.music_cog.auto_disconnect_service.start_timer(guild_id)
        except Exception as e:
            logger.error(f"Error checking empty voice channel: {e}", exc_info=True)