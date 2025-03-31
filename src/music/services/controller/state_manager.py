import logging
from typing import Dict, Optional
from discord import Message
from ....utils.json_manager import JsonManager

logger = logging.getLogger('discord')

class ControllerStateManager:
    def __init__(self):
        self.controller_messages: Dict[str, Message] = {}
        self.music_channels: Dict[str, str] = {}
        self.json_manager = JsonManager("music_controllers.json")
        self._saved_message_ids: Dict[str, str] = {}
        
    def load_data(self) -> None:
        """Load controller configuration from file"""
        try:
            data = self.json_manager.get_all()
            self.music_channels = {k: v for k, v in data.get("music_channels", {}).items()}
            self._saved_message_ids = {k: v for k, v in data.get("controller_messages", {}).items()}
            logger.info("Loaded music controller configuration")
        except Exception as e:
            logger.error(f"Error loading music controller configuration: {e}")
            self.music_channels = {}
            self._saved_message_ids = {}
    
    def save_data(self) -> None:
        """Save controller configuration to file"""
        try:
            controller_messages_data = {}
            for guild_id, message in self.controller_messages.items():
                if hasattr(message, 'id'):
                    controller_messages_data[guild_id] = str(message.id)
            
            data = {
                "music_channels": self.music_channels,
                "controller_messages": controller_messages_data
            }
            
            self.json_manager.data = data
            self.json_manager.save()
            logger.info("Saved music controller configuration")
        except Exception as e:
            logger.error(f"Error saving music controller configuration: {e}")
    
    def store_message(self, guild_id: str, message: Message, channel_id: Optional[str] = None) -> None:
        """Store the controller message for a guild"""
        self.controller_messages[guild_id] = message
        if channel_id:
            self.music_channels[guild_id] = str(channel_id)
        self.save_data()
    
    def get_message(self, guild_id: str) -> Optional[Message]:
        """Get the stored message for a guild"""
        return self.controller_messages.get(guild_id)
    
    def get_channel_id(self, guild_id: str) -> Optional[str]:
        """Get the stored channel ID for a guild"""
        return self.music_channels.get(guild_id)
    
    def get_saved_message_ids(self) -> Dict[str, str]:
        """Get the saved message IDs"""
        return self._saved_message_ids
    
    def clear_saved_message_ids(self) -> None:
        """Clear the saved message IDs after restoration"""
        self._saved_message_ids = {}
    
    def remove_controller(self, guild_id: str) -> None:
        """Remove a controller from storage"""
        if guild_id in self.controller_messages:
            del self.controller_messages[guild_id]
        if guild_id in self.music_channels:
            del self.music_channels[guild_id]
        self.save_data()