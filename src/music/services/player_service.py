import asyncio
import discord
import logging

from ..utils import get_song_info, is_youtube_playlist, get_fresh_stream_url

logger = logging.getLogger('discord')

class PlayerService:
    def __init__(self, music_cog):
        self.music_cog = music_cog
        self.bot = music_cog.bot
    
    async def play_song(self, guild_id, ctx=None, url=None):
        """Add song to queue and start playing if not already playing"""
        if url:
            # Get song info
            try:
                if ctx:
                    await ctx.respond(f"Processing {'playlist' if is_youtube_playlist(url) else 'video/search'}... This may take a moment.")
                songs_info = await get_song_info(self.music_cog.ytdl, url)
                if not songs_info:
                    if ctx:
                        await ctx.respond("No songs found for the provided URL or search query")
                    return
                
                # Add songs to queue
                self.music_cog.queue_manager.add_multiple_to_queue(guild_id, songs_info)
                
                # Notify user
                if ctx:
                    if len(songs_info) == 1:
                        await ctx.respond(f"Added to queue: {songs_info[0]['title']}")
                    else:
                        await ctx.respond(f"Added {len(songs_info)} songs to queue")
            except Exception as e:
                logger.error(f"Error processing play request: {e}")
                if ctx:
                    await ctx.respond(f"Error processing your request: {str(e)}")
                return
        
        # Clear any disconnect timers since we're active again
        self.music_cog.auto_disconnect_service.clear_timer(guild_id)

        # Start playing if not already playing
        voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
        if voice_client and not voice_client.is_playing():
            await self.play_next(guild_id)
    
    async def play_next(self, guild_id):
        """Play the next song in the queue"""
        queue = self.music_cog.queue_manager.get_queue(guild_id)
        voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
        
        if not queue or not voice_client:
            # Clear current song info if queue is empty
            self.music_cog.queue_manager.clear_current_song(guild_id)
            # Update controller to show nothing is playing
            await self.music_cog.controller_service.update_controller(guild_id)
            return
        
        # Get the next song and update current song info
        next_song = self.music_cog.queue_manager.get_next_song(guild_id)
        self.music_cog.queue_manager.set_current_song(guild_id, next_song)
        
        try:
            # Get fresh stream URL to avoid 403 errors from expired URLs
            fresh_url = await get_fresh_stream_url(self.music_cog.ytdl, next_song['webpage_url'])
            if not fresh_url:
                logger.error(f"Could not get fresh URL for: {next_song['title']}")
                # Try to play next song
                await self.play_next(guild_id)
                return
            
            # Create audio source and play with fresh URL
            audio_source = discord.FFmpegPCMAudio(fresh_url, **self.music_cog.ffmpeg_options)
            voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(
                self._play_next_error_handled(guild_id, e), self.bot.loop))
            
            logger.info(f"Playing: {next_song['title']} in guild {guild_id}")
            
            # Update controller with new song info
            await self.music_cog.controller_service.update_controller(guild_id)
        except Exception as e:
            logger.error(f"Error playing song {next_song['title']}: {e}")
            # Try to play next song
            await self.play_next(guild_id)
    
    async def _play_next_error_handled(self, guild_id, error):
        """Handle errors when playing next song"""
        if error:
            logger.error(f"Error playing song: {error}")
        try:
            await self.play_next(guild_id)
        except Exception as e:
            logger.error(f"Error in play_next: {e}")
    
    async def stop(self, guild_id):
        """Stop playback and clear the queue"""
        voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
        if (voice_client and voice_client.is_playing()):
            voice_client.stop()
        
        # Clear queue
        self.music_cog.queue_manager.clear_queue(guild_id)
        self.music_cog.queue_manager.clear_current_song(guild_id)
        
        # Update controller
        await self.music_cog.controller_service.update_controller(guild_id)