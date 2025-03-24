import logging
import discord

logger = logging.getLogger('discord')

async def handle_queue(self, ctx):
        """Handle queue command"""
        try:
            guild_id = ctx.guild.id
            queue = self.music_cog.queue_manager.get_queue(guild_id)
            current_song = self.music_cog.queue_manager.get_current_song(guild_id)
            
            if not queue and not current_song:
                await ctx.respond("The queue is empty. Use `/play` to add songs.",ephemeral=True)
                return
            
            # Build embed for queue display
            embed = discord.Embed(
                title="🎵 Music Queue",
                color=discord.Color.blue()
            )
            
            # Add current song if playing
            if current_song:
                embed.add_field(
                    name="Now Playing",
                    value=f"[{current_song['title']}]({current_song['webpage_url']})",
                    inline=False
                )
            
            # Add upcoming songs
            if queue:
                queue_text = ""
                for i, song in enumerate(queue[:10]):
                    queue_text += f"{i+1}. [{song['title']}]({song['webpage_url']})\n"
                
                if len(queue) > 10:
                    queue_text += f"\n... and {len(queue) - 10} more songs"
                
                embed.add_field(
                    name="Up Next",
                    value=queue_text,
                    inline=False
                )
            
            await ctx.respond(embed=embed)
            
        except Exception as e:
            logger.error(f"Error displaying queue: {e}", exc_info=True)
            await ctx.respond("⚠️ There was an error displaying the queue.")