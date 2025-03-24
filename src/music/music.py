import discord
from discord.ext import commands, bridge
import logging
import yt_dlp

from .services.player_service import PlayerService
from .services.controller_service import ControllerService
from .services.auto_disconnect_service import AutoDisconnectService
from .handlers import CommandHandlers, EventHandlers


from .utils import (
    get_ytdlp_options, get_ffmpeg_options,
    QueueManager, VoiceManager
)

logger = logging.getLogger('discord')

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Initialize managers
        self.queue_manager = QueueManager()
        self.voice_manager = VoiceManager()
        
        # yt-dlp setup
        self.ytdl_options = get_ytdlp_options()
        self.ytdl = yt_dlp.YoutubeDL(self.ytdl_options)
        
        # FFmpeg setup
        self.ffmpeg_options = get_ffmpeg_options()
        
        # Initialize services
        self.controller_service = ControllerService(self)
        self.player_service = PlayerService(self)
        self.auto_disconnect_service = AutoDisconnectService(self)
        
        # Initialize handlers
        self.command_handlers = CommandHandlers(self)
        self.event_handlers = EventHandlers(self)
        
        logger.info("Music cog loaded with commands")
    
    # Event listener (delegate to event handler)
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state changes"""
        await self.event_handlers.handle_voice_state_update(member, before, after)
    
    # Command definitions (delegate to command handlers)
    @bridge.bridge_command(name="play", description="Play a song or playlist from YouTube")
    async def play(self, ctx, *, url: str):
        await self.command_handlers.handle_play(ctx, url)
    
    @bridge.bridge_command(name="stop", description="Stop playback and clear the queue")
    async def stop(self, ctx):
        await self.command_handlers.handle_stop(ctx)
    
    @bridge.bridge_command(name="skip", description="Skip the current song")
    async def skip(self, ctx):
        await self.command_handlers.handle_skip(ctx)
    
    @bridge.bridge_command(name="queue", description="Show the current music queue")
    async def queue(self, ctx):
        await self.command_handlers.handle_queue(ctx)
    
    @bridge.bridge_command(name="leave", description="Leave the voice channel")
    async def leave(self, ctx):
        await self.command_handlers.handle_leave(ctx)
    
    @bridge.bridge_command(name="controller", description="Show music controller with buttons")
    async def controller(self, ctx):
        await self.command_handlers.handle_controller(ctx)
    
    @commands.has_permissions(manage_channels=True)   
    @bridge.bridge_command(name="set_music_channel", description="Set the current channel as the dedicated music channel")
    async def set_music_channel(self, ctx):
        await self.command_handlers.handle_music_channel(ctx)

def setup(bot):
    bot.add_cog(Music(bot))
