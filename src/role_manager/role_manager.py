import discord
from discord.ext import commands, bridge
import logging
from discord.ui import Button
import json
import os
from .views import RoleSelectView, AdminRoleView


logger = logging.getLogger('discord')

# Define data directory path
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Path for role configuration storage
ROLE_CONFIG_PATH = os.path.join(DATA_DIR, "role_config.json")
# Path for panel message storage
PANEL_CONFIG_PATH = os.path.join(DATA_DIR, "role_panels.json")


class RoleManager(commands.Cog):
    """Discord cog for role assignment functionality"""
    
    def __init__(self, bot):
        self.bot = bot
        self.assignable_roles = {}  # {role_id: {name: str, emoji: str}}
        self.admin_messages = {}  # {channel_id: message_id}
        self.user_panels = {}  # {guild_id: {channel_id: [message_ids]}}
        self.conversation_states = {}  # {user_id: {channel_id: state_dict}}
        
        # Load saved data
        self.load_roles()
        self.load_panels()
        
        # Schedule restoring panels after bot is fully ready
        bot.loop.create_task(self.restore_panels())

    def load_roles(self):
        """Load role configuration from file"""
        try:
            if os.path.exists(ROLE_CONFIG_PATH):
                with open(ROLE_CONFIG_PATH, 'r', encoding='utf-8') as f:
                    self.assignable_roles = json.load(f)
                    logger.info(f"Loaded {len(self.assignable_roles)} assignable roles from {ROLE_CONFIG_PATH}")
        except Exception as e:
            logger.error(f"Error loading role configuration from {ROLE_CONFIG_PATH}: {e}")
            self.assignable_roles = {}
    
    def load_panels(self):
        """Load panel message IDs from file"""
        try:
            if os.path.exists(PANEL_CONFIG_PATH):
                with open(PANEL_CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.admin_messages = data.get("admin_panels", {})
                    self.user_panels = data.get("user_panels", {})
                    logger.info(f"Loaded panel configurations from {PANEL_CONFIG_PATH}")
        except Exception as e:
            logger.error(f"Error loading panel configuration from {PANEL_CONFIG_PATH}: {e}")
            self.admin_messages = {}
            self.user_panels = {}
    
    def save_roles(self):
        """Save role configuration to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(ROLE_CONFIG_PATH), exist_ok=True)
            
            with open(ROLE_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.assignable_roles, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved role configuration to {ROLE_CONFIG_PATH}")
        except Exception as e:
            logger.error(f"Error saving role configuration to {ROLE_CONFIG_PATH}: {e}")
    
    def save_panels(self):
        """Save panel message IDs to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(PANEL_CONFIG_PATH), exist_ok=True)
            
            data = {
                "admin_panels": self.admin_messages,
                "user_panels": self.user_panels
            }
            with open(PANEL_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved panel configuration to {PANEL_CONFIG_PATH}")
        except Exception as e:
            logger.error(f"Error saving panel configuration to {PANEL_CONFIG_PATH}: {e}")
    
    def add_assignable_role(self, role_id, role_info):
        """Add a role to the assignable roles list"""
        self.assignable_roles[role_id] = role_info
        self.save_roles()
    
    def remove_assignable_role(self, role_id):
        """Remove a role from the assignable roles list"""
        if role_id in self.assignable_roles:
            del self.assignable_roles[role_id]
            self.save_roles()
    
    def add_conversation_state(self, user_id, channel_id, state):
        """Store conversation state for an ongoing admin operation"""
        if user_id not in self.conversation_states:
            self.conversation_states[user_id] = {}
        
        self.conversation_states[user_id][channel_id] = state
    
    def get_conversation_state(self, user_id, channel_id):
        """Get current conversation state for a user in a channel"""
        return self.conversation_states.get(user_id, {}).get(channel_id)
    
    def clear_conversation_state(self, user_id, channel_id):
        """Clear conversation state for completed or abandoned operations"""
        if user_id in self.conversation_states and channel_id in self.conversation_states[user_id]:
            del self.conversation_states[user_id][channel_id]
            
            # Remove user from states if no more active conversations
            if not self.conversation_states[user_id]:
                del self.conversation_states[user_id]
    
    def add_user_panel(self, guild_id, channel_id, message_id):
        """Store a user role panel location"""
        if guild_id not in self.user_panels:
            self.user_panels[guild_id] = {}
            
        if channel_id not in self.user_panels[guild_id]:
            self.user_panels[guild_id][channel_id] = []
            
        if message_id not in self.user_panels[guild_id][channel_id]:
            self.user_panels[guild_id][channel_id].append(message_id)
            self.save_panels()
    
    def add_admin_panel(self, channel_id, message_id):
        """Store an admin panel location"""
        self.admin_messages[channel_id] = message_id
        self.save_panels()
    
    async def restore_panels(self):
        """Restore all saved panels on bot startup"""
        # Wait for bot to be ready
        await self.bot.wait_until_ready()
        logger.info("Restoring role panels...")
        
        # Restore admin panels
        for channel_id, message_id in self.admin_messages.items():
            try:
                channel = self.bot.get_channel(int(channel_id))
                if not channel:
                    continue
                    
                message = await channel.fetch_message(int(message_id))
                if message:
                    await self.update_admin_panel(message)
            except Exception as e:
                logger.error(f"Failed to restore admin panel: {e}")
        
        # Restore user panels
        restored = 0
        for guild_id, channels in self.user_panels.items():
            for channel_id, message_ids in channels.items():
                try:
                    channel = self.bot.get_channel(int(channel_id))
                    if not channel:
                        continue
                        
                    for message_id in message_ids:
                        try:
                            message = await channel.fetch_message(int(message_id))
                            if message:
                                await self.update_user_panel(message)
                                restored += 1
                        except:
                            # Individual message restoration failure shouldn't stop the process
                            pass
                except Exception as e:
                    logger.error(f"Failed to restore user panels in channel {channel_id}: {e}")
        
        logger.info(f"Restored {restored} user role panels")
    
    async def update_all_panels(self):
        """Update all role panels after role changes"""
        # Update admin panels
        for channel_id, message_id in self.admin_messages.items():
            try:
                channel = self.bot.get_channel(int(channel_id))
                if not channel:
                    continue
                    
                message = await channel.fetch_message(int(message_id))
                if message:
                    await self.update_admin_panel(message)
            except Exception as e:
                logger.error(f"Failed to update admin panel: {e}")
        
        # Update user panels
        for guild_id, channels in self.user_panels.items():
            for channel_id, message_ids in channels.items():
                try:
                    channel = self.bot.get_channel(int(channel_id))
                    if not channel:
                        continue
                        
                    for message_id in message_ids:
                        try:
                            message = await channel.fetch_message(int(message_id))
                            if message:
                                await self.update_user_panel(message)
                        except:
                            # Individual message update failure shouldn't stop the process
                            pass
                except Exception as e:
                    logger.error(f"Failed to update user panels in channel {channel_id}: {e}")
    
    async def update_admin_panel(self, message):
        """Update an admin panel message"""
        try:
            view = AdminRoleView(self)
            embed = discord.Embed(
                title="Role Management Panel",
                description="Use this panel to configure self-assignable roles",
                color=discord.Color.green()
            )
            
            # Add list of current roles
            if self.assignable_roles:
                role_list = "\n".join(
                    f"{info.get('emoji', '🏷️')} **{info.get('name', 'Unknown')}**"
                    for info in self.assignable_roles.values()
                )
                embed.add_field(
                    name="Current Assignable Roles",
                    value=role_list,
                    inline=False
                )
            else:
                embed.add_field(
                    name="Current Assignable Roles",
                    value="None configured yet. Use the Add Role button to add roles.",
                    inline=False
                )
            
            await message.edit(embed=embed, view=view)
            return True
        except Exception as e:
            logger.error(f"Error updating admin panel: {e}")
            return False
    
    async def update_user_panel(self, message):
        """Update a user panel message"""
        try:
            view = RoleSelectView(self)
            embed = discord.Embed(
                title="Role Selection",
                description="Click a button below to add or remove a role from yourself",
                color=discord.Color.blue()
            )
            
            # Check if there are any roles added
            if not self.assignable_roles:
                embed.description = "No roles have been configured for self-assignment yet."
                view.clear_items()
                
                # Add a disabled button to indicate no roles
                no_roles_button = Button(
                    style=discord.ButtonStyle.secondary,
                    label="No roles available",
                    disabled=True
                )
                view.add_item(no_roles_button)
            
            await message.edit(embed=embed, view=view)
            return True
        except Exception as e:
            logger.error(f"Error updating user panel: {e}")
            return False
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Process messages for interactive role configuration"""
        # Ignore messages from bots
        if message.author.bot:
            return
            
        # Check if user is in conversation mode
        state = self.get_conversation_state(message.author.id, message.channel.id)
        if not state:
            return
            
        # Handle messages based on conversation state
        if state['state'] == 'waiting_for_role':
            # Try to get the role
            role = None
            role_input = message.content.strip()
            
            # Handle role mentions
            if message.role_mentions:
                role = message.role_mentions[0]
            elif role_input.isdigit():
                role = message.guild.get_role(int(role_input))
            else:
                # Remove @ prefix if present
                if role_input.startswith('@'):
                    role_input = role_input[1:]
                
                # Try case-sensitive exact match first
                role = discord.utils.get(message.guild.roles, name=role_input)
                
                # If not found, try case-insensitive match
                if not role:
                    role = discord.utils.get(
                        message.guild.roles,
                        name=lambda n: n.lower() == role_input.lower()
                    )
            
            # Delete the user's message if possible
            try:
                await message.delete()
            except:
                pass
            
            # Progress conversation based on role lookup result
            if role:
                # Save the role and move to emoji input
                state['role'] = role
                state['state'] = 'waiting_for_emoji'
                self.add_conversation_state(message.author.id, message.channel.id, state)
                
                # Ask for emoji
                await message.channel.send(
                    f"Role **{role.name}** selected. Now please enter an emoji to use for this role button:",
                    delete_after=10
                )
            else:
                # Send error and stay in same state
                await message.channel.send(
                    f"❌ Could not find role with name or ID: {role_input}\n\n"
                    f"Please try again with the exact role name, @mention, or role ID.",
                    delete_after=10
                )
                
        elif state['state'] == 'waiting_for_emoji':
            emoji = message.content.strip()
            
            # Delete the user's message if possible
            try:
                await message.delete()
            except:
                pass
            
            # Process emoji
            if emoji:
                # Add role to database
                role = state['role']
                self.add_assignable_role(
                    str(role.id),
                    {"name": role.name, "emoji": emoji if emoji else "🏷️"}
                )
                
                # Send confirmation
                await message.channel.send(
                    f"✅ Added **{role.name}** to assignable roles with emoji {emoji}",
                    delete_after=10
                )
                
                # Update all panels
                await self.update_all_panels()
            else:
                # Use default emoji
                role = state['role']
                self.add_assignable_role(
                    str(role.id),
                    {"name": role.name, "emoji": "🏷️"}
                )
                
                # Send confirmation
                await message.channel.send(
                    f"✅ Added **{role.name}** to assignable roles with default emoji 🏷️",
                    delete_after=10
                )
                
                # Update all panels
                await self.update_all_panels()
            
            # Clear conversation state
            self.clear_conversation_state(message.author.id, message.channel.id)
    
    @bridge.bridge_command(
        name="role_panel",
        description="Show the role assignment panel for users"
    )
    async def role_panel(self, ctx):
        """Display the user role panel"""
        embed = discord.Embed(
            title="Role Selection",
            description="Click a button below to add or remove a role from yourself",
            color=discord.Color.blue()
        )
        
        # Create user view
        view = RoleSelectView(self)
        
        # Check if there are any roles added
        if not self.assignable_roles:
            embed.description = "No roles have been configured for self-assignment yet."
            view.clear_items()
            
            # Add a disabled button to indicate no roles
            no_roles_button = Button(
                style=discord.ButtonStyle.secondary,
                label="No roles available",
                disabled=True
            )
            view.add_item(no_roles_button)
        
        # Send message and store for updates
        response = await ctx.respond(embed=embed, view=view)
        
        # Get the actual message object
        if hasattr(response, 'message'):
            message = response.message
        else:
            message = response
        
        # Add to tracked panels
        self.add_user_panel(
            str(ctx.guild.id),
            str(ctx.channel.id),
            str(message.id)
        )
    
    @bridge.bridge_command(
        name="role_admin",
        description="Display the role management panel (Admin only)"
    )
    @commands.has_permissions(manage_roles=True)
    async def role_admin(self, ctx):
        """Display the admin role management panel"""
        embed = discord.Embed(
            title="Role Management Panel",
            description="Use this panel to configure self-assignable roles",
            color=discord.Color.green()
        )
        
        # Add list of current roles
        if self.assignable_roles:
            role_list = "\n".join(
                f"{info.get('emoji', '🏷️')} **{info.get('name', 'Unknown')}**"
                for info in self.assignable_roles.values()
            )
            embed.add_field(
                name="Current Assignable Roles",
                value=role_list,
                inline=False
            )
        else:
            embed.add_field(
                name="Current Assignable Roles",
                value="None configured yet. Use the Add Role button to add roles.",
                inline=False
            )
        
        # Create admin view
        view = AdminRoleView(self)
        
        # Send panel
        response = await ctx.respond(embed=embed, view=view)
        
        # Store message for later updates
        if hasattr(response, 'message'):
            message = response.message
        else:
            message = response
        
        # Add to tracked admin panels
        self.add_admin_panel(str(ctx.channel.id), str(message.id))