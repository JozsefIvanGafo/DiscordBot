import logging
import discord

logger = logging.getLogger('discord')

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