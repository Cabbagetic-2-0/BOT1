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
TRUSTED_USERS = [int(i) for i in os.getenv("TRUSTED_USERS", "").split(",") if i]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Memory and Settings
history = {}
TRIGGER_EMOJI = "⚠️"

@bot.event
async def on_ready():
    # Set a nice status for the bot
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="for 'Hi' | !ping"
    ))
    print(f'✅ Logged in as {bot.user.name}. Ready for action!')

# 2. THE HI LOGIC (Merged & Cleaned)
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Clean the message and split it into words
    words = message.content.strip().lower().split()
    channel_id = message.channel.id

    # Check if "hi" is anywhere in the sentence
    if "hi" in words:
        # SCENARIO 2: USER SENDS 2 HI IN A ROW
        if (channel_id in history and
            history[channel_id]['author_id'] == message.author.id and
            history[channel_id]['content'] == "hi"):
            await message.add_reaction(TRIGGER_EMOJI)

        # SCENARIO 1: NORMAL REPLY + SELF-POLICING
        else:
            await asyncio.sleep(1)
            bot_msg = await message.channel.send("Hi")

            # Check if BOT just did 2 in a row
            if (channel_id in history and
                history[channel_id]['author_id'] == bot.user.id and
                history[channel_id]['content'] == "hi"):

                async def self_destruct(msg):
                    def check(reaction, user):
                        return (str(reaction.emoji) == TRIGGER_EMOJI and
                                user != bot.user and
                                reaction.message.id == msg.id)
                    try:
                        await bot.wait_for('reaction_add', timeout=120.0, check=check)
                    except asyncio.TimeoutError:
                        pass
                    try:
                        await msg.delete()
                    except:
                        pass
                asyncio.create_task(self_destruct(bot_msg))

            # Store that a 'hi' happened in history
            history[channel_id] = {'content': "hi", 'author_id': bot.user.id}
            # Still process commands in case the message was "hi !ping"
            await bot.process_commands(message)
            return

    # Update history for non-'hi' messages
    history[channel_id] = {'content': " ".join(words) if words else "", 'author_id': message.author.id}
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
        return await ctx.send("❌ You don't have permission!", delete_after=5)

    if amount > 50:
        return await ctx.send("⚠️ Limit is 50 per purge.", delete_after=5)

    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'✅ Deleted {len(deleted)-1} messages.', delete_after=5)

# 4. RUN
bot.run(os.getenv('DISCORD_TOKEN'))
