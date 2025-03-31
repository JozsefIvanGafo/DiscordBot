async def leave_vc_callback(self, interaction):
    guild_id = interaction.guild_id
    
    # Get voice client
    voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
    
    if not voice_client:
        await interaction.response.send_message("I'm not in a voice channel!", ephemeral=True)
        return
    
    # Disconnect
    await voice_client.disconnect()
    
    # Clear data
    self.music_cog.voice_manager.clear_voice_client(guild_id)
    self.music_cog.queue_manager.clear_guild_data(guild_id)
    
    await interaction.response.defer(ephemeral=True)
    
    # Use controller_service for update
    await self.music_cog.controller_service.update_controller(guild_id)
    
    await interaction.followup.send("Left the voice channel!", ephemeral=True)