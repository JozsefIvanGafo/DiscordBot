from collections import deque

class QueueManager:
    def __init__(self):
        self.queues = {}  # guild_id: deque(songs)
        self.current_songs = {}  # guild_id: current_song_info
    
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