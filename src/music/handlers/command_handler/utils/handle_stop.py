async def handle_stop(self, ctx):
        """Handle stop command"""
        guild_id = ctx.guild.id
        voice_client = self.music_cog.voice_manager.get_voice_client(guild_id)
        
        if voice_client and voice_client.is_connected():
            await self.music_cog.player_service.stop(guild_id)
            await ctx.respond("Playback stopped and queue cleared")
        else:
            await ctx.respond("Not currently playing anything")