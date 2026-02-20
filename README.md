# BOT1 (New Updates)
A feature-rich Discord bot built with Python and discord.py, optimized for 24/7 operation on Termux.

## ✨ New Features
- **🍖 Virtual Pet System:** The bot has a life of its own! It gets hungry over time and loses health if not fed.
- **📊 Persistent Stats:** Uses aiosqlite to save health and hunger data, so stats aren't lost when the bot restarts.
- **🔄 Auto-Restart Engine:** Includes a shell script that automatically revives the bot if it crashes or is told to !restart.
- **💬 Enhanced Social Logic:** Prevents "Hi" and "Bye" spam by detecting duplicates and managing permissions.
- **🛠️ Admin Suite:** Advanced !purge, !restart, and !stop commands for trusted users.

## 🛠️ Setup Instructions
**1. Prerequisites (Termux)**
Install the necessary packages on your Android device:
```bash
pkg update && pkg upgrade
pkg install python
pip install discord.py python-dotenv aiosqlite
```
**2. Configuration (.env)**
Create a .env file to store your secrets securely:
```bash
nano .env
```
Paste the following and replace with your actual data:
```txt
DISCORD_TOKEN=YOUR_BOT_TOKEN_HERE
TRUSTED_USERS=YOUR_USER_ID, ANOTHER_USER_ID
```
_**to save any files created by nano, press**_ `ctrl+x`, _**press**_ `Y`, _**press**_ `enter`

**3. Creating the Auto-Restart Script (start.sh)**
This script acts as a "bodyguard" to keep your bot running.
1. Create the file:
```bash
nano start.sh
```
2. Paste this logic:
```bash
#!/bin/bash
while true
do
    echo "Starting Bot..."
    python bot1.py
    status=$?
    if [ $status -eq 0 ]; then
        echo "✅ Bot stopped manually. Goodbye!"
        break
    else
        echo "🔄 Restarting in 3 seconds..."
        sleep 3
    fi
done
```
_**to save any files created by nano, press**_ `ctrl+x`_, **press**_ `Y`_, **press**_ `enter`


3. **Crucial step:** Give Termux permission to run this script:
```bash
chmod +x start.sh
```

## 🚀 Running the Bot
Instead of running the python file directly, use the starter script:
```bash
./start.sh
```

## 🎮 All Commands

Command         -        Description
---------------------------------------------------
!help           -        Shows the custom, categorized help menu.
---------------------------------------------------
!status         -        Displays the bot's current Health and Hunger levels.
---------------------------------------------------
!feed [food]    -        Increases hunger and heals the bot.
---------------------------------------------------
!uptime         -        Shows how long the bot has been online.
---------------------------------------------------
!ping           -        Shows latency
---------------------------------------------------
!purge [amount] -        Deletes message(s)
---------------------------------------------------
!battery        -        Shows the battery status using termux-battery-status command (termux-api) • this command only works when this bot is run by termux app on Android
---------------------------------------------------
!restart        -        Closes the bot and triggers an immediate restart.
---------------------------------------------------
!stop           -        Completely shuts down the bot and the restart loop.
---------------------------------------------------

### To Do
- [ ] Add ghost of bot when it reaches 0 health
- [ ] Make logic for ghost of bot so it would not respond to any commands even if it's online (except revive command)
- [ ] Add revive command
- [x] Add battery command
- [ ] Add XP system
- [x] Remove bot to bot Hi and Bye logic (due to prevent unsatisfaction)
