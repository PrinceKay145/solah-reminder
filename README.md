# Solah Reminder Bot 🤖🕌

A smart Telegram bot that provides personalized prayer times based on your location and reminds you when it's time for the next prayer.

## Features ✨

- **Personalized Prayer Times**: Get accurate prayer times for your specific location
- **Location-Based**: Share your location once, get localized times forever
- **Timezone Aware**: Handles timezone differences automatically
- **Next Prayer Alerts**: See exactly when the next prayer is and how long until then
- **Daily Schedule**: View complete prayer timetable for any day
- **Smart Defaults**: Works out of the box with Moscow timezone as fallback

## Commands 📋

- `/start` - Welcome message and setup instructions
- `/next` - Show the next upcoming prayer time with countdown
- `/today` - Display today's complete prayer schedule
- `/setlocation` - Instructions for sharing your location
- `/hello` - Get a friendly greeting

## Setup 🛠️

### Prerequisites

- Python 3.9+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Local Development

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/solah-reminder.git
   cd solah-reminder
   ```

2. **Create and activate virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup:**
   Create a `.env` file:

   ```env
   TOKEN=your_telegram_bot_token_here
   ```

5. **Run locally:**
   ```bash
   python bot.py
   ```
   The bot will run in polling mode for local testing.

### Production Deployment (Render)

1. **Environment Variables:**

   - `TOKEN` - Your Telegram bot token
   - `RENDER_EXTERNAL_URL` - Your Render app URL
   - `WEBHOOK_SECRET` - (Optional) Webhook security token

2. **Deploy Configuration:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python3 /opt/render/project/src/wsgi.py`

The bot automatically detects the environment and switches between polling (dev) and webhook (production) modes.

## How to Use 💡

### First Time Setup

1. Start a chat with your bot
2. Send `/start` to see the welcome message
3. Send `/setlocation` for location sharing instructions
4. Tap 📎 → Location → Share Live Location
5. Your location is saved automatically!

### Daily Usage

- `/next` - "Next prayer is Maghrib at 18:30 (in 2h 15m)"
- `/today` - See full prayer schedule for your location

## Technical Architecture 🏗️

### Core Components

- **Bot Handler** (`bot.py`) - Telegram bot logic and command handlers
- **API Layer** (`api.py`) - Prayer times API and reverse geocoding
- **Location System** - GPS coordinates → City/Timezone conversion
- **Timezone Management** - Accurate time comparisons across regions

### APIs Used

- **Aladhan Prayer Times API** - Islamic prayer calculations
- **OpenStreetMap Nominatim** - Reverse geocoding (coordinates → city)

### Key Features

- **Timezone Awareness**: Compares current time and prayer times in the same timezone
- **Location Storage**: In-memory user location preferences
- **Error Handling**: Graceful fallbacks and user-friendly error messages
- **Security**: Sanitized logging to prevent token exposure

## Example Usage 📱

```
User: /start
Bot: 🕌 Welcome to MySolahReminderBot!
     📍 No location set (using Moscow as default)
     📋 Available Commands: /next, /today, /setlocation

User: [shares location]
Bot: ✅ Location saved! 📍 New York, United States

User: /next
Bot: 🕌 Next prayer is Maghrib at 18:45 Today (in 3h 22m)
     📍 New York, United States
```

## Privacy & Data 🔒

- **Location Data**: Stored temporarily in memory, reset on bot restart
- **No Database**: No persistent data storage
- **Minimal Logging**: Production logs exclude sensitive information
- **Open Source**: Full code transparency

## Contributing 🤝

Contributions are welcome! Areas for enhancement:

- Persistent user data storage
- Prayer reminders/notifications
- Multiple location support
- Islamic calendar integration
- Custom prayer calculation methods

## Tech Stack 📚

- **Python 3.9+** with asyncio
- **python-telegram-bot** - Telegram Bot API wrapper
- **aiohttp** - Async HTTP client
- **pytz** - Timezone calculations
- **Render** - Cloud deployment platform

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support 💬

If you encounter issues or have questions:

1. Check the [Issues](https://github.com/PrinceKay145/solah-reminder/issues) page
2. Create a new issue with details
3. Contact the maintainer

---

**Made with ❤️ for the Muslim community worldwide 🌍**
