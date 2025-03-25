import discord
from discord.ui import View, Button, Select
from ..utils import get_emoji_from_str
class RoleSelectView(View):
    """View for users to assign/remove roles from themselves"""
    
    def __init__(self, role_manager):
        super().__init__(timeout=None)  # Persistent view
        self.role_manager = role_manager
        self.update_buttons()
    
    def update_buttons(self):
        """Update the buttons based on current role configuration"""
        self.clear_items()
        
        for role_id, role_info in self.role_manager.assignable_roles.items():
            # Process emoji safely
            emoji = role_info.get('emoji')
            processed_emoji = None
            
            if emoji:
                processed_emoji = get_emoji_from_str(emoji)
                
            button = Button(
                style=discord.ButtonStyle.primary,
                label=role_info.get('name', 'Unknown Role'),
                custom_id=f"role_{role_id}",
                emoji=processed_emoji or "🏷️"  # Fallback to default if emoji is invalid
            )
            button.callback = self.role_button_callback
            self.add_item(button)
    
    async def role_button_callback(self, interaction):
        """Handle role button click"""
        role_id = interaction.custom_id.split('_')[1]
        
        # Get the role
        role = interaction.guild.get_role(int(role_id))
        if not role:
            await interaction.response.send_message(
                "Role not found. It may have been deleted.",
                ephemeral=True
            )
            return
        
        # Toggle role on user
        if role in interaction.user.roles:
            # Remove role
            try:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(
                    f"✅ Removed role: **{role.name}**",
                    ephemeral=True
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ I don't have permission to remove that role.",
                    ephemeral=True
                )
        else:
            # Add role
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    f"✅ Added role: **{role.name}**",
                    ephemeral=True
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ I don't have permission to add that role.",
                    ephemeral=True
                )