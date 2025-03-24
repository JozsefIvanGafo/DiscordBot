async def skip_callback(self, interaction):
        """Skip the current song"""
        await interaction.response.defer(ephemeral=True)
        voice_client = self.music_cog.voice_manager.get_voice_client(self.guild_id)
        
        if voice_client and voice_client.is_connected() and voice_client.is_playing():
            voice_client.stop()  # This will trigger play_next
            await interaction.followup.send("Skipped current song", ephemeral=True)
        else:
            await interaction.followup.send("Not playing anything", ephemeral=True)