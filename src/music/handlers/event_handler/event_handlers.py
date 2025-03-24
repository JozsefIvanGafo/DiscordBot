import logging

from .utils import (check_empty_voice_channel,
                   handle_voice_state_update,
                   handle_user_join,
                   handle_user_leave,
                   handle_user_move,
                   handle_bot_voice_update,
                   force_disconnect)

logger = logging.getLogger('discord')

class EventHandlers:
    def __init__(self, music_cog):
        self.music_cog = music_cog
        self.bot = music_cog.bot
    
    async def handle_voice_state_update(self, member, before, after):
        """Handle voice state changes"""
        await handle_voice_state_update(self, member, before, after)
    
    async def _handle_bot_voice_update(self, member, before, after):
        """Handle the bot's own voice state updates"""
        await handle_bot_voice_update(self, member, before, after)
    
    async def _handle_user_join(self, member, after):
        """Handle user joining a voice channel"""
        await handle_user_join(self, member, after)
    
    async def _handle_user_leave(self, member, before):
        """Handle user leaving a voice channel"""
        await handle_user_leave(self, member, before)
    
    async def _handle_user_move(self, member, before, after):
        """Handle user moving between voice channels"""
        await handle_user_move(self, member, before, after)
    
    async def _check_empty_voice_channel(self, member, before, after):
        """Check if the voice channel is empty and start disconnect timer if needed"""
        await check_empty_voice_channel(self, member, before, after)
    
    async def force_disconnect(self, guild_id):
        """Force disconnect from voice in a specific guild"""
        await force_disconnect(self, guild_id)

