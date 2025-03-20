import discord
from discord.ext import commands, bridge
import logging
from src.commands.ping import Ping
from src.moderation.set_prefix import SetPrefix

# Log info
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('discord')

class DiscordBot(bridge.Bot):
    """A subclass of `commands.Bot` with additional functionality"""
    
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

    async def load_extensions(self) -> None:
        """Load all extensions"""
        logger.info('Loading extensions...')
        self.add_cog(Ping(self))
        self.add_cog(SetPrefix(self))
        
        #check extension loaded
        logger.info('Extensions loaded')

    async def on_ready(self) -> None:
        """Called when the bot is ready to use"""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} guilds')
        

def create_bot(prefix: str, owner_id: str) -> DiscordBot:
    """Create and return a bot instance"""
    return DiscordBot(command_prefix=prefix, owner_id=int(owner_id))