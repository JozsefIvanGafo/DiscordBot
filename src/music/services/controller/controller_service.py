import discord
import logging
from typing import Dict, Optional
from discord import Message
from .state_manager import ControllerStateManager
from .ui_manager import ControllerUIManager

logger = logging.getLogger('discord')

class ModularControllerService:
    def __init__(self, music_cog):
        self.music_cog = music_cog
        self.state_manager = ControllerStateManager()
        self.ui_manager = ControllerUIManager(music_cog)
        
        # Load saved data and schedule restoration
        self.state_manager.load_data()
        if hasattr(music_cog, 'bot'):
            music_cog.bot.loop.create_task(self.restore_controllers())
    
    async def restore_controllers(self) -> None:
        """Restore all saved controllers on bot startup"""
        saved_message_ids = self.state_manager.get_saved_message_ids()
        logger.info(f"Attempting to restore {len(saved_message_ids)} music controllers")
        
        for guild_id, message_id in saved_message_ids.items():
            try:
                channel_id = self.state_manager.get_channel_id(guild_id)
                if not channel_id:
                    logger.warning(f"No channel ID found for guild {guild_id}")
                    continue
                
                channel = self.music_cog.bot.get_channel(int(channel_id))
                if not channel:
                    logger.warning(f"Could not find channel {channel_id} for guild {guild_id}")
                    continue
                
                try:
                    message = await channel.fetch_message(int(message_id))
                    if message:
                        self.state_manager.store_message(guild_id, message)
                        view = self.ui_manager.create_controller_view(int(guild_id))
                        await message.edit(view=view)
                        await self.update_controller(guild_id)
                        logger.info(f"Restored music controller in guild {guild_id}")
                except discord.NotFound:
                    logger.warning(f"Message {message_id} not found in channel {channel_id}")
                except Exception as e:
                    logger.error(f"Could not restore controller message {message_id}: {e}")
            
            except Exception as e:
                logger.error(f"Error restoring controller for guild {guild_id}: {e}")
        
        self.state_manager.clear_saved_message_ids()
    
    async def create_controller(self, ctx) -> None:
        """Show music controller with buttons"""
        guild_id = str(ctx.guild.id)
        
        # Check if we already have a controller for this guild
        existing_controller = None
        existing_message = self.state_manager.get_message(guild_id)
        
        if existing_message:
            try:
                await existing_message.edit(content="Updating controller...")
                existing_controller = existing_message
            except discord.NotFound:
                pass
            except Exception as e:
                logger.error(f"Error checking existing controller: {e}")
        
        embed = self.ui_manager.create_controller_embed(int(guild_id))
        view = self.ui_manager.create_controller_view(int(guild_id))
        
        if existing_controller:
            await existing_controller.edit(embed=embed, view=view)
            await ctx.respond(f"Updated the music controller in <#{existing_controller.channel.id}>", ephemeral=True)
            message = existing_controller
        else:
            message = await ctx.respond(embed=embed, view=view)
            if hasattr(message, 'message'):
                message = message.message
        
        self.state_manager.store_message(guild_id, message, str(ctx.channel.id))
    
    async def setup_persistent_controller(self, ctx) -> bool:
        """Create a persistent controller without directly responding to the interaction"""
        try:
            guild_id = str(ctx.guild.id)
            
            # Clean up existing controller
            await self._cleanup_existing_controller(guild_id)
            
            # Create and send new controller
            embed = self.ui_manager.create_controller_embed(int(guild_id))
            view = self.ui_manager.create_controller_view(int(guild_id))
            message = await ctx.channel.send(embed=embed, view=view)
            
            if not message:
                raise Exception("Failed to create controller message")
            
            self.state_manager.store_message(guild_id, message, str(ctx.channel.id))
            await self.ui_manager.send_success_message(ctx)
            return True
            
        except Exception as e:
            logger.error(f"Error setting up persistent controller: {e}")
            await self.ui_manager.send_error_message(ctx)
            return False
    
    async def _cleanup_existing_controller(self, guild_id: str) -> None:
        """Clean up existing controller if any"""
        message = self.state_manager.get_message(guild_id)
        if message:
            try:
                await message.delete()
            except discord.NotFound:
                pass
            except Exception as e:
                logger.error(f"Error deleting existing controller: {e}")
            self.state_manager.remove_controller(guild_id)
    
    async def update_controller(self, guild_id: str) -> None:
        """Update the music controller for a specific guild with current information"""
        try:
            message = self.state_manager.get_message(str(guild_id))
            if not message:
                logger.debug(f"No controller message found for guild {guild_id}")
                return
            
            await self.ui_manager.update_controller_message(message, int(guild_id))
            
        except discord.NotFound:
            self.state_manager.remove_controller(str(guild_id))
            logger.info(f"Controller message for guild {guild_id} was deleted, removed from registry")
            
        except Exception as e:
            logger.error(f"Error updating controller for guild {guild_id}: {e}")