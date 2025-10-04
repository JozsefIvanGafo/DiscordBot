from collections import deque

class QueueManager:
    def __init__(self):
        self.queues = {}  # guild_id: deque(songs)
        self.current_songs = {}  # guild_id: current_song_info
        self.repeat_mode = {}  # guild_id: 'off', 'one', or 'all'
    
    def get_queue(self, guild_id):
        """Get the queue for a guild"""
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        return self.queues[guild_id]
    
    def get_current_song(self, guild_id):
        """Get the current song for a guild"""
        return self.current_songs.get(guild_id)
    
    def set_current_song(self, guild_id, song):
        """Set the current song for a guild"""
        self.current_songs[guild_id] = song
    
    def clear_current_song(self, guild_id):
        """Clear the current song for a guild"""
        if guild_id in self.current_songs:
            del self.current_songs[guild_id]
    
    def add_to_queue(self, guild_id, song):
        """Add a song to the queue"""
        self.get_queue(guild_id).append(song)
    
    def add_multiple_to_queue(self, guild_id, songs):
        """Add multiple songs to the queue"""
        queue = self.get_queue(guild_id)
        for song in songs:
            queue.append(song)
    
    def get_next_song(self, guild_id):
        """Get the next song in the queue"""
        queue = self.get_queue(guild_id)
        if not queue:
            return None
        return queue.popleft()
    
    def clear_queue(self, guild_id):
        """Clear the queue for a guild"""
        self.queues[guild_id] = deque()
    
    def clear_guild_data(self, guild_id):
        """Clear all data for a guild"""
        if guild_id in self.queues:
            del self.queues[guild_id]
        if guild_id in self.current_songs:
            del self.current_songs[guild_id]
        if guild_id in self.repeat_mode:
            del self.repeat_mode[guild_id]
    
    def get_repeat_mode(self, guild_id):
        """Get the repeat mode for a guild"""
        return self.repeat_mode.get(guild_id, 'off')
    
    def set_repeat_mode(self, guild_id, mode):
        """Set the repeat mode for a guild. Modes: 'off', 'one', 'all'"""
        if mode in ['off', 'one', 'all']:
            self.repeat_mode[guild_id] = mode
        else:
            raise ValueError(f"Invalid repeat mode: {mode}. Must be 'off', 'one', or 'all'")
    
    def toggle_repeat(self, guild_id):
        """Toggle through repeat modes: off -> one -> all -> off"""
        current = self.get_repeat_mode(guild_id)
        if current == 'off':
            self.repeat_mode[guild_id] = 'one'
            return 'one'
        elif current == 'one':
            self.repeat_mode[guild_id] = 'all'
            return 'all'
        else:  # 'all'
            self.repeat_mode[guild_id] = 'off'
            return 'off'