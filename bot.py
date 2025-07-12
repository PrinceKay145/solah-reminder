from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import os
from dotenv import load_dotenv
import api
from datetime import datetime, timedelta
import logging
import pytz
from http.server import BaseHTTPRequestHandler
import threading
import json
# Enable logging
if os.getenv('RENDER'):
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.WARNING
    )
else:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
# ALWAYS suppress token exposure regardless of environment
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram.ext.Application").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


load_dotenv()

TOKEN = os.getenv('TOKEN')
RENDER_EXTERNAL_URL = os.getenv('RENDER_EXTERNAL_URL', 'https://solah-reminder.onrender.com')

user_locations={}

#HTTP Handler for health checks

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self): 
        if self.path == '/' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status":"ok",
                "message":"Solah Reminder Bot is running",
                "bot":"MySolahReminderBot",
                "timestamp":datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, format, *args):
        pass
def save_user_location(user_id:int, city:str, country:str) -> None:
    """
    Save user's location preference
    """
    user_locations[user_id] = {
        "city": city, 
        "country": country
    }

def get_user_location(user_id:int) ->dict:
    """Get user's saved location or return default"""
    return user_locations.get(user_id, {
        #Default fallback
        "city": "Moscow",  
        "country": "Russia"
    })
def has_user_location(user_id: int) -> bool:
    """Check if user has saved a location"""
    return user_id in user_locations
def get_current_time_in_timezone(timezone_name: str) -> datetime:
    """
    Get current time in a specific timezone
    
    Args:
        timezone_name: e.g., "Europe/Moscow", "UTC", "America/New_York"
    
    Returns:
        Current datetime in that timezone
    """
    try:
        tz = pytz.timezone(timezone_name)
        
        utc_now = datetime.now(pytz.utc)
        local_time = utc_now.astimezone(tz)
        return local_time
    except  Excetion as e:
        print(f"Error getting current time in timezone {timezone_name}: {str(e)}")
        return datetime.now(pytz.UTC)
    

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle when user shares their locatio"""

    location = update.message.location
    user_id = update.effective_user.id

    latitude =  location.latitude
    longitude = location.longitude

    await update.message.reply_text("📍 Processing your location...")

    location_info = await api.get_location_info(latitude=latitude, longitude=longitude)

    if location_info['success']:
        city = location_info['city']
        country = location_info['country']

        save_user_location(user_id, city, country)
        await update.message.reply_text(
            f"📍 Location received! I'll use this to provide accurate prayer times.\n\n"
            f"Here's what you can do next:\n"
            f"🕒 /next - See when the next prayer is\n"
            f"📅 /today - View today's full prayer schedule\n"
            f"👋 /hello - Get a friendly greeting"
        )
    else:
        await update.message.reply_text(
            f"❌ Sorry, I couldn't process your location.\n"
            f"Error: {location_info.get('error', 'Unknown error')}\n"
            f"Please try again or contact support."
        )

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hello {update.effective_user.first_name}")

async def set_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt user to share their location"""
    await update.message.reply_text(
        "📍 Set Your Location\n\n"
        "To get accurate prayer times for your area:\n\n"
        "1️⃣ Tap the 📎 (attachment) button below\n"
        "2️⃣ Select 'Location'\n"
        "3️⃣ Choose 'Share Live Location' or 'Send My Current Location'\n\n"
        "I'll use it for all future prayer time requests! 🕌"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.first_name
    user_id = update.effective_user.id

    if has_user_location(user_id):
        user_location=get_user_location(user_id)
        city, country = user_location["city"], user_location["country"]
        location_status = f"📍 Your location: {city}, {country}"
    else:
        location_status = "📍 No location set (using Moscow as default)"

    await update.message.reply_text(
        f"🕌 Welcome to MySolahReminderBot, {user_name}!\n\n"
        f"{location_status}\n\n"
        f"📋 Available Commands:\n"
        f"/next - Get the next prayer time\n"
        f"/today - Get today's prayer schedule\n"
        f"/hello - Get a friendly greeting\n\n"
        f"📍 Set Your Location:\n"
        f"Tap the 📎 button → Location → 'Share Live Location' or 'Send My Current Location'\n"
        f"This ensures accurate prayer times for your area!\n\n"
        f"🕌 Ready to help you stay connected with your prayers!"
    )

async def next_prayer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the current time and return the next upcoming prayer time"""
    user_id = update.effective_user.id
    user_location = get_user_location(user_id)
    city, country = user_location["city"], user_location["country"]

    prayer_data = await api.get_prayer_times(city, country)
    
    if "error" in prayer_data:
        await update.message.reply_text("Error: " + prayer_data["error"])
        return 
    
    timings = prayer_data["timings"]
    timezone_name=prayer_data["timezone"]
    
    current_datetime = get_current_time_in_timezone(timezone_name)
    current_time = current_datetime.time()
    prayer_order = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

    next_prayer_name = None
    next_prayer_time = None
    for prayer in prayer_order:
        prayer_time = datetime.strptime(timings[prayer], "%H:%M").time()
        if prayer_time > current_time:
            next_prayer_name = prayer
            next_prayer_time = prayer_time
            break
    
    # If no more prayers today, get first prayer of next day
    if next_prayer_name is None:
        tomorrow = (current_datetime + timedelta(days=1)).strftime("%d-%m-%Y")
        tomorrow_data = await api.get_prayer_times(city, country, date=tomorrow)
        if "error" in tomorrow_data:
            await update.message.reply_text("Error getting tomorrow's prayer times")
            return
        
        next_prayer_name = prayer_order[0]
        next_prayer_time = datetime.strptime(tomorrow_data["timings"][next_prayer_name], "%H:%M").time()
        day_info = "Tomorrow"
    else: 
        day_info = "Today"
    
    prayer_datetime = datetime.combine(current_datetime.date(), next_prayer_time)
    if day_info == "Tomorrow":
        prayer_datetime += timedelta(days=1)
        tz = pytz.timezone(timezone_name)
        prayer_datetime = tz.localize(prayer_datetime)
    else:
        tz = pytz.timezone(timezone_name)
        prayer_datetime = tz.localize(prayer_datetime)
    
    time_until = prayer_datetime - current_datetime
    hours, remainder = divmod(time_until.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    # Show if user has set a custom location
    location_note = "" if has_user_location(user_id) else "\n\n💡 Tip: Share your location to get prayer times for your area!"
    
    await update.message.reply_text(
        f"🕌 Next prayer is {next_prayer_name} at {next_prayer_time.strftime('%H:%M')} {day_info} "
        f"(in {hours}h {minutes}m)\n"
        f"📍 {city}, {country}"
        f"{location_note}"
    )

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the current time and return the prayer times for today"""
    user_id= update.effective_user.id
    user_location = get_user_location(user_id=user_id)
    city, country = user_location["city"], user_location["country"]

    prayer_data = await api.get_prayer_times(city, country)
    if "error" in prayer_data:
        await update.message.reply_text("Error: " + prayer_data["error"])
        return 
    
    timings = prayer_data["timings"]
    date = prayer_data["date"]
    # Show if user has set a custom location
    location_note = "" if has_user_location(user_id) else "\n\n💡 Tip: Share your location to get prayer times for your area!"
    
    await update.message.reply_text(
        f"🕌 Prayer times for {city}, {country}\n"
        f"📅 {date}\n\n"
        f"🌅 Fajr: {timings['Fajr']}\n"
        f"☀️ Dhuhr: {timings['Dhuhr']}\n"
        f"🌤️ Asr: {timings['Asr']}\n"
        f"🌅 Maghrib: {timings['Maghrib']}\n"
        f"🌙 Isha: {timings['Isha']}"
        f"{location_note}"
    )

# async def tomorrow(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """
#     Get the current time and return the prayer times for tomorrow
#     """
#     await update.message.reply_text("Tomorrow's prayer times are:")

# async def month(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """
#     Get the current time and return the prayer times for this month
#     """
#     await update.message.reply_text("Month's prayer times are:")

# async def location(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """
#     Get the current location and return the prayer times for that location
#     """
#     await update.message.reply_text("Location's prayer times are:")

def run_health_check():
    PORT = int(os.getenv('PORT', 5000))
    server = HTTPServer('0.0.0.0', PORT, HealthCheckHandler)
    logger.info(f"Health check server running on port {PORT}")
    server.serve_forever()
def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("next", next_prayer))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("setlocation", set_location))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # Check if we're on Render (production)
    if os.getenv('RENDER'):  # Render sets this automatically
        # Production: Use webhook
        PORT = int(os.getenv('PORT', 5000))
        WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}/webhook"

        logger.warning(f"Starting webhook on port {PORT}")
        logger.info(f"Webhook URL: {WEBHOOK_URL}")

        health_thread= threading.Thread(target=run_health_check, daemon=True)
        health_thread.start()
        
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=WEBHOOK_URL,
            secret_token=os.getenv('WEBHOOK_SECRET'),
            url_path="/webhook"
        )
    else:
        # Local development: Use polling
        logger.info("Bot is starting in polling mode (local development)...")
        app.run_polling(poll_interval=5)

if __name__ == '__main__':
    main()