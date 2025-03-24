import discord
from discord.ui import Modal, InputText

class AddSongModal(Modal):
    def __init__(self, music_cog, guild_id):
        super().__init__(title="Add Song to Queue")
        self.music_cog = music_cog
        self.guild_id = guild_id
        
        # Add text input for song URL or search term
        self.song_input = InputText(
            label="YouTube URL or Search Term",
            placeholder="Enter a YouTube URL or search term...",
            style=discord.InputTextStyle.short,
            required=True,
            max_length=200
        )
        self.add_item(self.song_input)
    
    async def callback(self, interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Get the URL/search term
        url = self.song_input.value
        
        # Process the song
        try:
            # Join voice channel if not already in one
            voice_client = self.music_cog.voice_manager.get_voice_client(self.guild_id)
            if not voice_client:
                # Add custom handling for joining voice channel
                if not interaction.user.voice or not interaction.user.voice.channel:
                    await interaction.followup.send("You need to be in a voice channel to use this command.", ephemeral=True)
                    return
                    
                voice_channel = interaction.user.voice.channel
                guild = interaction.guild
                
                # Connect to voice channel directly
                try:
                    voice_client = await voice_channel.connect()
                    self.music_cog.voice_manager.set_voice_client(self.guild_id, voice_client)
                except Exception as e:
                    await interaction.followup.send(f"Error connecting to voice channel: {str(e)}", ephemeral=True)
                    return
            
            # Get song info
            from ...youtube import get_song_info
            #type_msg = 'playlist' if is_youtube_playlist(url) else 'video/search'
            #await interaction.followup.send(f"Processing {type_msg}... This may take a moment.", ephemeral=True)
            
            songs_info = await get_song_info(self.music_cog.ytdl, url)
            if not songs_info:
                await interaction.followup.send("No songs found for the provided URL or search query", ephemeral=True)
                return
            
            # Add songs to queue
            self.music_cog.queue_manager.add_multiple_to_queue(self.guild_id, songs_info)
            
            # Notify user
            """if len(songs_info) == 1:
                await interaction.followup.send(f"Added to queue: {songs_info[0]['title']}", ephemeral=True)
            else:
                await interaction.followup.send(f"Added {len(songs_info)} songs to queue", ephemeral=True)
            """
            # Start playing if not already playing
            if not voice_client.is_playing():
                await self.music_cog.player_service.play_next(self.guild_id)
                
            # Update the controller if there's an active one
            await self.music_cog.controller_service.update_controller(self.guild_id)
                
        except ValueError as e:
            await interaction.followup.send(f"Error: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Error processing your request: {str(e)}", ephemeral=True)
