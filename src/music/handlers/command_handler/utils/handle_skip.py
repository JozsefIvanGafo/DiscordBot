async def handle_skip(self, ctx):
        """Handle skip command"""
        guild_id = ctx.guild.id
        voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
        
        if voice_client and voice_client.is_connected() and voice_client.is_playing():
            voice_client.stop()  # This will trigger play_next via the after callback
            await ctx.respond("Skipped current song")
        else:
            await ctx.respond("Not currently playing anything")