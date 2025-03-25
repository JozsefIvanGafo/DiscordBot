import re
def is_valid_emoji(emoji_str):
    """Check if a string is a valid Discord emoji"""
    if not emoji_str:
        return False
        
    # Check for standard unicode emoji (simple approach)
    if len(emoji_str) == 1 or len(emoji_str) == 2:
        return True
        
    # Check for custom emoji format <:name:id> or <a:name:id>
    custom_emoji_pattern = r'<a?:[a-zA-Z0-9_]+:\d+>'
    return bool(re.fullmatch(custom_emoji_pattern, emoji_str))