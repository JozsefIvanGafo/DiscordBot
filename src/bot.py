import discord
from discord.ext import commands
import os
import logging
from typing import Optional
from src.commands.ping import Ping

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('discord')

class DiscordBot(commands.Bot):
    def __init__(self, command_prefix: str, owner_id: int, **kwargs):
        """Initialise the bot with the given command prefix and owner ID"""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=command_prefix,
            owner_id=owner_id,
            intents=intents,
            **kwargs
        )


    async def on_ready(self) -> None:
        """Called when the bot is ready to use"""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} guilds')

        # Try direct cog loading instead of extension loading
        if not hasattr(self, '_ready_called'):
            logger.info("Loading cogs directly in on_ready")
            try:
                #TODO: Make it dynamic
                #from src.commands.ping import Ping
                self.add_cog(Ping(self))





                logger.info("Added Ping cog directly")
                # Debug: Log all registered commands
                all_commands = [cmd.name for cmd in self.commands]
                logger.info(f'Registered commands: {all_commands}')
            except Exception as e:
                logger.error(f"Error loading Ping cog directly: {e}")
            
            self._ready_called = True

def create_bot(prefix: str, owner_id: str) -> DiscordBot:
    """Create and return a bot instance"""
    return DiscordBot(command_prefix=prefix, owner_id=int(owner_id))