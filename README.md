# BOT1
DISCORD BOT using Python Programming Language. discord.py is used for it

# Termux Discord Bot

A lightweight Discord bot designed to run on **Termux (Android)**. Features include a secure purge system, latency check, and a "socially aware" Hi-logic.

## Features
* **Purge Command:** Clean up chat history (Restricted to Admins and Trusted Users).
* **Ping Command:** Check the bot's heartbeat latency.
* **Hi-Logic:** * Automatically warns users if they send "Hi" twice in a row.
    * Self-destructs the bot's own "Hi" if it accidentally sends two in a row.
* **Termux Optimized:** Designed to run with low resource usage.

## Setup Instructions

### 1. Prerequisites
On your Android device, install **Termux** (prefer F-Droid version). Run the following commands:
```bash
pkg update && pkg upgrade
pkg install python
pip install discord.py python-dotenv
```

### 2. Configuration (The Secret Step)
To keep the bot secure, you must create a .env file in the same folder as bot.py. Do not upload this file to GitHub!

Create the file:
```bash
nano .env
write this: "DISCORD_TOKEN=YOUR_BOT_TOKEN_HERE
TRUSTED_USERS=YOUR_USER_ID,ANOTHER_USER_ID
"
press CTRL + x
press Y
press enter
```
### 3 Running the bot
```bash
python bot1.py
```
the bot1.py is named according to the main bot1.py file in this repository but if you use different name (e.g. NAME.py, use ```python NAME.py```

# Licence
This project is licensed under [MIT Licence](https://github.com/Cabbagetic-2-0/BOT1/?tab=MIT-1-ov-file#)
