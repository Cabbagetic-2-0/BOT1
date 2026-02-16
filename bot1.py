import discord
from discord.ext import commands
import asyncio
import time
import os
from dotenv import load_dotenv

# --- List of User IDs allowed to use the !purge command ---
TRUSTED_USERS = [int(i) for i in os.getenv("TRUSTED_USERS").split(",")]

# --- Set up the bot with a prefix (e.g., !) and necessary intents ---
intents = discord.Intents.default()
intents.message_content = True  # Required to read messages for commands
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}. {bot.user.name} is online!')

# --- ping COMMAND ---
@bot.command()
async def ping(ctx):
    # bot.latency is in seconds, so multiply by 1000 for milliseconds
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Latency: {latency}ms')

# --- Hi LOGIC ---
TRIGGER_EMOJI = "⚠️" 


# Memory to track the last message in each channel
# Format: {channel_id: {'content': str, 'author_id': int, 'msg_obj': message_object}}
history = {}

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.strip().lower()
    channel_id = message.channel.id
    current_time = asyncio.get_event_loop().time()

    if content == "hi":
        # --- SCENARIO 2: USER SENDS 2 HI IN A ROW ---
        if channel_id in history and history[channel_id]['author_id'] == message.author.id and history[channel_id]['content'] == "hi":
            await message.add_reaction("⚠️")
            # The bot stays silent here because the user messed up
        
        # --- SCENARIO 1: NORMAL REPLY + SELF-POLICING ---
        else:
            await asyncio.sleep(1) # Your natural delay
            bot_msg = await message.channel.send("Hi")

            # Check: Did the BOT just send 2 Hi's in a row?
            if channel_id in history and history[channel_id]['author_id'] == bot.user.id and history[channel_id]['content'] == "hi":
                
                # The bot realizes it made a double-hi. 
                # It will wait for a reaction OR 2 minutes, then delete.
                async def self_destruct(msg):
                    def check(reaction, user):
                        return str(reaction.emoji) == "⚠️" and user != bot.user and reaction.message.id == msg.id
                    
                    try:
                        # Wait for a human to react OR 2 minutes to pass
                        await bot.wait_for('reaction_add', timeout=120.0, check=check)
                    except asyncio.TimeoutError:
                        pass # 2 minutes up
                    
                    try:
                        await msg.delete()
                    except:
                        pass # Message already gone

                asyncio.create_task(self_destruct(bot_msg))

            # Update history with the BOT'S message
            history[channel_id] = {'content': "hi", 'author_id': bot.user.id}
            return # Skip the user history update below since we just updated with the bot

    # Update history with the USER'S message (if it wasn't a bot reply)
    history[channel_id] = {'content': content, 'author_id': message.author.id}
    
    await bot.process_commands(message)

# --- purge COMMAND ---
@bot.command()
async def purge(ctx, amount: int):
    # SECURITY CHECK:
    # Is the user on the list? OR are they an Admin? OR are they the Server Owner?
    is_admin = ctx.author.guild_permissions.administrator
    is_owner = ctx.author == ctx.guild.owner
    is_trusted = ctx.author.id in TRUSTED_USERS

    if not (is_admin or is_owner or is_trusted):
        return await ctx.send("❌ You don't have permission to use this command!", delete_after=5)

    # SAFETY CAP: Prevents accidental massive deletions (adjust as you like)
    if amount > 50:
        return await ctx.send("⚠️ Whoa! Let's stay under 50 messages at a time to avoid lag.", delete_after=5)

    # THE PURGE:
    # We add 1 to include the "!purge" command message itself
    deleted = await ctx.channel.purge(limit=amount + 1)

    # Send confirmation and delete it after 5 seconds
    await ctx.send(f'✅ Deleted {len(deleted)-1} messages.', delete_after=5)


# --- bot token autofiller and run bot ---
load_dotenv()
bot.run(os.getenv('DISCORD_TOKEN'))

