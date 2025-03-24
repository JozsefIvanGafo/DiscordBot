import logging
import discord
logger = logging.getLogger('discord')
async def handle_user_leave(self, member, before):
        """Handle user leaving a voice channel"""
        try:
            # We'll let _check_empty_voice_channel handle the logic for this
            # as it already covers the case when users leave
            pass
        except Exception as e:
            logger.error(f"Error handling user leave: {e}", exc_info=True)