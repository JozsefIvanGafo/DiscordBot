import discord
import logging
from ..utils import MusicControllerView, format_duration
from ...utils.json_manager import JsonManager

logger = logging.getLogger('discord')

class ControllerService:
    def __init__(self, music_cog):
        self.music_cog = music_cog
        self.controller_messages = {}  # guild_id: message
        self.json_manager = JsonManager("music_controllers.json")
        
        # Load saved data
        self.load_controller_data()
        
        # Schedule restoring controllers after bot is fully ready
        if hasattr(music_cog, 'bot'):
            music_cog.bot.loop.create_task(self.restore_controllers())
    
    def load_controller_data(self):
        """Load controller configuration from file"""
        try:
            data = self.json_manager.get_all()
            # Convert keys to strings for consistency
            self.music_channels = {k: v for k, v in data.get("music_channels", {}).items()}
            saved_messages = {k: v for k, v in data.get("controller_messages", {}).items()}
            
            # We'll temporarily store the IDs - we'll get the actual message objects later
            self._saved_message_ids = saved_messages
            
            logger.info("Loaded music controller configuration")
        except Exception as e:
            logger.error(f"Error loading music controller configuration: {e}")
            self.music_channels = {}
            self._saved_message_ids = {}
    
    def save_controller_data(self):
        """Save controller configuration to file"""
        try:
            # Extract just the IDs from the controller_messages
            controller_messages_data = {}
            for guild_id, message in self.controller_messages.items():
                if hasattr(message, 'id'):
                    controller_messages_data[guild_id] = str(message.id)
            
            data = {
                "music_channels": self.music_channels,
                "controller_messages": controller_messages_data
            }
            
            self.json_manager.data = data
            self.json_manager.save()
            logger.info("Saved music controller configuration")
                
        except Exception as e:
            logger.error(f"Error saving music controller configuration: {e}")
    
    async def restore_controllers(self):
        """Restore all saved controllers on bot startup"""
        # Wait for bot to be ready
        await self.music_cog.bot.wait_until_ready()
        
        if not hasattr(self, '_saved_message_ids'):
            logger.info("No saved message IDs to restore")
            return
        
        if not self._saved_message_ids:
            logger.info("No music controllers to restore")
            return
            
        logger.info(f"Attempting to restore {len(self._saved_message_ids)} music controllers")
        
        for guild_id, message_id in self._saved_message_ids.items():
            try:
                # Get the channel
                channel_id = self.music_channels.get(guild_id)
                if not channel_id:
                    logger.warning(f"No channel ID found for guild {guild_id}")
                    continue
                    
                channel = self.music_cog.bot.get_channel(int(channel_id))
                if not channel:
                    logger.warning(f"Could not find channel {channel_id} for guild {guild_id}")
                    continue
                
                # Try to get the message
                try:
                    message = await channel.fetch_message(int(message_id))
                    if message:
                        self.controller_messages[guild_id] = message
                        # Create a fresh view and update the message with it
                        view = MusicControllerView(self.music_cog, int(guild_id))
                        await message.edit(view=view)
                        # Update the controller content
                        await self.update_controller(guild_id)
                        logger.info(f"Restored music controller in guild {guild_id}")
                except discord.NotFound:
                    logger.warning(f"Message {message_id} not found in channel {channel_id}")
                except Exception as e:
                    logger.error(f"Could not restore controller message {message_id}: {e}")
            
            except Exception as e:
                logger.error(f"Error restoring controller for guild {guild_id}: {e}")
        
        # Clean up temporary data
        if hasattr(self, '_saved_message_ids'):
            del self._saved_message_ids

    def store_controller_message(self, guild_id, message, channel_id=None):
        """Store the controller message for a guild"""
        guild_id_str = str(guild_id)
        self.controller_messages[guild_id_str] = message
        if channel_id:
            self.music_channels[guild_id_str] = str(channel_id)
        self.save_controller_data()

    async def create_controller(self, ctx):
        """Show music controller with buttons"""
        guild_id = ctx.guild.id
        guild_id_str = str(guild_id)
        
        # Check if we already have a controller for this guild
        existing_controller = None
        if guild_id_str in self.controller_messages:
            try:
                existing_message = self.controller_messages[guild_id_str]
                # Verify the message still exists
                try:
                    await existing_message.edit(content="Updating controller...")
                    existing_controller = existing_message
                except discord.NotFound:
                    # Message was deleted, we'll create a new one
                    pass
                except Exception as e:
                    logger.error(f"Error checking existing controller: {e}")
            except Exception as e:
                logger.error(f"Error retrieving existing controller: {e}")
        
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
        
        if existing_controller:
            # Update existing controller
            await existing_controller.edit(embed=embed, view=view)
            await ctx.respond(f"Updated the music controller in <#{existing_controller.channel.id}>", ephemeral=True)
            message = existing_controller
        else:
            # Send message with buttons and store it for later updating
            message = await ctx.respond(embed=embed, view=view)
            # For bridge commands, we need to extract the actual message
            if hasattr(message, 'message'):
                message = message.message
        
        # Store the message for updating
        self.store_controller_message(guild_id, message, ctx.channel.id)

    async def setup_persistent_controller(self, ctx):
        """Create a persistent controller without directly responding to the interaction"""
        try:
            guild_id = ctx.guild.id
            
            # First clean up any existing controller
            await self._cleanup_existing_controller(guild_id)
            
            # Create and send new controller
            message = await self._create_and_send_controller(ctx, guild_id)
            if not message:
                raise Exception("Failed to create controller message")
                
            # Store the new controller
            self.store_controller_message(guild_id, message, ctx.channel.id)
            
            # Send success message
            await self._send_success_message(ctx)
            return True
            
        except Exception as e:
            logger.error(f"Error setting up persistent controller: {e}")
            await self._send_error_message(ctx)
            return False

    async def _cleanup_existing_controller(self, guild_id):
        """Clean up existing controller if any"""
        guild_id_str = str(guild_id)
        if guild_id_str in self.controller_messages:
            try:
                existing_message = self.controller_messages[guild_id_str]
                try:
                    await existing_message.delete()
                except discord.NotFound:
                    pass
                except Exception as e:
                    logger.error(f"Error deleting existing controller: {e}")
            except Exception as e:
                logger.error(f"Error retrieving existing controller: {e}")

    async def _create_and_send_controller(self, ctx, guild_id):
        """Create and send a new controller message"""
        try:
            embed = await self._create_controller_embed(guild_id)
            view = MusicControllerView(self.music_cog, guild_id)
            return await ctx.channel.send(embed=embed, view=view)
        except Exception as e:
            logger.error(f"Error creating controller message: {e}")
            return None

    async def _create_controller_embed(self, guild_id):
        """Create the controller embed"""
        current_song = self.music_cog.queue_manager.get_current_song(guild_id)
        
        embed = discord.Embed(
            title="🎵 Music Controller",
            description="Control the music playback using the buttons below.",
            color=discord.Color.blue()
        )
        
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
        
        return embed

    async def _send_success_message(self, ctx):
        """Send success message"""
        try:
            await ctx.respond("✅ Music controller has been set up successfully!", ephemeral=True)
        except Exception as e:
            logger.error(f"Error sending success message: {e}")

    async def _send_error_message(self, ctx):
        """Send error message"""
        try:
            await ctx.respond("❌ There was an error setting up the music controller.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error sending error message: {e}")

    async def update_controller(self, guild_id):
        """Update the music controller for a specific guild with current information"""
        try:
            # Convert guild_id to string for consistent lookup
            guild_id_str = str(guild_id)
            
            if guild_id_str not in self.controller_messages:
                logger.debug(f"No controller message found for guild {guild_id}")
                return
                
            message = self.controller_messages[guild_id_str]
            
            # Create updated embed
            current_song = self.music_cog.queue_manager.get_current_song(guild_id)
            
            embed = discord.Embed(
                title="🎵 Music Controller",
                description="Control the music playback using the buttons below.",
                color=discord.Color.blue()
            )
            
            # Get voice client status
            voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
            status = "Disconnected"
            if voice_client:
                status = "Playing" if voice_client.is_playing() else "Paused" if voice_client.is_paused() else "Connected (Idle)"
                
            # Add info about current song if playing
            if current_song:
                from ..utils import format_duration
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
            
            # Create fresh controller view
            from ..utils.controller import MusicControllerView
            view = MusicControllerView(self.music_cog, guild_id)
            
            # Update the message
            await message.edit(embed=embed, view=view)
            logger.debug(f"Updated controller message for guild {guild_id}")
            
        except discord.NotFound:
            # Message was deleted, remove from our registry
            if str(guild_id) in self.controller_messages:
                del self.controller_messages[str(guild_id)]
            logger.info(f"Controller message for guild {guild_id} was deleted, removed from registry")
            self.save_controller_data()
            
        except Exception as e:
            logger.error(f"Error updating controller for guild {guild_id}: {e}")