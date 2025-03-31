import discord
from ...formatter import format_duration, split_text

async def clear_queue_callback(self, interaction):
    guild_id = interaction.guild_id
    
    # Clear the queue
    self.music_cog.queue_manager.clear_queue(guild_id)
    
    await interaction.response.defer(ephemeral=True)
    
    # Use controller_service instead of direct call to update_controller
    await self.music_cog.controller_service.update_controller(self.guild_id)
    
    await interaction.followup.send("Queue cleared!", ephemeral=True)


async def queue_callback(self, interaction):
        """Show the queue"""
        await interaction.response.defer(ephemeral=True)
        
        guild_id = self.guild_id
        queue = self.music_cog.queue_manager.get_queue(guild_id)
        current_song = self.music_cog.queue_manager.get_current_song(guild_id)
        
        if not current_song and not queue:
            await interaction.followup.send("The queue is empty", ephemeral=True)
            return
        
        
        embed = discord.Embed(title="Music Queue", color=discord.Color.purple())
        
        # Add current song
        if current_song:
            duration = format_duration(current_song['duration'])
            embed.add_field(
                name="🎵 Currently Playing",
                value=f"[{current_song['title']}]({current_song['webpage_url']}) ({duration})",
                inline=False
            )
        
        # Add queue
        if queue:
            queue_list = []
            for i, song in enumerate(queue, 1):
                duration = format_duration(song['duration'])
                queue_list.append(f"{i}. [{song['title']}]({song['webpage_url']}) ({duration})")
            
            queue_text = "\n".join(queue_list)
            if len(queue_text) <= 1024:
                embed.add_field(name="📝 Up Next", value=queue_text, inline=False)
            else:
                chunks = split_text(queue_text, 1024)
                for i, chunk in enumerate(chunks):
                    embed.add_field(
                        name=f"📝 Up Next (Part {i+1})" if i > 0 else "📝 Up Next", 
                        value=chunk, 
                        inline=False
                    )
        
        # Add total duration
        total_duration = sum(song['duration'] for song in queue)
        if current_song:
            total_duration += current_song['duration']
        embed.set_footer(
            text=f"Total songs: {len(queue) + (1 if current_song else 0)} | " +
                f"Total duration: {format_duration(total_duration)}"
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)