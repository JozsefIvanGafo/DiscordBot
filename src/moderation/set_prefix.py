import os
import discord
from discord.ext import commands ,bridge
import logging


logger = logging.getLogger('discord')

class SetPrefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # Helper function for ping commands
    async def _set_prefix(self, ctx,prefix):
        ctx.bot.command_prefix = prefix
        response = f"Prefix set to {prefix}"   
        await ctx.respond(response)

       
    
    # Prefix and slash commands

    @bridge.bridge_command(name="set_prefix", 
                           description="Replies with the bot's latency.",
                           )
    @commands.has_permissions(administrator=True)
    async def ping_prefix(self, ctx,prefix):
        """Check the bot's latency"""
        await self._set_prefix(ctx,prefix)
    

def setup(bot):
    bot.add_cog(SetPrefix(bot))