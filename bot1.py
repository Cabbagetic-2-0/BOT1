import aiosqlite
import asyncio
import discord
import os
import subprocess
import sys
import time
from datetime import timedelta
from discord.ext import commands, tasks
from dotenv import load_dotenv

# 1. SETUP & STARTUP
load_dotenv()
# Record the exact time the script starts
start_time = time.time()
# recognising trusted users from the .env file
TRUSTED_USERS = [int(i) for i in os.getenv("TRUSTED_USERS", "").split(",") if i]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

async def update_bot_status(hunger_level):
    """A helper function to change the bot's status based on hunger."""
    if hunger_level > 80:
        status_text = "Happy & Full! | !ping"
        activity_type = discord.ActivityType.playing
    elif hunger_level < 20:
        status_text = "Starving... | !feed 🍕"
        activity_type = discord.ActivityType.playing
    else:
        status_text = "for 'Hi' | !ping"
        activity_type = discord.ActivityType.watching

    await bot.change_presence(activity=discord.Activity(type=activity_type, name=status_text))

@bot.event
async def on_ready():
    # 1. Initialize the Database
    await init_db()

    # 2. Start the background hunger timer
    if not hunger_decay.is_running():
        hunger_decay.start()

    # 3. Set the initial status
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="for 'Hi' | !ping"
    ))

    print(f'✅ Logged in as {bot.user.name}. Everything is loaded  and ready for action!')

    # 4. Set status immediately based on current database stats
    async with aiosqlite.connect("bot_stats.db") as db:
        cursor = await db.execute("SELECT hunger FROM bot_stats WHERE id = 1")
        row = await cursor.fetchone()
        if row:
            await update_bot_status(row[0])


# How fast the bot gets hungry (in seconds)
HUNGER_DECAY_INTERVAL = 600

# --- Database Setup ---
async def init_db():
    async with aiosqlite.connect("bot_stats.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bot_stats (
                id INTEGER PRIMARY KEY,
                health INTEGER DEFAULT 100,
                hunger INTEGER DEFAULT 100
            )
        """)
        # Initialize stats if they don't exist
        cursor = await db.execute("SELECT count(*) FROM bot_stats")
        count = await cursor.fetchone()
        if count[0] == 0:
            await db.execute("INSERT INTO bot_stats (id, health, hunger) VALUES (1, 100, 100)")
        await db.commit()

# --- Background Task: Decay Hunger/Health ---
@tasks.loop(seconds=HUNGER_DECAY_INTERVAL)
async def hunger_decay():
    async with aiosqlite.connect("bot_stats.db") as db:
        # Reduce hunger
        await db.execute("UPDATE bot_stats SET hunger = MAX(0, hunger - 10) WHERE id = 1")

        # Get the new hunger to update the status
        cursor = await db.execute("SELECT hunger, health FROM bot_stats WHERE id = 1")
        row = await cursor.fetchone()
        new_hunger = row[0]

        # If hungry, take damage
        if new_hunger < 20:
            await db.execute("UPDATE bot_stats SET health = MAX(0, health - 5) WHERE id = 1")

        await db.commit()

    # Automatically update the status based on the new hunger level!
    await update_bot_status(new_hunger)


# 2. THE HI & BYE LOGIC (Merged & Cleaned)
# Track the last message content for each channel to prevent "In a row" duplicates
last_message_content = {}
last_author_id = {}

@bot.event
async def on_message(message):
    # Rule 1: Always ignore yourself
    if message.author == bot.user:
        return

    content = message.content.strip().lower()
    words = content.split()
    channel_id = message.channel.id
    author_id = message.author.id

    # --- Greeting Logic ---
    target_words = ["hi", "bye"]
    found_word = next((w for w in target_words if w in words), None)

    if found_word:
        # NEW RULE: If the author is a bot, don't reply!
        # This stops BotA, BotB, and BotC from triggering each other.
        if message.author.bot:
            return

        # Check for human duplicates (same person saying Hi twice)
        if (last_message_content.get(channel_id) == found_word and
            last_author_id.get(channel_id) == author_id):
            try:
                await message.delete()
            except discord.Forbidden:
                pass
            return

        # Send response (This will now ONLY be to humans)
        await message.channel.send(found_word.capitalize())

        # Update trackers
        last_message_content[channel_id] = found_word
        last_author_id[channel_id] = author_id

    else:
        if not (content.startswith(':!') or content.startswith('!')):
            last_message_content[channel_id] = None
            last_author_id[channel_id] = None

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
    uptime_str = str(timedelta(seconds=uptime_seconds))

    await ctx.send(f"🕒 **Uptime:** {uptime_str}")

@bot.command()
async def purge(ctx, amount: int):
    is_admin = ctx.author.guild_permissions.administrator
    is_owner = ctx.author == ctx.guild.owner
    is_trusted = ctx.author.id in TRUSTED_USERS

    if not (is_admin or is_owner or is_trusted):
        return await ctx.send("❌ You don't have permission!", delete_after=5)

    if amount > 50:
        return await ctx.send("⚠️ Limit is 50 per purge.", delete_after=5)

    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'✅ Deleted {len(deleted)-1} messages.', delete_after=5)

@bot.command()
async def status(ctx):
    """Checks the bot's current health and hunger."""
    async with aiosqlite.connect("bot_stats.db") as db:
        cursor = await db.execute("SELECT health, hunger FROM bot_stats WHERE id = 1")
        stats = await cursor.fetchone()

    h = "❤️" if stats[0] > 50 else "💔"
    f = "🍖" if stats[1] > 50 else "🦴"

    embed = discord.Embed(title="Bot Status", color=discord.Color.green())
    embed.add_field(name=f"{h} Health", value=f"{stats[0]}/100")
    embed.add_field(name=f"{f} Hunger", value=f"{stats[1]}/100")
    await ctx.send(embed=embed)

@bot.command()
async def feed(ctx, item: str):
    """Feed the bot to increase hunger and heal it."""
    async with aiosqlite.connect("bot_stats.db") as db:
        cursor = await db.execute("SELECT health, hunger FROM bot_stats WHERE id = 1")
        stats = await cursor.fetchone()

        # Simple logic: food increases hunger, high hunger heals
        new_hunger = min(100, stats[1] + 20)
        new_health = stats[0]
        if stats[1] > 80: # If already full, heal a little
            new_health = min(100, stats[0] + 5)

        await db.execute("UPDATE bot_stats SET health = ?, hunger = ? WHERE id = 1", (new_health, new_hunger))
        await db.commit()


    # Calculate the new hunger... (e.g., new_hunger = bot_stats["hunger"])
    await update_bot_status(new_hunger)
    await ctx.send(f"You fed the bot a {item}! It feels much better :D")


@bot.command()
async def restart(ctx):
    if ctx.author.id not in TRUSTED_USERS:
        return await ctx.send("❌ Only admins can restart the bot.")

    await ctx.send("🔄 Restarting... See you in 3 seconds!")
    await bot.close() # This stops the Python script
    # Exit with code 1 to trigger the bash script's loop
    os._exit(1)


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🤖 Bot Command Menu",
        description="Here is everything I can do!",
        color=discord.Color.blue()
    )

    # Category 1: Social
    embed.add_field(
        name="💬 Social",
        value="• Say **Hi** or **Bye** (I'll respond!)\n• I delete duplicate greetings.",
        inline=False
    )

    # Category 2: Pet System
    embed.add_field(
        name="🍖 Pet System",
        value="• `!status`: Check my health/hunger.\n• `!feed <food>`: Give me a snack!",
        inline=False
    )

    # Category 3: Utility
    embed.add_field(
        name="🛠️ Utility",
        value="• `!ping`: Check my speed(latency).\n• `!uptime`: See how long I've been awake.\n• `!battery`: Shows current battery status of the host device.\n• `!purge <num>`: Clear messages (Admin only).\n• `!restart`: Restart me (Admin only).\n• `!stop`: Shutdown me (Admin only).",
        inline=False
    )

    embed.set_footer(text="Requested by " + ctx.author.name)
    await ctx.send(embed=embed)


@bot.command()
async def stop(ctx):
    if ctx.author.id not in TRUSTED_USERS:
        return await ctx.send("❌ Only admins can restart the bot.")

    await ctx.send("📴 Shutdown Complete. See you later.")
    await bot.close()
    # Exit with code 0 to tell the bash script to "break" the loop
    os._exit(0)


@bot.command()
async def battery(ctx):
    try:
        # Full Termux path (since you're using proot-distro)
        result = subprocess.check_output(
            ["/data/data/com.termux/files/usr/bin/termux-battery-status"]
        )

        output = result.decode("utf-8")

        # Send full raw output inside a code block
        await ctx.send(f"```json\n{output}\n```")

    except Exception as e:
        await ctx.send("❌ Failed to read battery info.")
        print("Battery command error:", e)


# 4. RUN
bot.run(os.getenv('DISCORD_TOKEN'))
