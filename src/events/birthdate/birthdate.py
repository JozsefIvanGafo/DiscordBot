import os
import discord
from discord.ext import commands, bridge, tasks
import logging
from datetime import datetime, timedelta
from ...utils.json_manager import JsonManager
import threading

logger = logging.getLogger('discord')

class BirthDate(commands.Cog):
    def __init__(self, bot):
        self._birthdate = JsonManager("birthdate.json")
        self.bot = bot
        self._lock = threading.Lock()
        self.check_birthdates.start()
    
    def cog_unload(self):
        self.check_birthdates.cancel()

    # Helper function for ping commands
    async def _set_birthdate(self, ctx, date):
        # Check if the date is correct
        # Format: DD-MM-YYYY
        try:
            date_obj = datetime.strptime(date, "%d-%m-%Y")
        except ValueError:
            await ctx.respond("Invalid date format. Please use DD-MM-YYYY.")
            return
        
        with self._lock:
            self._birthdate.set(str(ctx.author.id), date)
        response = f"Birthdate set to {date_obj.strftime('%d-%m-%Y')}"
        await ctx.respond(response)

    async def _get_birthdate(self, ctx):
        with self._lock:
            date = self._birthdate.get(str(ctx.author.id))
        if date is None:
            await ctx.respond("No birthdate set")
            return
        
        response = f"Your birthdate is {date}"
        await ctx.respond(response)

    async def _delete_birthdate(self, ctx):
        with self._lock:
            self._birthdate.delete(str(ctx.author.id))
        response = "Birthdate deleted"
        await ctx.respond(response)

    # Prefix and slash commands
    @bridge.bridge_command(name="set_birthdate", 
                           description="Set your birthdate (format: DD-MM-YYYY)")
    async def birthdate(self, ctx, date):
        """Set your birthdate"""
        await self._set_birthdate(ctx, date)

    @bridge.bridge_command(name="get_birthdate",
                           description="Get your birthdate")
    async def get_birthdate(self, ctx):
        """Get your birthdate"""
        await self._get_birthdate(ctx)

    @bridge.bridge_command(name="delete_birthdate",
                           description="Delete your birthdate")
    async def delete_birthdate(self, ctx):
        """Delete your birthdate"""
        await self._delete_birthdate(ctx)

    @tasks.loop(hours=24)
    async def check_birthdates(self):
        now = datetime.now()
        if now.hour == 11:
            today = now.strftime("%d-%m")
            with self._lock:
                birthdates = self._birthdate.get_all()
            for user_id, date in birthdates.items():
                if date.startswith(today):
                    user = self.bot.get_user(int(user_id))
                    if user:
                        await user.send(f"Feliz cumpleaños!!!! {user.mention}!")


    @check_birthdates.before_loop
    async def before_check_birthdates(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(BirthDate(bot))
