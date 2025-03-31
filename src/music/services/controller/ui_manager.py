import discord
import logging
from typing import Dict, Optional
from discord import Message, Embed, Color
from ..player_service import PlayerService
from ...utils import MusicControllerView, format_duration

logger = logging.getLogger('discord')

class ControllerUIManager:
    def __init__(self, music_cog):
        self.music_cog = music_cog
        self.player_service: PlayerService = music_cog.player_service
    
    def create_controller_embed(self, guild_id: int) -> Embed:
        """Create the controller embed with current song information"""
        current_song = self.music_cog.queue_manager.get_current_song(guild_id)
        
        embed = Embed(
            title="🎵 Music Controller",
            description="Control the music playback using the buttons below.",
            color=Color.blue()
        )
        
        # Get voice client status
        voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
        status = "Disconnected"
        if voice_client:
            status = "Playing" if voice_client.is_playing() else "Paused" if voice_client.is_paused() else "Connected (Idle)"
        
        if current_song:
            duration = format_duration(current_song['duration'])
            embed.add_field(
                name="Now Playing",
                value=f"[{current_song['title']}]({current_song['webpage_url']}) ({duration})",
                inline=False
            )
            embed.add_field(
                name="Status",
                value=f"{status}",
                inline=True
            )
        else:
            embed.add_field(
                name="Status",
                value=f"{status}\nNothing is currently playing. Use `/play <song name or URL>` to add songs to the queue.",
                inline=False
            )
        
        return embed
    
    def create_controller_view(self, guild_id: int) -> MusicControllerView:
        """Create a fresh controller view with buttons"""
        return MusicControllerView(self.music_cog, guild_id)
    
    async def update_controller_message(self, message: Message, guild_id: int) -> None:
        """Update an existing controller message with current information"""
        try:
            embed = self.create_controller_embed(guild_id)
            view = self.create_controller_view(guild_id)
            await message.edit(embed=embed, view=view)
            logger.debug(f"Updated controller message for guild {guild_id}")
        except discord.NotFound:
            logger.warning(f"Controller message for guild {guild_id} was not found")
            raise
        except Exception as e:
            logger.error(f"Error updating controller message: {e}")
            raise
    
    async def send_success_message(self, ctx) -> None:
        """Send a success message for controller setup"""
        try:
            await ctx.respond("✅ Music controller has been set up successfully!", ephemeral=True)
        except Exception as e:
            logger.error(f"Error sending success message: {e}")
    
    async def send_error_message(self, ctx) -> None:
        """Send an error message for controller setup"""
        try:
            await ctx.respond("❌ There was an error setting up the music controller.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error sending error message: {e}")