import discord
from discord.ext import commands
import asyncio
import time
import os
from dotenv import load_dotenv

# 1. SETUP
load_dotenv()
# Record the exact time the script starts
start_time = time.time()
# recognising trusted users from the .env file
TRUSTED_USERS = [int(i) for i in os.getenv("TRUSTED_USERS", "").split(",") i>

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    # Set a nice status for the bot
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="for 'Hi' | !ping"
    ))
    print(f'✅ Logged in as {bot.user.name}. Ready for action!')

# 2. THE HI LOGIC (Merged & Cleaned)
# Track the last message content for each channel to prevent "In a row" dupl>
last_message_content = {}
last_author_id = {}

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.strip().lower()
    words = content.split()
    channel_id = message.channel.id
    author_id = message.author.id  # Get the ID of the person who just typed

    if "hi" in words:
        # NEW RULE: Only delete if the content is "hi" AND it's the same per>
        if (last_message_content.get(channel_id) == "hi" and
            last_author_id.get(channel_id) == author_id):
            try:
                await message.delete()
            except discord.Forbidden:
                print("Missing 'Manage Messages' permission.")
            return

        # Greeting logic
        if message.author.bot:
            await message.channel.send("👋")
        else:
            await message.channel.send("Hi")

        # Update trackers for this channel
        last_message_content[channel_id] = "hi"
        last_author_id[channel_id] = author_id

    else:
        # Reset trackers if they say anything other than "hi"
        last_message_content[channel_id] = content
        last_author_id[channel_id] = author_id

    await bot.process_commands(message)

# 3. COMMANDS
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Latency: {latency}ms')

@bot.command()
async def uptime(ctx):
    # Calculate total seconds passed
    current_time = time.time()
    uptime_seconds = int(round(current_time - start_time))

    # Convert seconds into a readable format (Hours, Minutes, Seconds)
    # Using timedelta is the easiest way to format this
    from datetime import timedelta
    uptime_str = str(timedelta(seconds=uptime_seconds))

    await ctx.send(f"🕒 **Uptime:** {uptime_str}")


@bot.command()
async def purge(ctx, amount: int):
    is_admin = ctx.author.guild_permissions.administrator
    is_owner = ctx.author == ctx.guild.owner
    is_trusted = ctx.author.id in TRUSTED_USERS

    if not (is_admin or is_owner or is_trusted):
        return await ctx.send("❌ You don't have permission!", delete_after=>

    if amount > 50:
        return await ctx.send("⚠️ Limit is 50 per purge.", delete_after=5)

    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'✅ Deleted {len(deleted)-1} messages.', delete_after=5)

# 4. RUN
bot.run(os.getenv('DISCORD_TOKEN'))
