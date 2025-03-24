import logging
import discord

logger = logging.getLogger('discord')

class CommandHandlers:
    def __init__(self, music_cog):
        self.music_cog = music_cog
    
    async def handle_play(self, ctx, url):
        """Handle play command"""
        guild_id = ctx.guild.id
        
        # Join voice channel first
        voice_client = await self.music_cog.voice_manager.join_voice_channel(ctx)
        if voice_client is None:
            return
        
        # Play the song
        await self.music_cog.player_service.play_song(guild_id, ctx, url)
        
        # Make sure the controller is displayed and updated
        if guild_id not in self.music_cog.controller_service.controller_messages:
            await self.handle_controller(ctx)
        else:
            await self.music_cog.controller_service.update_controller(guild_id)
    
    async def handle_stop(self, ctx):
        """Handle stop command"""
        guild_id = ctx.guild.id
        voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
        
        if voice_client and voice_client.is_connected():
            await self.music_cog.player_service.stop(guild_id)
            await ctx.respond("Playback stopped and queue cleared")
        else:
            await ctx.respond("Not currently playing anything")
    
    async def handle_skip(self, ctx):
        """Handle skip command"""
        guild_id = ctx.guild.id
        voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
        
        if voice_client and voice_client.is_connected() and voice_client.is_playing():
            voice_client.stop()  # This will trigger play_next via the after callback
            await ctx.respond("Skipped current song")
        else:
            await ctx.respond("Not currently playing anything")
    
    async def handle_queue(self, ctx):
        """Handle queue command"""
        try:
            guild_id = ctx.guild.id
            queue = self.music_cog.queue_manager.get_queue(guild_id)
            current_song = self.music_cog.queue_manager.get_current_song(guild_id)
            
            if not queue and not current_song:
                await ctx.respond("The queue is empty. Use `/play` to add songs.",ephemeral=True)
                return
            
            # Build embed for queue display
            embed = discord.Embed(
                title="🎵 Music Queue",
                color=discord.Color.blue()
            )
            
            # Add current song if playing
            if current_song:
                embed.add_field(
                    name="Now Playing",
                    value=f"[{current_song['title']}]({current_song['webpage_url']})",
                    inline=False
                )
            
            # Add upcoming songs
            if queue:
                queue_text = ""
                for i, song in enumerate(queue[:10]):
                    queue_text += f"{i+1}. [{song['title']}]({song['webpage_url']})\n"
                
                if len(queue) > 10:
                    queue_text += f"\n... and {len(queue) - 10} more songs"
                
                embed.add_field(
                    name="Up Next",
                    value=queue_text,
                    inline=False
                )
            
            await ctx.respond(embed=embed)
            
        except Exception as e:
            logger.error(f"Error displaying queue: {e}", exc_info=True)
            await ctx.respond("⚠️ There was an error displaying the queue.")
    
    async def handle_leave(self, ctx):
        """Handle leave command"""
        try:
            guild_id = ctx.guild.id
            voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
            
            if voice_client and voice_client.is_connected():
                # Stop playback and clear queue
                await self.music_cog.player_service.stop(guild_id)
                
                # Disconnect from voice
                await voice_client.disconnect()
                self.music_cog.voice_manager.clear_voice_client(guild_id)
                
                # Update controller if needed
                await self.music_cog.controller_service.update_controller(guild_id)
                
                await ctx.respond("Disconnected from voice channel")
            else:
                await ctx.respond("Not currently in a voice channel")
                
        except Exception as e:
            logger.error(f"Error handling leave command: {e}", exc_info=True)
            await ctx.respond("⚠️ There was an error disconnecting from the voice channel.")
    
    async def handle_controller(self, ctx):
        """Handle controller command"""
        try:
            guild_id = ctx.guild.id
            
            # Create the controller in the current channel
            await self.music_cog.controller_service.create_controller(ctx)
            
            # Respond with confirmation
            #await ctx.respond("Music controller displayed", ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error creating controller: {e}", exc_info=True)
            await ctx.respond("⚠️ There was an error displaying the music controller.")
    
    async def handle_music_channel(self, ctx):
        """Set the current channel as the dedicated music channel for the bot's music controller"""
        try:
            guild_id = ctx.guild.id
            channel_id = ctx.channel.id
            
            # Store the channel as the music channel
            self.music_cog.controller_service.music_channels[guild_id] = channel_id
            
            # Clean up any existing controller message
            if guild_id in self.music_cog.controller_service.controller_messages:
                try:
                    message = self.music_cog.controller_service.controller_messages[guild_id]
                    await message.edit(view=None)
                    del self.music_cog.controller_service.controller_messages[guild_id]
                except Exception as e:
                    logger.error(f"Error cleaning up old controller: {e}")
            
            # Create a new controller in this channel
            await self.music_cog.controller_service.create_controller(ctx)
            
            #await ctx.respond(f"🎵 This channel has been set as the music control channel for this server.", ephemeral=True)
            
            logger.info(f"Set music channel for guild {guild_id} to channel {channel_id}")
        except Exception as e:
            logger.error(f"Error setting music channel: {e}", exc_info=True)
            await ctx.respond("⚠️ There was an error setting up the music channel. Please try again.", ephemeral=True)

