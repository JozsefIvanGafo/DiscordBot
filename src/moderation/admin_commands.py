import discord
from discord.ext import commands, bridge
import logging
import sys
import os

logger = logging.getLogger('discord')

class AdminCommands(commands.Cog):
    """Administrative commands for bot management"""
    
    def __init__(self, bot):
        self.bot = bot
        logger.info("Admin commands cog loaded")
    
    @commands.has_permissions(administrator=True)
    @bridge.bridge_command(name="shutdown", description="Shutdown the bot (Administrator only)")
    async def shutdown(self, ctx):
        """Shutdown the bot"""
        await ctx.respond("🛑 Shutting down bot...", ephemeral=True)
        logger.info(f"Bot shutdown initiated by {ctx.author} (ID: {ctx.author.id})")
        
        # Schedule the shutdown
        import asyncio
        asyncio.create_task(self._shutdown_bot())
    
    async def _shutdown_bot(self):
        """Internal method to shutdown the bot"""
        import asyncio
        
        # Wait a moment for the response to be sent
        await asyncio.sleep(1)
        
        logger.info("Closing bot connections...")
        
        # Close all voice clients
        for voice_client in self.bot.voice_clients:
            try:
                await voice_client.disconnect(force=True)
            except:
                pass
        
        # Close the bot connection
        await self.bot.close()
        
        # Wait for cleanup
        await asyncio.sleep(1)
        
        logger.info("Shutting down...")
        
        # Exit the program
        sys.exit(0)

def setup(bot):
    bot.add_cog(AdminCommands(bot))
