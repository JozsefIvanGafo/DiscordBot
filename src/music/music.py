import discord
from discord.ext import commands, bridge
import asyncio
import logging
import yt_dlp
import threading

from .utils import (
    get_ytdlp_options, get_ffmpeg_options,
    is_youtube_url, is_youtube_playlist, 
    extract_info, get_song_info,
    QueueManager, VoiceManager,
    format_duration, split_text
)

logger = logging.getLogger('discord')

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._lock = threading.Lock()
        
        # Initialize managers
        self.queue_manager = QueueManager()
        self.voice_manager = VoiceManager()
        
        # yt-dlp setup
        self.ytdl_options = get_ytdlp_options()
        self.ytdl = yt_dlp.YoutubeDL(self.ytdl_options)
        
        # FFmpeg setup
        self.ffmpeg_options = get_ffmpeg_options()
    
    # Playback methods
    async def play_next(self, guild_id):
        """Play the next song in the queue"""
        queue = self.queue_manager.get_queue(guild_id)
        voice_client = self.voice_manager.get_voice_client(guild_id)
        
        if not queue or not voice_client:
            # Clear current song info if queue is empty
            self.queue_manager.clear_current_song(guild_id)
            return
        
        # Get the next song and update current song info
        next_song = self.queue_manager.get_next_song(guild_id)
        self.queue_manager.set_current_song(guild_id, next_song)
        
        # Create audio source and play
        audio_source = discord.FFmpegPCMAudio(next_song['url'], **self.ffmpeg_options)
        voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(
            self._play_next_error_handled(guild_id, e), self.bot.loop))
        
        logger.info(f"Playing: {next_song['title']} in guild {guild_id}")
    
    async def _play_next_error_handled(self, guild_id, error):
        """Handle errors when playing next song"""
        if error:
            logger.error(f"Error playing song: {error}")
        try:
            await self.play_next(guild_id)
        except Exception as e:
            logger.error(f"Error in play_next: {e}")
    
    # Command methods
    async def _play(self, ctx, url):
        """Play a song or playlist from YouTube"""
        guild_id = ctx.guild.id
        
        # Join voice channel first
        voice_client = await self.voice_manager.join_voice_channel(ctx)
        if voice_client is None:
            return
        
        # Get song info
        try:
            await ctx.respond(f"Processing {'playlist' if is_youtube_playlist(url) else 'video/search'}... This may take a moment.")
            songs_info = await get_song_info(self.ytdl, url)
            if not songs_info:
                await ctx.respond("No songs found for the provided URL or search query")
                return
            
            # Add songs to queue
            self.queue_manager.add_multiple_to_queue(guild_id, songs_info)
            
            # Notify user
            if len(songs_info) == 1:
                await ctx.respond(f"Added to queue: {songs_info[0]['title']}")
            else:
                await ctx.respond(f"Added {len(songs_info)} songs to queue")
            
            # Start playing if not already playing
            if not voice_client.is_playing():
                await self.play_next(guild_id)
                
        except ValueError as e:
            # Friendly error message for specific errors
            await ctx.respond(f"Error: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing play request: {e}")
            await ctx.respond(f"Error processing your request: {str(e)}")
    
    async def _stop(self, ctx):
        """Stop playback and clear queue"""
        guild_id = ctx.guild.id
        voice_client = self.voice_manager.get_voice_client(guild_id)
        
        if voice_client and voice_client.is_connected():
            # Stop playback
            if voice_client.is_playing():
                voice_client.stop()
            
            # Clear queue
            self.queue_manager.clear_queue(guild_id)
            self.queue_manager.clear_current_song(guild_id)
            
            await ctx.respond("Playback stopped and queue cleared")
        else:
            await ctx.respond("Not currently playing anything")
    
    async def _skip(self, ctx):
        """Skip the current song"""
        guild_id = ctx.guild.id
        voice_client = self.voice_manager.get_voice_client(guild_id)
        
        if voice_client and voice_client.is_playing():
            voice_client.stop()  # This will trigger play_next via the after callback
            await ctx.respond("Skipped current song")
        else:
            await ctx.respond("Not currently playing anything")
    
    async def _queue(self, ctx):
        """Show the current queue"""
        guild_id = ctx.guild.id
        queue = self.queue_manager.get_queue(guild_id)
        current_song = self.queue_manager.get_current_song(guild_id)
        
        if not current_song and not queue:
            await ctx.respond("The queue is empty")
            return
        
        # Build embed
        embed = discord.Embed(title="Music Queue", color=discord.Color.purple())
        
        # Add current song
        if current_song:
            duration = format_duration(current_song['duration'])
            embed.add_field(
                name="🎵 Currently Playing",
                value=f"[{current_song['title']}]({current_song['webpage_url']}) ({duration})",
                inline=False
            )
        
        # Add queue
        if queue:
            queue_list = []
            for i, song in enumerate(queue, 1):
                duration = format_duration(song['duration'])
                queue_list.append(f"{i}. [{song['title']}]({song['webpage_url']}) ({duration})")
            
            queue_text = "\n".join(queue_list)
            # Split into chunks if too long
            if len(queue_text) <= 1024:
                embed.add_field(name="📝 Up Next", value=queue_text, inline=False)
            else:
                chunks = split_text(queue_text, 1024)
                for i, chunk in enumerate(chunks):
                    embed.add_field(name=f"📝 Up Next (Part {i+1})" if i > 0 else "📝 Up Next", 
                                    value=chunk, inline=False)
        
        # Add total duration
        total_duration = sum(song['duration'] for song in queue)
        if current_song:
            total_duration += current_song['duration']
        embed.set_footer(text=f"Total songs: {len(queue) + (1 if current_song else 0)} | Total duration: {format_duration(total_duration)}")
        
        await ctx.respond(embed=embed)
    
    async def _leave(self, ctx):
        """Leave the voice channel"""
        guild_id = ctx.guild.id
        voice_client = self.voice_manager.get_voice_client(guild_id)
        
        if voice_client and voice_client.is_connected():
            # Stop playback
            if voice_client.is_playing():
                voice_client.stop()
            
            # Disconnect
            await voice_client.disconnect()
            
            # Clear data
            self.voice_manager.clear_voice_client(guild_id)
            self.queue_manager.clear_guild_data(guild_id)
            
            await ctx.respond("Left voice channel")
        else:
            await ctx.respond("Not connected to a voice channel")
    
    # Command definitions
    @bridge.bridge_command(
        name="play",
        description="Play a song or playlist from YouTube"
    )
    async def play(self, ctx, *, url: str):
        """Play a song or playlist from YouTube"""
        await self._play(ctx, url)
    
    @bridge.bridge_command(
        name="stop",
        description="Stop playback and clear the queue"
    )
    async def stop(self, ctx):
        """Stop playback and clear the queue"""
        await self._stop(ctx)
    
    @bridge.bridge_command(
        name="skip",
        description="Skip the current song"
    )
    async def skip(self, ctx):
        """Skip the current song"""
        await self._skip(ctx)
    
    @bridge.bridge_command(
        name="queue",
        description="Show the current music queue"
    )
    async def queue(self, ctx):
        """Show the current music queue"""
        await self._queue(ctx)
    
    @bridge.bridge_command(
        name="leave",
        description="Leave the voice channel"
    )
    async def leave(self, ctx):
        """Leave the voice channel"""
        await self._leave(ctx)

def setup(bot):
    bot.add_cog(Music(bot))