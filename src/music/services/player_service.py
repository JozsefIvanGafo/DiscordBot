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
                    await ctx.respond("🔍 Searching...", ephemeral=True)
                
                logger.info(f"Fetching info for: {url}")
                songs_info, metadata = await get_song_info(self.music_cog.ytdl, url)
                
                if not songs_info:
                    if ctx:
                        await ctx.respond("❌ No songs found for the provided URL or search query")
                    return
                
                # Add songs to queue
                self.music_cog.queue_manager.add_multiple_to_queue(guild_id, songs_info)
                
                # Notify user (always single song now)
                if ctx:
                    embed = discord.Embed(
                        title="✅ Added to Queue",
                        description=f"[{songs_info[0]['title']}]({songs_info[0]['webpage_url']})",
                        color=discord.Color.green()
                    )
                    await ctx.respond(embed=embed)
            except ValueError as e:
                logger.error(f"Error processing play request: {e}")
                if ctx:
                    await ctx.respond(f"❌ Error: {str(e)}")
                return
            except Exception as e:
                logger.error(f"Unexpected error processing play request: {e}", exc_info=True)
                if ctx:
                    error_msg = str(e)
                    if "unavailable" in error_msg.lower():
                        await ctx.respond("❌ This video/playlist is unavailable or private")
                    elif "copyright" in error_msg.lower():
                        await ctx.respond("❌ This video is blocked due to copyright restrictions")
                    else:
                        await ctx.respond(f"❌ Error processing your request: {error_msg[:200]}")
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
        repeat_mode = self.music_cog.queue_manager.get_repeat_mode(guild_id)
        current_song = self.music_cog.queue_manager.get_current_song(guild_id)
        
        # Handle repeat modes
        if repeat_mode == 'one' and current_song:
            # Repeat the current song
            next_song = current_song
        elif repeat_mode == 'all' and current_song and not queue:
            # If queue is empty and repeat all is on, replay current song
            next_song = current_song
        elif not queue or not voice_client:
            # No more songs and no repeat
            self.music_cog.queue_manager.clear_current_song(guild_id)
            await self.music_cog.controller_service.update_controller(guild_id)
            return
        else:
            # Get the next song from queue
            next_song = self.music_cog.queue_manager.get_next_song(guild_id)
            
            # If repeat all is on, add the finished song back to the end of queue
            if repeat_mode == 'all' and current_song:
                self.music_cog.queue_manager.add_to_queue(guild_id, current_song)
        
        # Update current song info
        self.music_cog.queue_manager.set_current_song(guild_id, next_song)
        
        try:
            # Get fresh stream URL to avoid 403 errors from expired URLs
            logger.info(f"Getting fresh stream URL for: {next_song['title']}")
            logger.debug(f"Webpage URL: {next_song['webpage_url']}")
            
            fresh_url = await get_fresh_stream_url(self.music_cog.ytdl, next_song['webpage_url'])
            
            if not fresh_url:
                logger.error(f"Could not get fresh URL for: {next_song['title']}")
                logger.error(f"Skipping song and trying next...")
                # Try to play next song
                await self.play_next(guild_id)
                return
            
            logger.info(f"Got fresh URL, creating audio source...")
            
            # Create audio source and play with fresh URL
            audio_source = discord.FFmpegPCMAudio(fresh_url, **self.music_cog.ffmpeg_options)
            voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(
                self._play_next_error_handled(guild_id, e), self.bot.loop))
            
            logger.info(f"Now playing: {next_song['title']} in guild {guild_id}")
            
            # Update controller with new song info
            await self.music_cog.controller_service.update_controller(guild_id)
        except Exception as e:
            logger.error(f"Error playing song '{next_song['title']}': {e}", exc_info=True)
            logger.error(f"Skipping to next song...")
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