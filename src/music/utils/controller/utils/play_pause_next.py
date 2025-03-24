import discord

async def play_pause_callback(self, interaction):
        """Toggle between playing and pausing"""
        await interaction.response.defer(ephemeral=True)
        voice_client = self.music_cog.voice_manager.get_voice_client(self.guild_id)
        
        if not voice_client or not voice_client.is_connected():
            await interaction.followup.send("I'm not connected to a voice channel", ephemeral=True)
            return
        
        # Check if a song is loaded but paused
        current_song = self.music_cog.queue_manager.get_current_song(self.guild_id)
        if not current_song:
            # No song loaded, check if there's anything in the queue to play
            queue = self.music_cog.queue_manager.get_queue(self.guild_id)
            if queue:
                await self.music_cog.player_service.play_next(self.guild_id)
                await interaction.followup.send("Started playing the next song in queue", ephemeral=True)
            else:
                await interaction.followup.send("The queue is empty", ephemeral=True)
            return
        
        # Toggle between pause and resume
        if voice_client.is_playing():
            voice_client.pause()
            await interaction.followup.send("Paused playback", ephemeral=True)
        elif voice_client.is_paused():
            voice_client.resume()
            await interaction.followup.send("Resumed playback", ephemeral=True)
        else:
            # Not playing or paused, but we have a current song - start playing it
            await self.music_cog.player_service.play_next(self.guild_id)
            await interaction.followup.send("Started playback", ephemeral=True)
        
        # Update the controller
        await self.music_cog.controller_service.update_controller(self.guild_id)


async def play_next(self, guild_id):
    """Play the next song in the queue"""
    voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
    if not voice_client or not voice_client.is_connected():
        return
    next_song = self.music_cog.queue_manager.get_next_song(guild_id)
    if not next_song:
        return
    source_url = next_song['url']
    source = discord.FFmpegPCMAudio(source_url)
    volume_source = discord.PCMVolumeTransformer(source, volume=1.0)
    voice_client.play(volume_source, after=lambda e: self.play_next_song(guild_id))
