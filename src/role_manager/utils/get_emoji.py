import re
import discord
# Find emoji ID from custom emoji string
def get_emoji_from_str(emoji_str):
    """Extract emoji information from a string"""
    # Standard unicode emoji
    if len(emoji_str) <= 2:
        return emoji_str
        
    # Try to extract custom emoji data
    match = re.match(r'<(a?):([a-zA-Z0-9_]+):(\d+)>', emoji_str)
    if match:
        animated, name, emoji_id = match.groups()
        return discord.PartialEmoji(name=name, id=int(emoji_id), animated=bool(animated))
    
    # Default fallback
    return None