import discord
from discord.ext import commands, bridge, tasks
import logging
import json
import os
import time
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
from collections import defaultdict
import asyncio
import matplotlib as mpl

# Use a font that supports Korean characters
try:
    # For Windows
    mpl.rc('font', family='Malgun Gothic')
except:
    try:
        # For Linux/Mac
        mpl.rc('font', family='AppleGothic')
    except:
        # Fallback
        mpl.rc('font', family='DejaVu Sans')

logger = logging.getLogger('discord')

# Define data directory path
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Path for statistics storage
STATS_CONFIG_PATH = os.path.join(DATA_DIR, "statistics.json")
# Path for activity tracking
ACTIVITY_PATH = os.path.join(DATA_DIR, "activity_tracking.json")

class Statistics(commands.Cog):
    """Bot and server statistics tracking system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now()
        
        # Bot statistics
        self.stats = {
            "commands_used": 0,
            "voice_time": 0,  # in seconds
            "messages_processed": 0
        }
        
        # Server activity tracking
        self.activity = {}
        
        # Excluded channels
        self.excluded = {}
        
        # Voice state tracking
        self.voice_sessions = {}
        
        # Load saved data
        self.load_statistics()
        self.load_activity()
        
        # Start background tasks
        self.save_loop.start()
        self.voice_tracker.start()
    
    def cog_unload(self):
        """Handle shutdown"""
        self.save_loop.cancel()
        self.voice_tracker.cancel()
        self.save_statistics()
        self.save_activity()
    
    def load_statistics(self):
        """Load bot statistics from file"""
        try:
            if os.path.exists(STATS_CONFIG_PATH):
                with open(STATS_CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.stats = data.get("bot_stats", self.stats)
                    self.excluded = data.get("excluded_channels", {})
                    logger.info(f"Loaded statistics configuration from {STATS_CONFIG_PATH}")
        except Exception as e:
            logger.error(f"Error loading statistics from {STATS_CONFIG_PATH}: {e}")
    
    def load_activity(self):
        """Load activity tracking data from file"""
        try:
            if os.path.exists(ACTIVITY_PATH):
                with open(ACTIVITY_PATH, 'r', encoding='utf-8') as f:
                    self.activity = json.load(f)
                    logger.info(f"Loaded activity data from {ACTIVITY_PATH}")
        except Exception as e:
            logger.error(f"Error loading activity data from {ACTIVITY_PATH}: {e}")
            self.activity = {}
    
    def save_statistics(self):
        """Save bot statistics to file"""
        try:
            data = {
                "bot_stats": self.stats,
                "excluded_channels": self.excluded
            }
            with open(STATS_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved statistics to {STATS_CONFIG_PATH}")
        except Exception as e:
            logger.error(f"Error saving statistics to {STATS_CONFIG_PATH}: {e}")
    
    def save_activity(self):
        """Save activity tracking data to file"""
        try:
            with open(ACTIVITY_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.activity, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved activity data to {ACTIVITY_PATH}")
        except Exception as e:
            logger.error(f"Error saving activity data to {ACTIVITY_PATH}: {e}")
    
    @tasks.loop(minutes=5)
    async def save_loop(self):
        """Save data periodically"""
        self.save_statistics()
        self.save_activity()
    
    @tasks.loop(seconds=30)
    async def voice_tracker(self):
        """Update voice time for users in voice channels"""
        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            
            # Initialize guild data if not exists
            if guild_id not in self.activity:
                self.activity[guild_id] = {"messages": {}, "voice": {}}
            
            # Get excluded voice channels
            excluded_voice = self.excluded.get(guild_id, {}).get("voice", [])
            
            # Check all voice channels
            for voice_channel in guild.voice_channels:
                if str(voice_channel.id) in excluded_voice:
                    continue
                
                # Update time for each member in voice
                for member in voice_channel.members:
                    # Ignore bot users
                    if member.bot:
                        continue
                    
                    # Only count if not AFK, not muted, and not deafened
                    if not member.voice.afk and not member.voice.self_mute and not member.voice.self_deaf:
                        member_id = str(member.id)
                        
                        # Initialize member voice data if not exists
                        if member_id not in self.activity[guild_id]["voice"]:
                            self.activity[guild_id]["voice"][member_id] = 0
                        
                        # Add 30 seconds (the loop interval)
                        self.activity[guild_id]["voice"][member_id] += 30
    
    @save_loop.before_loop
    @voice_tracker.before_loop
    async def before_loops(self):
        """Wait for bot to be ready before starting loops"""
        await self.bot.wait_until_ready()
    
    def is_channel_excluded(self, guild_id, channel_id, channel_type="messages"):
        """Check if a channel is in the excluded list"""
        guild_id = str(guild_id)
        channel_id = str(channel_id)
        
        if guild_id not in self.excluded:
            return False
        
        if channel_type not in self.excluded[guild_id]:
            return False
        
        return channel_id in self.excluded[guild_id][channel_type]
    
    def add_excluded_channel(self, guild_id, channel_id, channel_type="messages"):
        """Add a channel to the excluded list"""
        guild_id = str(guild_id)
        channel_id = str(channel_id)
        
        if guild_id not in self.excluded:
            self.excluded[guild_id] = {"messages": [], "voice": []}
        
        if channel_type not in self.excluded[guild_id]:
            self.excluded[guild_id][channel_type] = []
        
        if channel_id not in self.excluded[guild_id][channel_type]:
            self.excluded[guild_id][channel_type].append(channel_id)
            self.save_statistics()
            return True
        return False
    
    def remove_excluded_channel(self, guild_id, channel_id, channel_type="messages"):
        """Remove a channel from the excluded list"""
        guild_id = str(guild_id)
        channel_id = str(channel_id)
        
        if (guild_id in self.excluded and 
            channel_type in self.excluded[guild_id] and 
            channel_id in self.excluded[guild_id][channel_type]):
            
            self.excluded[guild_id][channel_type].remove(channel_id)
            self.save_statistics()
            return True
        return False
    
    def get_uptime(self):
        """Get bot uptime as a formatted string"""
        uptime = datetime.now() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 or not parts:
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        
        return ", ".join(parts)
    
    def format_time(self, seconds):
        """Format seconds into a readable time string"""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        elif minutes > 0:
            return f"{int(minutes)}m {int(seconds)}s"
        else:
            return f"{int(seconds)}s"
    
    async def create_leaderboard_image(self, data, title, ylabel):
        """Create a bar chart for the leaderboard"""
        # Sort data by value (descending)
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
        
        # Take top 10 only
        top_data = sorted_data[:10]
        
        if not top_data:
            return None
        
        # Prepare data for plotting
        names = []
        values = []
        
        for user_id, value in top_data:
            try:
                user = await self.bot.fetch_user(int(user_id))
                name = user.display_name
            except:
                name = f"User {user_id}"
            
            names.append(name[:15] + "..." if len(name) > 15 else name)
            values.append(value)
        
        # Create figure
        plt.figure(figsize=(10, 6))
        plt.bar(names, values, color='royalblue')
        plt.title(title)
        plt.xlabel('Users')
        plt.ylabel(ylabel)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save to buffer
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        return buf
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Increment command counter when a command is used"""
        self.stats["commands_used"] += 1
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Track message counts for users"""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Increment processed message counter
        self.stats["messages_processed"] += 1
        
        # Get guild and channel
        if not message.guild:
            return  # Skip DMs
        
        guild_id = str(message.guild.id)
        channel_id = str(message.channel.id)
        
        # Check if channel is excluded
        if self.is_channel_excluded(guild_id, channel_id, "messages"):
            return
        
        # Initialize guild data if not exists
        if guild_id not in self.activity:
            self.activity[guild_id] = {"messages": {}, "voice": {}}
        
        # Initialize user message count if not exists
        user_id = str(message.author.id)
        if user_id not in self.activity[guild_id]["messages"]:
            self.activity[guild_id]["messages"][user_id] = 0
        
        # Increment message count
        self.activity[guild_id]["messages"][user_id] += 1
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Track voice channel activity"""
        # Ignore bot users
        if member.bot:
            return
        
        guild_id = str(member.guild.id)
        user_id = str(member.id)
        
        # Initialize tracking data
        if guild_id not in self.activity:
            self.activity[guild_id] = {"messages": {}, "voice": {}}
        
        if user_id not in self.activity[guild_id]["voice"]:
            self.activity[guild_id]["voice"][user_id] = 0
        
        # User joined a voice channel
        if before.channel is None and after.channel is not None:
            # Check if channel is excluded
            if not self.is_channel_excluded(guild_id, after.channel.id, "voice"):
                self.voice_sessions[(guild_id, user_id)] = time.time()
        
        # User left a voice channel
        elif before.channel is not None and after.channel is None:
            session_key = (guild_id, user_id)
            if session_key in self.voice_sessions:
                # Calculate session duration
                start_time = self.voice_sessions[session_key]
                end_time = time.time()
                duration = end_time - start_time
                
                # Only count if channel wasn't excluded
                if not self.is_channel_excluded(guild_id, before.channel.id, "voice"):
                    # Add to user's voice time
                    self.activity[guild_id]["voice"][user_id] += duration
                    # Add to bot's voice time tracking
                    self.stats["voice_time"] += duration
                
                # Remove session tracking
                del self.voice_sessions[session_key]
        
        # User moved between voice channels
        elif before.channel != after.channel:
            session_key = (guild_id, user_id)
            
            # End old session if not excluded
            if session_key in self.voice_sessions and not self.is_channel_excluded(guild_id, before.channel.id, "voice"):
                start_time = self.voice_sessions[session_key]
                end_time = time.time()
                duration = end_time - start_time
                self.activity[guild_id]["voice"][user_id] += duration
                self.stats["voice_time"] += duration
            
            # Start new session if not excluded
            if not self.is_channel_excluded(guild_id, after.channel.id, "voice"):
                self.voice_sessions[(guild_id, user_id)] = time.time()
            else:
                # Remove session tracking if new channel is excluded
                if session_key in self.voice_sessions:
                    del self.voice_sessions[session_key]
    
    @bridge.bridge_command(name="botstats", description="Show bot statistics")
    async def show_bot_statistics(self, ctx):
        """Display bot statistics"""
        embed = discord.Embed(
            title="Bot Statistics",
            description="Performance and usage statistics",
            color=discord.Color.blue()
        )
        
        # Uptime
        embed.add_field(
            name="Uptime",
            value=self.get_uptime(),
            inline=False
        )
        
        # Command usage
        embed.add_field(
            name="Commands Used",
            value=f"{self.stats['commands_used']} commands",
            inline=True
        )
        
        # Messages processed
        embed.add_field(
            name="Messages Processed",
            value=f"{self.stats['messages_processed']} messages",
            inline=True
        )
        
        # Voice time
        voice_time = self.format_time(self.stats["voice_time"])
        embed.add_field(
            name="Total Voice Time",
            value=voice_time,
            inline=True
        )
        
        # Server count
        embed.add_field(
            name="Servers",
            value=f"{len(self.bot.guilds)} servers",
            inline=True
        )
        
        # User count (approximate)
        user_count = sum(guild.member_count for guild in self.bot.guilds)
        embed.add_field(
            name="Users",
            value=f"~{user_count} users",
            inline=True
        )
        
        await ctx.respond(embed=embed)
    
    @bridge.bridge_command(name="serverstats", description="Show server statistics")
    async def server_statistics(self, ctx):
        """Display server activity statistics"""
        guild_id = str(ctx.guild.id)
        
        # Initialize data if not exists
        if guild_id not in self.activity:
            self.activity[guild_id] = {"messages": {}, "voice": {}}
        
        embed = discord.Embed(
            title=f"{ctx.guild.name} Statistics",
            description="Server activity statistics",
            color=discord.Color.green()
        )
        
        # Calculate totals
        total_messages = sum(self.activity[guild_id]["messages"].values())
        total_voice_seconds = sum(self.activity[guild_id]["voice"].values())
        total_voice_time = self.format_time(total_voice_seconds)
        
        # Add to embed
        embed.add_field(
            name="Total Messages",
            value=f"{total_messages} messages",
            inline=True
        )
        
        embed.add_field(
            name="Total Voice Time",
            value=total_voice_time,
            inline=True
        )
        
        # Add excluded channels info
        excluded_text = self.excluded.get(guild_id, {}).get("messages", [])
        excluded_voice = self.excluded.get(guild_id, {}).get("voice", [])
        
        if excluded_text or excluded_voice:
            exclusion_info = ""
            
            if excluded_text:
                text_channels = [f"<#{channel_id}>" for channel_id in excluded_text]
                exclusion_info += f"**Excluded Text Channels**: {', '.join(text_channels)}\n"
            
            if excluded_voice:
                voice_channels = [f"<#{channel_id}>" for channel_id in excluded_voice]
                exclusion_info += f"**Excluded Voice Channels**: {', '.join(voice_channels)}"
            
            embed.add_field(
                name="Exclusions",
                value=exclusion_info,
                inline=False
            )
        
        await ctx.respond(embed=embed)
    
    @bridge.bridge_command(name="messageleaderboard", description="Show message leaderboard")
    async def message_leaderboard(self, ctx):
        """Display message count leaderboard"""
        guild_id = str(ctx.guild.id)
        
        # Check if there's data
        if guild_id not in self.activity or not self.activity[guild_id]["messages"]:
            await ctx.respond("No message data has been recorded for this server yet.")
            return
        
        # Create leaderboard image
        buffer = await self.create_leaderboard_image(
            self.activity[guild_id]["messages"],
            f"{ctx.guild.name} Message Leaderboard",
            "Number of Messages"
        )
        
        if not buffer:
            await ctx.respond("Not enough data to create a leaderboard.")
            return
        
        # Send image
        file = discord.File(buffer, filename="message_leaderboard.png")
        await ctx.respond(file=file)
    
    @bridge.bridge_command(name="voiceleaderboard", description="Show voice activity leaderboard")
    async def voice_leaderboard(self, ctx):
        """Display voice activity leaderboard"""
        guild_id = str(ctx.guild.id)
        
        # Check if there's data
        if guild_id not in self.activity or not self.activity[guild_id]["voice"]:
            await ctx.respond("No voice activity data has been recorded for this server yet.")
            return
        
        # Convert seconds to hours for better visualization
        voice_hours = {user_id: time / 3600 for user_id, time in self.activity[guild_id]["voice"].items()}
        
        # Create leaderboard image
        buffer = await self.create_leaderboard_image(
            voice_hours,
            f"{ctx.guild.name} Voice Activity Leaderboard",
            "Hours in Voice Channels"
        )
        
        if not buffer:
            await ctx.respond("Not enough data to create a leaderboard.")
            return
        
        # Send image
        file = discord.File(buffer, filename="voice_leaderboard.png")
        await ctx.respond(file=file)
    
    @bridge.bridge_command(
    name="excludechannel", 
    description="Exclude a channel from statistics tracking (e.g. /excludechannel #general messages)")
    @commands.has_permissions(administrator=True)
    async def exclude_channel(self, ctx, channel: discord.abc.GuildChannel, channel_type: str = "messages"):
    
        """Exclude a channel from statistics tracking"""
        if not channel:
            await ctx.respond("⚠️ You must specify a channel. Example: `/excludechannel #general messages` or `/excludechannel 'Voice Chat' voice`", ephemeral=True)
            return
        # Validate channel type
        if channel_type not in ["messages", "voice"]:
            await ctx.respond("Invalid channel type. Must be 'messages' or 'voice'.", ephemeral=True)
            return
        
        # Validate channel type matches actual channel type
        if channel_type == "messages" and not isinstance(channel, discord.TextChannel):
            await ctx.respond("Cannot exclude a non-text channel from message tracking.", ephemeral=True)
            return
        
        if channel_type == "voice" and not isinstance(channel, discord.VoiceChannel):
            await ctx.respond("Cannot exclude a non-voice channel from voice tracking.", ephemeral=True)
            return
        
        # Add to excluded channels
        if self.add_excluded_channel(ctx.guild.id, channel.id, channel_type):
            await ctx.respond(f"Channel {channel.mention} has been excluded from {channel_type} tracking.", ephemeral=True)
        else:
            await ctx.respond(f"Channel {channel.mention} is already excluded from {channel_type} tracking.", ephemeral=True)
    
    @bridge.bridge_command(name="includechannel", description="Include a previously excluded channel in statistics tracking")
    @commands.has_permissions(administrator=True)
    async def include_channel(self, ctx, channel: discord.abc.GuildChannel, channel_type: str = "messages"):
        """Include a previously excluded channel"""
        # Validate channel type
        if channel_type not in ["messages", "voice"]:
            await ctx.respond("Invalid channel type. Must be 'messages' or 'voice'.", ephemeral=True)
            return
        
        # Remove from excluded channels
        if self.remove_excluded_channel(ctx.guild.id, channel.id, channel_type):
            await ctx.respond(f"Channel {channel.mention} has been included in {channel_type} tracking.", ephemeral=True)
        else:
            await ctx.respond(f"Channel {channel.mention} was not excluded from {channel_type} tracking.", ephemeral=True)
    
    @bridge.bridge_command(name="resetstats", description="Reset statistics for this server")
    @commands.has_permissions(administrator=True)
    async def reset_stats(self, ctx, stat_type: str = "all"):
        """Reset statistics for the server"""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.activity:
            await ctx.respond("No statistics have been recorded for this server yet.", ephemeral=True)
            return
        
        if stat_type.lower() == "messages" or stat_type.lower() == "all":
            self.activity[guild_id]["messages"] = {}
        
        if stat_type.lower() == "voice" or stat_type.lower() == "all":
            self.activity[guild_id]["voice"] = {}
        
        # Save changes
        self.save_activity()
        
        await ctx.respond(f"Reset {stat_type} statistics for this server.", ephemeral=True)