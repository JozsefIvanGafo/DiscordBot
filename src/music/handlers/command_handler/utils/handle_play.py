async def handle_play(self, ctx, url):
        """Handle play command"""
        guild_id = ctx.guild.id
        
        # Join voice channel first
        voice_client = await self.music_cog.voice_manager.join_voice_channel(ctx)
        if voice_client is None:
            return
        
        # Play the song
        await self.music_cog.player_service.play_song(guild_id, ctx, url)
        
        # Make sure the controller is displayed and updated
        if guild_id not in self.music_cog.controller_service.controller_messages:
            await self.handle_controller(ctx)
        else:
            await self.music_cog.controller_service.update_controller(guild_id)