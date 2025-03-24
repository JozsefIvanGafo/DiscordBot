import asyncio
import logging
import discord

logger = logging.getLogger('discord')

class EventHandlers:
    def __init__(self, music_cog):
        self.music_cog = music_cog
        self.bot = music_cog.bot
    
    async def handle_voice_state_update(self, member, before, after):
        """Handle voice state changes"""
        try:
            # Handle bot's own voice state updates
            if member.id == self.bot.user.id:
                await self._handle_bot_voice_update(member, before, after)
                return
                
            # Handle user join events
            if before.channel is None and after.channel is not None:
                await self._handle_user_join(member, after)
            
            # Handle user leave events
            elif before.channel is not None and after.channel is None:
                await self._handle_user_leave(member, before)
            
            # Handle user moving between channels
            elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
                await self._handle_user_move(member, before, after)
            
            # Handle emptying voice channels (regardless of event type)
            await self._check_empty_voice_channel(member, before, after)
        except Exception as e:
            logger.error(f"Error in voice_state_update handler: {e}", exc_info=True)
    
    async def _handle_bot_voice_update(self, member, before, after):
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
    
    async def _handle_user_join(self, member, after):
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
    
    async def _handle_user_leave(self, member, before):
        """Handle user leaving a voice channel"""
        try:
            # We'll let _check_empty_voice_channel handle the logic for this
            # as it already covers the case when users leave
            pass
        except Exception as e:
            logger.error(f"Error handling user leave: {e}", exc_info=True)
    
    async def _handle_user_move(self, member, before, after):
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
    
    async def _check_empty_voice_channel(self, member, before, after):
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
    
    # Additional helper that could be useful for external calls
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

