import discord
from discord.ui import View, Button, Select
from .roleselectview import RoleSelectView

class AdminRoleView(View):
    """Admin view for managing assignable roles"""
    
    def __init__(self, role_manager):
        super().__init__(timeout=None)
        self.role_manager = role_manager
        self.update_items()
    
    def update_items(self):
        """Update view items based on current configuration"""
        self.clear_items()
        
        # Add New Role button
        add_button = Button(
            style=discord.ButtonStyle.success,
            label="Add Role",
            custom_id="add_role",
            emoji="➕"
        )
        add_button.callback = self.add_role_callback
        self.add_item(add_button)
        
        # Only add remove select if there are roles to remove
        if self.role_manager.assignable_roles:
            # Role removal dropdown
            options = []
            for role_id, info in self.role_manager.assignable_roles.items():
                # Process emoji safely for the select menu
                emoji = info.get('emoji')
                processed_emoji = None
                
                if emoji and len(emoji) <= 2:  # Only use Unicode emojis in the dropdown
                    processed_emoji = emoji
                
                options.append(discord.SelectOption(
                    label=info.get('name', 'Unknown')[:100],  # Limit to 100 chars
                    value=role_id,
                    emoji=processed_emoji
                ))
                
            remove_select = Select(
                placeholder="Select a role to remove",
                custom_id="remove_role",
                min_values=1,
                max_values=1,
                options=options
            )
            remove_select.callback = self.remove_role_callback
            self.add_item(remove_select)
        
        # Show panel button
        show_button = Button(
            style=discord.ButtonStyle.primary,
            label="Show User Panel",
            custom_id="show_panel",
            emoji="👥"
        )
        show_button.callback = self.show_panel_callback
        self.add_item(show_button)
        
        # Shutdown bot button (second row)
        shutdown_button = Button(
            style=discord.ButtonStyle.danger,
            label="Shutdown Bot",
            custom_id="shutdown_bot",
            emoji="🛑"
        )
        shutdown_button.callback = self.shutdown_bot_callback
        self.add_item(shutdown_button)
    
    async def add_role_callback(self, interaction):
        """Start the conversational flow for adding a role"""
        # Acknowledge the interaction
        await interaction.response.defer(ephemeral=True)
        
        # Send the first prompt message
        prompt_msg = await interaction.followup.send(
            "Please enter the role name or mention the role you want to add:",
            ephemeral=True
        )
        
        # Start waiting for response
        self.role_manager.add_conversation_state(
            interaction.user.id, 
            interaction.channel_id,
            {
                'state': 'waiting_for_role',
                'prompt_msg': prompt_msg.id,
                'admin_message': interaction.message.id,
                'guild_id': interaction.guild.id
            }
        )
    
    async def remove_role_callback(self, interaction):
        """Remove a role from assignable roles"""
        role_id = interaction.data['values'][0]
        role_name = self.role_manager.assignable_roles.get(role_id, {}).get('name', 'Unknown Role')
        
        # Remove role from assignable roles
        self.role_manager.remove_assignable_role(role_id)
        
        await interaction.response.send_message(
            f"✅ Removed **{role_name}** from assignable roles",
            ephemeral=True
        )
        
        # Update all panels
        await self.role_manager.update_all_panels()
    
    async def show_panel_callback(self, interaction):
        """Display the user role panel"""
        embed = discord.Embed(
            title="Role Selection",
            description="Click a button below to add or remove a role from yourself",
            color=discord.Color.blue()
        )
        
        # Create user view
        view = RoleSelectView(self.role_manager)
        
        # Check if there are any roles added
        if not self.role_manager.assignable_roles:
            embed.description = "No roles have been configured for self-assignment yet."
            view.clear_items()
            
            # Add a disabled button to indicate no roles
            no_roles_button = Button(
                style=discord.ButtonStyle.secondary,
                label="No roles available",
                disabled=True
            )
            view.add_item(no_roles_button)
        
        # Send the panel and save its location
        response = await interaction.response.send_message(embed=embed, view=view)
        
        # Store this panel for future updates
        message = await interaction.original_response()
        self.role_manager.add_user_panel(
            str(interaction.guild.id),
            str(interaction.channel_id),
            str(message.id)
        )
    
    async def shutdown_bot_callback(self, interaction):
        """Shutdown the bot - requires administrator permission"""
        # Check if user has administrator permission
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You need Administrator permission to shutdown the bot!",
                ephemeral=True
            )
            return
        
        # Confirm and shutdown
        await interaction.response.send_message(
            "🛑 Shutting down bot...",
            ephemeral=True
        )
        
        import logging
        import sys
        import asyncio
        
        logger = logging.getLogger('discord')
        logger.info(f"Bot shutdown initiated by {interaction.user} (ID: {interaction.user.id})")
        
        # Schedule shutdown
        async def do_shutdown():
            await asyncio.sleep(1)
            
            # Close all voice clients
            for voice_client in self.role_manager.bot.voice_clients:
                try:
                    await voice_client.disconnect(force=True)
                except:
                    pass
            
            await self.role_manager.bot.close()
            await asyncio.sleep(1)
            
            sys.exit(0)
        
        asyncio.create_task(do_shutdown())