import discord
from discord.ext import commands ,bridge
import logging

logger = logging.getLogger('discord')

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # Helper function for ping commands
    async def _do_ping(self, ctx, is_slash=True):
        latency = round(self.bot.latency * 1000)
        response = f"🏓 Pong! Latency: {latency}ms"
        await ctx.respond(response)
    
    
    # Helper function for pingdetailed commands
    async def _do_ping_detailed(self, ctx, is_slash=True):
        ws_latency = round(self.bot.latency * 1000)
        
        start = discord.utils.utcnow()
    
        message = await ctx.respond("Testing API latency...")
        
        end = discord.utils.utcnow()
        api_latency = (end - start).total_seconds() * 1000
        
        embed = discord.Embed(title="🏓 Pong!", color=discord.Color.green())
        embed.add_field(name="WebSocket Latency", value=f"{ws_latency}ms", inline=True)
        embed.add_field(name="API Latency", value=f"{round(api_latency)}ms", inline=True)
        
        await message.edit(content=None, embed=embed)
    
    # Prefix commands
    @bridge.bridge_command(name="ping", description="Replies with the bot's latency.")
    async def ping_prefix(self, ctx):
        """Check the bot's latency"""
        await self._do_ping(ctx, is_slash=False)
    
    @bridge.bridge_command(name="pingdetailed", aliases=["pd"], description="Check the bot's websocket and API latency")
    async def ping_detailed_prefix(self, ctx):
        """Check the bot's websocket and API latency"""
        await self._do_ping_detailed(ctx, is_slash=False)


    # Slash commands
    
def setup(bot):
    bot.add_cog(Ping(bot))