import discord
from discord.ui import View, Button
from .utils import (AddSongModal,
                    get_volume_percentage,
                    volume_down_callback,
                    volume_up_callback,
                    play_pause_callback,
                    skip_callback,
                    clear_queue_callback,
                    queue_callback,
                    play_next,
                    join_vc_callback,
                    leave_vc_callback,
                    repeat_callback)


class MusicControllerView(View):
    def __init__(self, music_cog, guild_id, timeout=None):  # None means no timeout - persistent controller
        super().__init__(timeout=timeout)
        self.music_cog = music_cog
        self.guild_id = guild_id
        self.setup_buttons()
    
    def setup_buttons(self):
        
        # Play/Pause button
        play_button = Button(style=discord.ButtonStyle.primary,
                              label="⏯️ Play/Pause",
                                custom_id="music_play_pause")
        play_button.callback = self.play_pause_callback
        
        #Skip button
        skip_button = Button(style=discord.ButtonStyle.primary,
                              label="⏭️ Skip",
                                custom_id="music_skip")
        skip_button.callback = self.skip_callback
        
        #Clear button
        clear_queue_button = Button(style=discord.ButtonStyle.danger,
                                     label="🗑️ Clear Queue",
                                       custom_id="music_clear_queue")
        clear_queue_button.callback = self.clear_queue_callback
        
        #queue button
        queue_button = Button(style=discord.ButtonStyle.secondary,
                               label="📋 Queue",
                                 custom_id="music_queue")
        queue_button.callback = self.queue_callback
        
        # Add song button
        add_song_button = Button(style=discord.ButtonStyle.primary,
                  label="🎵 Add Song",
                  custom_id="music_add_song")
        add_song_button.callback = self.add_song_callback
        
        # Volume control buttons
        volume_down_button = Button(style=discord.ButtonStyle.secondary, 
                                    label="🔉 -10%", 
                                    custom_id="music_volume_down")
        volume_down_button.callback = self.volume_down_callback
        
        # Volume display button (disabled, just shows current volume)
        volume_display_button = Button(
            style=discord.ButtonStyle.secondary, 
            label=f"🔊 {self.get_volume_percentage()}%", 
            custom_id="music_volume_display",
            disabled=True
        )
        
        volume_up_button = Button(style=discord.ButtonStyle.secondary,
                                   label="🔊 +10%",
                                     custom_id="music_volume_up")
        volume_up_button.callback = self.volume_up_callback
        
        # Join and leave buttons
        join_button = Button(style=discord.ButtonStyle.success,
                              label="🎤 Join VC",
                                custom_id="music_join_vc")
        join_button.callback = self.join_vc_callback
        
        leave_button = Button(style=discord.ButtonStyle.danger,
                               label="👋 Leave VC",
                                 custom_id="music_leave_vc")
        leave_button.callback = self.leave_vc_callback
        
        # Repeat button
        repeat_mode = self.music_cog.queue_manager.get_repeat_mode(self.guild_id)
        repeat_emojis = {'off': '⏹️', 'one': '🔂', 'all': '🔁'}
        repeat_button = Button(style=discord.ButtonStyle.secondary,
                                label=f"{repeat_emojis[repeat_mode]} Repeat",
                                  custom_id="music_repeat")
        repeat_button.callback = self.repeat_callback
        
        # Refresh button - moved to end
        refresh_button = Button(style=discord.ButtonStyle.secondary,
                                 label="🔄 Refresh",
                                   custom_id="music_refresh")
        refresh_button.callback = self.refresh_callback
        
        # Add buttons to the view - first row
        self.add_item(play_button)
        self.add_item(add_song_button)
        self.add_item(skip_button)
        self.add_item(queue_button)
        self.add_item(clear_queue_button)
        
        # Second row - volume controls
        self.add_item(volume_down_button)
        self.add_item(volume_display_button) 
        self.add_item(volume_up_button)
        self.add_item(join_button)
        self.add_item(leave_button)
        
        # Third row - repeat and refresh
        self.add_item(repeat_button)
        self.add_item(refresh_button)

    def get_volume_percentage(self):
        """Get current volume as percentage, rounded to the nearest 10%"""
        return get_volume_percentage(self)
    
    async def volume_down_callback(self, interaction):
        """Decrease volume by 10%"""
        await volume_down_callback(self, interaction)

    async def volume_up_callback(self, interaction):
        """Increase volume by 10%"""
        await volume_up_callback(self, interaction)

    async def play_pause_callback(self, interaction):
        """Toggle between playing and pausing"""
        await play_pause_callback(self, interaction)
    
    async def skip_callback(self, interaction):
        """Skip the current song"""
        await skip_callback(self, interaction)
    
    async def clear_queue_callback(self, interaction):
        """Clear the queue"""
        await clear_queue_callback(self, interaction)
    
    async def queue_callback(self, interaction):
        """Show the queue"""
        await queue_callback(self, interaction)
    
    async def refresh_callback(self, interaction: discord.Interaction):
        """Refresh the controller"""
        # Acknowledge the interaction
        await interaction.response.defer(ephemeral=True)
        
        # Update the controller
        await self.music_cog.controller_service.update_controller(self.guild_id)
        
        # Send confirmation
        await interaction.followup.send("Controller refreshed!", ephemeral=True)

    async def add_song_callback(self, interaction):
        """Show a modal to add a song"""
        # Create the modal
        modal = AddSongModal(self.music_cog, self.guild_id)

        # Send the modal
        await interaction.response.send_modal(modal)
    
    async def repeat_callback(self, interaction):
        """Toggle repeat mode"""
        await repeat_callback(self, interaction)

    async def play_next(self, guild_id):
        """Play the next song in the queue"""
        await play_next(self, guild_id)

    async def join_vc_callback(self, interaction):
        """Join the user's voice channel"""
        await join_vc_callback(self, interaction)

    async def leave_vc_callback(self, interaction):
        """Leave the voice channel"""
        await leave_vc_callback(self, interaction)