import os
import discord
from discord.ext import commands, bridge
import logging
import random
import asyncio

logger = logging.getLogger('discord')

class Roulette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        current_path = os.path.dirname(os.path.abspath(__file__))
        src_path = os.path.dirname(current_path)
        self.data_folder = os.path.join(src_path, 'data')
        os.makedirs(self.data_folder, exist_ok=True)
        self.games_file = os.path.join(self.data_folder, 'games.txt')
        self._ensure_games_file_exists()
    
    def _ensure_games_file_exists(self):
        """Create a games file with sample games if it doesn't exist"""
        if not os.path.exists(self.games_file):
            sample_games = [
                "Minecraft", "Fortnite", "Call of Duty", "League of Legends",
                "Among Us", "Valorant", "GTA V", "Apex Legends",
                "Rocket League", "Counter-Strike"
            ]
            with open(self.games_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(sample_games))
    
    def read_games(self):
        try:
            with open(self.games_file, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            logger.error(f"Error reading games file: {e}", exc_info=True)
            return ["Error reading games"]
    
    @bridge.bridge_command(
        name="roulette",
        description="Run a roulette to select a random game"
    )
    async def text_roulette(self, ctx, channel: discord.TextChannel = None):
        # Setup
        channel = channel or ctx.channel
        games = self.read_games()
        if len(games) < 2:
            await ctx.respond("Not enough games in the list.", ephemeral=True)
            return
        
        winner = random.choice(games)
        await ctx.respond("Spinning the wheel...", ephemeral=True)
        
        # Initialize with an embed
        embed = discord.Embed(
            title="🎮 Game Roulette",
            description="Spinning the wheel...",
            color=discord.Color.blue()
        )
        msg = await channel.send(embed=embed)
        
        # Initial spinning animation using embed
        spinner = ["⠋", "⠙", "⠸", "⠴"]
        for i, char in enumerate(spinner):
            embed.description = f"{char} Spinning..."
            embed.color = discord.Color.blue()
            await msg.edit(embed=embed)
            await asyncio.sleep(0.2)
        
        # Create a list of ~30 games to show (with repetitions allowed)
        # First phase: Fast games (15 games)
        fast_games = random.choices(games, k=15)
        
        # Second phase: Medium speed games (10 games)
        medium_games = random.choices(games, k=10)
        
        # Final phase: Slow games (5 games)
        final_games = random.choices(games, k=5)
        
        # Combine all phases + winner
        games_to_show = fast_games + medium_games + final_games + [winner]
        
        # Fast batch editing - group edits to avoid rate limiting
        # Display games with appropriate delays and colors based on position
        for i, game in enumerate(games_to_show):
            # Set color based on phase
            if i < 15:
                embed.color = discord.Color.gold()  # Fast phase - gold
                emoji = "🔄"
                delay = 0.01
            elif i < 25:
                embed.color = discord.Color.orange()  # Medium phase - orange
                emoji = "🔄"
                delay = 0.01
            elif i < 30:
                embed.color = discord.Color.red()  # Slow phase - red
                emoji = "⏱️"
                delay = 0.2
            else:
                embed.color = discord.Color.green()  # Winner - green
                emoji = "🎯"
                delay = 0.7
            
            # Show the game in the embed
            embed.description = f"{emoji} **{game}**"
            
            # Group edits for fast phase to avoid rate limiting
            if i < 15 and i % 4 == 0:
                await msg.edit(embed=embed)
                await asyncio.sleep(0.04)  # Small delay for batch updates
            elif i < 25 and i % 3 == 0:
                await msg.edit(embed=embed)
                await asyncio.sleep(0.03)  # Small delay for batch updates
            else:
                await msg.edit(embed=embed)
                await asyncio.sleep(delay)
        
        # Final result with a green embed
        final_embed = discord.Embed(
            title="🎮 Game Roulette Result!",
            description=f"🎉 The wheel has chosen: **{winner}**!",
            color=discord.Color.green()
        )
        final_embed.set_footer(text="Let's play! 🎮")
        await msg.edit(embed=final_embed)
    
    @commands.has_permissions(administrator=True)
    @bridge.bridge_command(name="addgame", description="Add a game to the roulette games list")
    async def add_game(self, ctx, *, game: str):
        try:
            games = self.read_games()
            if game in games:
                await ctx.respond(f"'{game}' is already in the games list.", ephemeral=True)
                return
            
            with open(self.games_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{game}")
            
            await ctx.respond(f"Added '{game}' to the games list!", ephemeral=True)
        except Exception as e:
            logger.error(f"Error adding game: {e}", exc_info=True)
            await ctx.respond(f"Error adding game: {str(e)}", ephemeral=True)

    @commands.has_permissions(administrator=True)
    @bridge.bridge_command(name="removegame", description="Remove a game from the roulette games list")
    async def remove_game(self, ctx, *, game: str):
        try:
            games = self.read_games()
            if game not in games:
                await ctx.respond(f"'{game}' is not in the games list.", ephemeral=True)
                return
            
            games.remove(game)
            with open(self.games_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(games))
            
            await ctx.respond(f"Removed '{game}' from the games list!", ephemeral=True)
        except Exception as e:
            logger.error(f"Error removing game: {e}", exc_info=True)
            await ctx.respond(f"Error removing game: {str(e)}", ephemeral=True)
    
    @bridge.bridge_command(name="listgames", description="List all games in the roulette games list")
    async def list_games(self, ctx):
        games = self.read_games()
        
        if not games:
            await ctx.respond("The games list is empty.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎮 Roulette Games List",
            description="\n".join(f"• {game}" for game in games),
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Total games: {len(games)}")
        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Roulette(bot))