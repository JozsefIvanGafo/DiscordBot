import discord
from discord.ext import commands, bridge
import logging
import threading
from ..events.birthdate.json_manager import JsonManager 


logger = logging.getLogger('discord')

class AuditLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._audit_log = JsonManager("audit_log.json")  # For storing audit log channel IDs
        self._lock = threading.Lock()
        
    async def _set_audit_log_channel(self, ctx, channel):
        """Helper function to set the audit log channel"""
        if not isinstance(channel, discord.TextChannel):
            await ctx.respond("Please specify a valid text channel.")
            return
            
        # Check if this is already the audit log channel
        with self._lock:
            current_channel_id = self._audit_log.get(str(ctx.guild.id))
            is_current_channel = current_channel_id and int(current_channel_id) == channel.id
            
            # Save the channel ID for this guild
            self._audit_log.set(str(ctx.guild.id), channel.id)
        
        if is_current_channel:
            response = f"{channel.mention} is already set as the audit log channel"
        else:
            response = f"Audit log channel set to {channel.mention}"
        
        await ctx.respond(response)
    
    
    @bridge.bridge_command(
        name="set_audit_log",
        description="Set the channel for audit logs"
    )
    @commands.has_permissions(administrator=True)
    async def set_audit_log(self, ctx, channel: discord.TextChannel = None):
        """Set the channel for audit logs"""
        # If no channel provided, use the current channel
        if channel is None:
            channel = ctx.channel
        await self._set_audit_log_channel(ctx, channel)
    # Event listeners for guild changes
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Called when a guild channel is created"""
        await self._log_channel_event(channel.guild, "Channel Created", f"Channel {channel.mention} ({channel.name}) was created")
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Called when a guild channel is deleted"""
        await self._log_channel_event(channel.guild, "Channel Deleted", f"Channel #{channel.name} was deleted")
    
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        """Called when a guild channel is updated"""
        changes = []
        if before.name != after.name:
            changes.append(f"Name: {before.name} → {after.name}")
        if before.position != after.position:
            changes.append(f"Position: {before.position} → {after.position}")
        if isinstance(before, discord.TextChannel) and isinstance(after, discord.TextChannel):
            if before.topic != after.topic:
                changes.append(f"Topic changed")
            if before.nsfw != after.nsfw:
                changes.append(f"NSFW: {before.nsfw} → {after.nsfw}")
            if before.slowmode_delay != after.slowmode_delay:
                changes.append(f"Slowmode: {before.slowmode_delay}s → {after.slowmode_delay}s")
                
        if changes:
            await self._log_channel_event(after.guild, "Channel Updated", f"Channel {after.mention} was updated:\n• " + "\n• ".join(changes))
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        """Called when a guild role is created"""
        await self._log_role_event(role.guild, "Role Created", f"Role {role.mention} ({role.name}) was created")
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """Called when a guild role is deleted"""
        await self._log_role_event(role.guild, "Role Deleted", f"Role **{role.name}** was deleted")
    
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        """Called when a guild role is updated"""
        changes = []
        if before.name != after.name:
            changes.append(f"Name: {before.name} → {after.name}")
        if before.color != after.color:
            changes.append(f"Color: {before.color} → {after.color}")
        if before.hoist != after.hoist:
            changes.append(f"Displayed separately: {before.hoist} → {after.hoist}")
        if before.mentionable != after.mentionable:
            changes.append(f"Mentionable: {before.mentionable} → {after.mentionable}")
        if before.permissions != after.permissions:
            changes.append(f"Permissions updated")
        
        if changes:
            await self._log_role_event(after.guild, "Role Updated", f"Role {after.mention} was updated:\n• " + "\n• ".join(changes))
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Called when a member is banned"""
        await self._log_moderation_event(guild, "Member Banned", f"User **{user}** was banned from the server")
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        """Called when a member is unbanned"""
        await self._log_moderation_event(guild, "Member Unbanned", f"User **{user}** was unbanned from the server")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Called when a member is updated"""
        if before.roles != after.roles:
            # Find added and removed roles
            added_roles = [role for role in after.roles if role not in before.roles]
            removed_roles = [role for role in before.roles if role not in after.roles]
            
            changes = []
            if added_roles:
                changes.append(f"Added roles: {', '.join(role.mention for role in added_roles)}")
            if removed_roles:
                changes.append(f"Removed roles: {', '.join(role.name for role in removed_roles)}")
                
            if changes:
                await self._log_moderation_event(after.guild, "Member Roles Updated", 
                                               f"Member {after.mention} ({after.name}) had roles changed:\n• " + "\n• ".join(changes))
    
    async def _log_channel_event(self, guild, title, description):
        """Helper method to log channel events"""
        await self._send_audit_log(guild, title, description, discord.Color.blue())
    
    async def _log_role_event(self, guild, title, description):
        """Helper method to log role events"""
        await self._send_audit_log(guild, title, description, discord.Color.gold())
    
    async def _log_moderation_event(self, guild, title, description):
        """Helper method to log moderation events"""
        await self._send_audit_log(guild, title, description, discord.Color.red())
    
    async def _send_audit_log(self, guild, title, description, color):
        """Send an audit log message to the configured channel"""
        with self._lock:
            channel_id = self._audit_log.get(str(guild.id))
        
        if not channel_id:
            return  # No audit log channel configured for this guild
        
        channel = guild.get_channel(int(channel_id))
        if not channel:
            logger.warning(f"Audit log channel {channel_id} not found in guild {guild.id}")
            return
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=f"Server: {guild.name}")
        
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning(f"Missing permissions to send audit logs to channel {channel.id} in guild {guild.id}")
        except Exception as e:
            logger.error(f"Error sending audit log: {str(e)}")

def setup(bot):
    bot.add_cog(AuditLog(bot))