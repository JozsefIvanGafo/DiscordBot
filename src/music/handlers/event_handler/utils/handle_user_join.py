import logging
import discord
logger = logging.getLogger('discord')

async def handle_user_join(self, member, after):
        """Handle user joining a voice channel"""
        try:
            # Only process if this is a channel the bot is in
            voice_client = self.music_cog.voice_manager.get_voice_client(after.channel.guild.id)
            if not voice_client or voice_client.channel.id != after.channel.id:
                return
                
            # If a user joins the bot's voice channel, cancel any disconnect timers
            if not member.bot:
                guild_id = after.channel.guild.id
                self.music_cog.auto_disconnect_service.clear_timer(guild_id)
                logger.debug(f"User {member.display_name} joined voice channel, cancelling disconnect timer")
        except Exception as e:
            logger.error(f"Error handling user join: {e}", exc_info=True)