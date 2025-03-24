import discord
def get_volume_percentage(self):
        """Get current volume as percentage, rounded to the nearest 10%"""
        voice_client = self.music_cog.voice_manager.get_voice_client(self.guild_id)
        if not voice_client or not hasattr(voice_client.source, 'volume'):
            return 100  # Default volume
        # Round to nearest 10%
        return round(voice_client.source.volume * 100 / 10) * 10

async def volume_down_callback(self, interaction):
        """Decrease volume by 10%"""
        await interaction.response.defer(ephemeral=True)
        voice_client = self.music_cog.voice_manager.get_voice_client(self.guild_id)
        
        if not voice_client or not voice_client.is_connected():
            await interaction.followup.send("Not currently playing anything", ephemeral=True)
            return
            
        # Check if source has volume control
        if not hasattr(voice_client.source, 'volume'):
            # Add volume control to the source
            voice_client.source = discord.PCMVolumeTransformer(voice_client.source)
            voice_client.source.volume = 1.0  # Default volume
        
        # Calculate current percentage and decrease by exactly 10%
        current_percent = round(voice_client.source.volume * 100 / 10) * 10
        new_percent = max(0, current_percent - 10)
        voice_client.source.volume = new_percent / 100
        
        await self.music_cog.controller_service.update_controller(self.guild_id)  # Update controller to show new volume

async def volume_up_callback(self, interaction):
        """Increase volume by 10%"""
        await interaction.response.defer(ephemeral=True)
        voice_client = self.music_cog.voice_manager.get_voice_client(self.guild_id)
        
        if not voice_client or not voice_client.is_connected() or not voice_client.source:
            await interaction.followup.send("Not currently playing anything", ephemeral=True)
            return
        
        # Check if source has volume control
        if not hasattr(voice_client.source, 'volume'):
            # If it doesn't, convert it to a PCMVolumeTransformer
            try:
                # Create a new PCMVolumeTransformer with the original source
                original_source = voice_client.source
                voice_client.source = discord.PCMVolumeTransformer(original_source, volume=1.0)
            except Exception as e:
                # If conversion fails, inform the user
                await interaction.followup.send(f"Cannot adjust volume: {str(e)}", ephemeral=True)
                return
        
        # Now safely calculate percentage and increase volume
        try:
            current_percent = round(voice_client.source.volume * 100 / 10) * 10
            new_percent = min(200, current_percent + 10)
            voice_client.source.volume = new_percent / 100
            
            await self.music_cog.controller_service.update_controller(self.guild_id)  # Update controller to show new volume
        except Exception as e:
            await interaction.followup.send(f"Error adjusting volume: {str(e)}", ephemeral=True)