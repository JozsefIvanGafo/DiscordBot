import discord
import logging
from ..utils import MusicControllerView, format_duration

logger = logging.getLogger('discord')

class ControllerService:
    def __init__(self, music_cog):
        self.music_cog = music_cog
        self.controller_messages = {}  # guild_id: message
        self.music_channels = {}       # guild_id: channel_id
    
    def store_controller_message(self, guild_id, message):
        """Store the controller message for a guild"""
        self.controller_messages[guild_id] = message
    
    async def update_controller(self, guild_id):
        """Update the controller message for a guild"""
        if guild_id not in self.controller_messages:
            return
        
        message = self.controller_messages[guild_id]
        
        try:
            # Create updated embed
            current_song = self.music_cog.queue_manager.get_current_song(guild_id)
            voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
            
            embed = discord.Embed(
                title="🎵 Music Controller",
                description="Control the music playback using the buttons below.",
                color=discord.Color.blue()
            )
            
            # Add info about current song if playing
            if current_song:
                duration = format_duration(current_song['duration'])
                
                # Show playback status
                status = "⏸️ Paused" if voice_client and voice_client.is_paused() else "▶️ Playing"
                
                embed.add_field(
                    name=f"Now {status}",
                    value=f"[{current_song['title']}]({current_song['webpage_url']}) ({duration})",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Status",
                    value="Nothing is currently playing. Use `commands or the buttons` to add songs to the queue.",
                    inline=False
                )
            
            # Create new view (buttons)
            view = MusicControllerView(self.music_cog, guild_id)
            
            # Edit message
            await message.edit(embed=embed, view=view)
        except Exception as e:
            logger.error(f"Error updating controller: {e}")
            # Remove message from tracking if it was deleted or can't be updated
            if "Unknown Message" in str(e):
                if guild_id in self.controller_messages:
                    del self.controller_messages[guild_id]
    
    async def create_controller(self, ctx):
        """Show music controller with buttons"""
        guild_id = ctx.guild.id
        
        # Create controller embed
        current_song = self.music_cog.queue_manager.get_current_song(guild_id)
        
        embed = discord.Embed(
            title="🎵 Music Controller",
            description="Control the music playback using the buttons below.",
            color=discord.Color.blue()
        )
        
        # Add info about current song if playing
        if current_song:
            duration = format_duration(current_song['duration'])
            embed.add_field(
                name="Now Playing",
                value=f"[{current_song['title']}]({current_song['webpage_url']}) ({duration})",
                inline=False
            )
        else:
            embed.add_field(
                name="Status",
                value="Nothing is currently playing. Use `/play <song name or URL>` to add songs to the queue.",
                inline=False
            )
        
        # Create controller view
        view = MusicControllerView(self.music_cog, guild_id)
        
        # Send message with buttons and store it for later updating
        message = await ctx.respond(embed=embed, view=view)
        # For bridge commands, we need to extract the actual message
        if hasattr(message, 'message'):
            message = message.message
        
        # Store the message for updating
        self.store_controller_message(guild_id, message)