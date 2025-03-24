import logging
import discord

logger = logging.getLogger('discord')
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