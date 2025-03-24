import discord
import logging
logger = logging.getLogger('discord')

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