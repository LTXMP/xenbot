🤖 Xenfigs custom bot







A fully featured Moderation and ticket bot built with discord.py, designed for moderation, giveaways, automation, and ticket support — all replying with clean Discord embeds.

Built to run 24/7 on Render.com with easy configuration and no external dependencies.

🌟 Features
Category	Highlights
🛡️ Moderation	Warn, mute, unmute, clear warnings, channel lock, link protection
🎫 Tickets	Dropdown ticket system, 10 product options, automatic HTML transcripts (sent to DM + log)
🎉 Giveaways	Persistent giveaways (survive restarts), auto cleanup, reroll, and end early
🔔 Auto Messages	Welcome and farewell embeds
🪵 Logging	Centralized log channel for moderation, joins/leaves, tickets, and giveaways
🔐 Role Permissions	Command-based role access system
💬 Utilities	Custom embeds, ping command, global help/cmds menu
🖼️ Embeds	Every command response is a styled embed (no plain text)
🗂️ Folder Structure
mee6_clone_bot/
├─ .env
├─ requirements.txt
├─ main.py
├─ keep_alive.py
├─ data/
│  ├─ config.json
│  ├─ warnings.json
│  ├─ mutes.json
│  ├─ permissions.json
│  ├─ link_protection.json
│  ├─ giveaways.json
│  └─ giveaways_config.json
└─ cogs/
   ├─ utils_embeds.py
   ├─ logging.py
   ├─ automessages.py
   ├─ permissions.py
   ├─ moderation.py
   ├─ tickets.py
   ├─ giveaways.py
   ├─ embeds.py
   ├─ utilities.py
   └─ help.py

⚙️ Setup
1️⃣ Prerequisites

Python 3.10+

Discord Developer Portal
 bot token

Render.com
 account (optional, for hosting)

2️⃣ Clone or Download
git clone https://github.com/LTXMP/mee6-clone-bot.git
cd mee6-clone-bot

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Add Environment Variable

Create a .env file in your root folder:

DISCORD_TOKEN=### 🔧 CHANGE THIS: <YOUR_DISCORD_BOT_TOKEN>


On Render, you can set this in the Environment Variables section instead.

5️⃣ Run the Bot
python main.py


You should see:

✅ Logged in as MEE6 Clone (1234567890)
✅ Slash commands synced

🧩 Key Commands Overview
🛡️ Moderation
Command	Description
/warn [user] [reason]	Warn a user
/warnings [user]	Show warnings
/clearwarnings [user]	Clear warnings
/mute [user] [time] [reason]	Mute for 10m / 1h / 1d
/unmute [user]	Unmute user
/lock	Lock current channel (read-only)
/linkprotection	Toggle link blocking in this channel
🎫 Tickets
Command	Description
/ticketpanel	Send ticket dropdown panel
🛠️ Dropdown Options: Support or Buy → choose product	
🧾 Features: Private channels, HTML transcripts (DM + log), unmoderated tickets	
🎉 Giveaways
Command	Description
/giveaway	Start giveaway (channel, prize, time, winners)
/giveawaylist	List active giveaways
/giveawayinfo [id]	Show giveaway info
/giveawayend [id]	End early
/reroll [id]	Reroll winner
/setgiveawaypurge [days]	Auto-delete old giveaways
🔔 Setup
Command	Description
/setlog [channel]	Set log channel
/setwelcome [channel]	Set welcome channel
/setfarewell [channel]	Set farewell channel
🔐 Role Permissions
Command	Description
/setroleperm [command] [role]	Give role access to command
/removeroleperm [command] [role]	Remove access
/listperms	Show permissions
💬 Utilities
Command	Description
/embed [title] [description] [color]	Send a custom embed
/ping	Show bot latency
/help	Show help menu
/cmds	Same as /help
🪵 Logging System

All moderation, ticket, and giveaway events are automatically logged to your /setlog channel, including:

User warns, mutes, unmutes

Ticket creation and closure

Giveaway start and end

Member joins and leaves

🎨 Global Embed System

Every command — from /warn to /ping — responds with a clean, styled embed.
Colors are consistent across all categories:

Type	Color
Success	🟢 Green
Info	🔵 Blurple
Warning	🟠 Orange
Error	🔴 Red
☁️ Render Deployment (Free 24/7 Hosting)

Push your code to GitHub.

Log in to Render.com
 → New Web Service.

Connect your GitHub repo.

Under settings:

Build Command:
pip install -r requirements.txt

Start Command:
python main.py

Environment Variable:
DISCORD_TOKEN = <YOUR_DISCORD_BOT_TOKEN>

Deploy 🎉

Render automatically restarts your bot if it ever stops.

💡 Customization
File	Change
automessages.py	Update <YOUR_SERVER_NAME> for welcome messages
moderation.py	Set <STAFF_ROLE_NAME> and <ADMIN_ROLE_NAME>
tickets.py	Set <STAFF_ROLE_NAME>, <TICKETS_CATEGORY_NAME>, and your 10 products
config.json	Will auto-fill when using /setlog, /setwelcome, etc.
🧾 License

MIT License © 2025 — You are free to use, modify, and distribute this bot.
If you add new features, consider sharing them with the community ❤️

👨‍💻 Author

Developed by Xen
Built with ❤️ using discord.py
