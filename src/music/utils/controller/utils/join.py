async def join_vc_callback(self, interaction):
        """Join the user's voice channel"""
        await interaction.response.defer(ephemeral=True)
        
        # Check if user is in a voice channel
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("You need to be in a voice channel first!", ephemeral=True)
            return
        
        voice_channel = interaction.user.voice.channel
        guild = interaction.guild
        guild_id = guild.id
        
        # Check if already connected
        voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
        if voice_client and voice_client.is_connected():
            # Already connected, check if in same channel
            if voice_client.channel.id == voice_channel.id:
                await interaction.followup.send(f"Already connected to {voice_channel.name}", ephemeral=True)
                return
            # Otherwise move to the new channel
            await voice_client.move_to(voice_channel)
            #await interaction.followup.send(f"Moved to {voice_channel.name}", ephemeral=True)
        else:
            # Connect to the voice channel
            try:
                voice_client = await voice_channel.connect()
                self.music_cog.voice_manager.set_voice_client(guild_id, voice_client)
                #await interaction.followup.send(f"Joined {voice_channel.name}", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"Error joining voice channel: {str(e)}", ephemeral=True)
                return
                
        # Update controller
        await self.music_cog.controller_service.update_controller(guild_id)