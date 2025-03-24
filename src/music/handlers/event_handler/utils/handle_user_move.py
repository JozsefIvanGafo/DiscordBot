import logging
import discord
logger = logging.getLogger('discord')
async def handle_user_move(self, member, before, after):
        """Handle user moving between voice channels"""
        try:
            # Check if the user left a channel the bot is in
            voice_client = self.music_cog.voice_manager.get_voice_client(before.channel.guild.id)
            if voice_client and voice_client.channel.id == before.channel.id and not member.bot:
                # User moved from bot's channel, check if it's now empty
                human_members = [m for m in before.channel.members if not m.bot]
                if len(human_members) == 0:
                    guild_id = before.channel.guild.id
                    logger.info(f"Last user moved from bot's channel in guild {guild_id}, starting disconnect timer")
                    await self.music_cog.auto_disconnect_service.start_timer(guild_id)
            
            # Check if the user joined a channel the bot is in
            if voice_client and voice_client.channel.id == after.channel.id and not member.bot:
                # User moved to bot's channel, cancel any disconnect timers
                guild_id = after.channel.guild.id
                self.music_cog.auto_disconnect_service.clear_timer(guild_id)
                logger.debug(f"User {member.display_name} moved to bot's channel, cancelling disconnect timer")
        except Exception as e:
            logger.error(f"Error handling user move: {e}", exc_info=True)