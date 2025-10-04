import logging
import discord
from .utils import (handle_play, 
                    handle_stop,
                    handle_skip,
                    handle_queue,
                    handle_leave,
                    handle_controller,
                    handle_music_channel,
                    handle_repeat)



logger = logging.getLogger('discord')

class CommandHandlers:
    def __init__(self, music_cog):
        self.music_cog = music_cog
    
    async def handle_play(self, ctx, url):
        """Handle play command"""
        await handle_play(self, ctx, url)
    
    async def handle_stop(self, ctx):
        """Handle stop command"""
        await handle_stop(self, ctx)
    
    async def handle_skip(self, ctx):
        """Handle skip command"""
        await handle_skip(self, ctx)
    
    async def handle_queue(self, ctx):
        """Handle queue command"""
        await handle_queue(self, ctx)
    
    async def handle_leave(self, ctx):
        """Handle leave command"""
        await handle_leave(self, ctx)
    
    async def handle_controller(self, ctx):
        """Handle controller command"""
        await handle_controller(self, ctx)
    
    async def handle_music_channel(self, ctx):
        """Set the current channel as the dedicated music channel for the bot's music controller"""
        await handle_music_channel(self, ctx)
    
    async def handle_repeat(self, ctx):
        """Handle repeat command - toggle through repeat modes"""
        await handle_repeat(self, ctx)

