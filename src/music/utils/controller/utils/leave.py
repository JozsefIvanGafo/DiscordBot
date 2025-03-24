async def leave_vc_callback(self, interaction):
        """Leave the voice channel"""
        await interaction.response.defer(ephemeral=True)
        
        guild_id = interaction.guild.id
        voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
        
        if not voice_client or not voice_client.is_connected():
            await interaction.followup.send("Not connected to a voice channel", ephemeral=True)
            return
        
        # Stop playback
        if voice_client.is_playing():
            voice_client.stop()
        
        # Disconnect
        await voice_client.disconnect()
        
        # Clear data
        self.music_cog.voice_manager.clear_voice_client(guild_id)
        self.music_cog.queue_manager.clear_guild_data(guild_id)
        
        await interaction.followup.send("Left voice channel", ephemeral=True)
        
        # Update controller
        await self.music_cog.update_controller(guild_id)