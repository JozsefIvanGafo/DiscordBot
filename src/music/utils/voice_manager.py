import logging
import discord

logger = logging.getLogger('discord')

class VoiceManager:
    def __init__(self):
        self.voice_clients = {}  # guild_id: VoiceClient
    
    def get_voice_client(self, guild_id):
        """Get the voice client for a guild"""
        return self.voice_clients.get(guild_id)
    
    def set_voice_client(self, guild_id, voice_client):
        """Set the voice client for a guild"""
        self.voice_clients[guild_id] = voice_client
    
    def clear_voice_client(self, guild_id):
        """Clear the voice client for a guild"""
        if guild_id in self.voice_clients:
            del self.voice_clients[guild_id]
    
    async def join_voice_channel(self, ctx):
        """Join a voice channel"""
        user = ctx.user
        if ctx.author.voice is None:
            await ctx.respond("You need to be in a voice channel to use this command")
            return None
        
        voice_channel = ctx.author.voice.channel
        guild_id = ctx.guild.id
        
        # Check if already connected
        voice_client = self.get_voice_client(guild_id)
        if voice_client and voice_client.is_connected():
            # Move to new channel if needed
            if voice_client.channel != voice_channel:
                await voice_client.move_to(voice_channel)
            return voice_client
        
        # Connect to voice channel
        try:
            voice_client = await voice_channel.connect()
            self.set_voice_client(guild_id, voice_client)
            return voice_client
        except Exception as e:
            logger.error(f"Error connecting to voice channel: {e}")
            await ctx.respond(f"Error connecting to voice channel: {str(e)}")
            return None