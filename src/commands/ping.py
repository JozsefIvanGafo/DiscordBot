import discord
from discord.ext import commands
import logging

logger = logging.getLogger('discord')

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="ping")
    async def ping(self, ctx):
        """Check the bot's latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency: {latency}ms")
    
    @discord.slash_command(name="ping", description="Check the bot's latency")
    async def slash_ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.respond(f"🏓 Pong! Latency: {latency}ms")
        
    @commands.command(name="pingdetailed", aliases=["pd"])
    async def ping_detailed(self, ctx):
        """Check the bot's websocket and API latency"""
        ws_latency = round(self.bot.latency * 1000)
        
        start = discord.utils.utcnow()
        message = await ctx.send("Testing API latency...")
        end = discord.utils.utcnow()
        api_latency = (end - start).total_seconds() * 1000
        
        embed = discord.Embed(title="🏓 Pong!", color=discord.Color.green())
        embed.add_field(name="WebSocket Latency", value=f"{ws_latency}ms", inline=True)
        embed.add_field(name="API Latency", value=f"{round(api_latency)}ms", inline=True)
        
        await message.edit(content=None, embed=embed)

# This is the critical function - make sure it's exactly like this
async def setup(bot):
    await bot.add_cog(Ping(bot))