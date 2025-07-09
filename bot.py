from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv
import api
from datetime import datetime

# Bot name = MySolahReminderBot
load_dotenv()

TOKEN = os.getenv('TOKEN')
RENDER_EXTERNAL_URL = os.getenv('RENDER_EXTERNAL_URL', 'https://solah-reminder.onrender.com')
async def hello(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hello {update.effective_user.first_name}")

async def start(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to MySolahReminderBot!\n" 
        "Use /next to get the next prayer time.\n"
        "Use /today to get the prayer times for today."
        )


async def next_prayer(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Get the current time and return the next upcoming prayer time
    """
    city, country = "Moscow", "Russia"

    prayer_data = await api.get_prayer_times(city, country)
    #check the current datetime of the user request and then check the next closest prayer time from the list.
    #if the request time is after the last prayer of today... get the prayer times for tomorrow and return the first prayer time.
    #due to calculation error, what threshold should be allowed for +/- 15 minutes?
    if "error" in prayer_data:
        await update.message.reply_text("Error: " + prayer_data["error"])
        return 
    
    
    timings = prayer_data["timings"]
    current_time = datetime.now().time()
    prayer_order = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

    next_prayer_name = None
    next_prayer_time = None
    for prayer in prayer_order:
        prayer_time = datetime.strptime(timings[prayer], "%H:%M").time()
        if prayer_time > current_time:
            next_prayer_name = prayer
            next_prayer_time = prayer_time
            break
    #if no more prayers today, get first prayer of next day
    if next_prayer_name is None:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
        tomorrow_data = await api.get_prayer_times(city, country, tomorrow)
        if "error" in tomorrow_data:
            await update.message.reply_text("Error getting tomorrow's prayer times")
            return
        
        next_prayer_name=prayer_order[0]
        next_prayer_time=datetime.strptime(tomorrow_data["timings"][next_prayer_name], "%H:%M").time()
        day_info = "Tomorrow"
    else: 
        day_info = "Today"
    current_datetime =datetime.now()
    prayer_datetime = datetime.combine(current_datetime.date(), next_prayer_time)
    if day_info == "Tomorrow":
        prayer_datetime += timedelta(days=1)
    time_until = prayer_datetime - current_datetime
    hours, remainder = divmod(time_until.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    await update.message.reply_text(
            f"🕌 Next prayer is {next_prayer_name} at {next_prayer_time.strftime('%H:%M')} {day_info} "
            f"(in {hours}h {minutes}m)\n"
            f"📍 {city}, {country}"
        )
async def today(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Get the current time and return the prayer times for today
    """
    city, country = "Moscow", "Russia"

    prayer_data = await api.get_prayer_times(city, country)
    if "error" in prayer_data:
        await update.message.reply_text("Error: " + prayer_data["error"])
        return 
    
    
    timings = prayer_data["timings"]
    await update.message.reply_text(
            f"Prayer times for {city}:\n"
            f"Fajr: {timings['Fajr']}\n"
            f"Dhuhr: {timings['Dhuhr']}\n"
            f"Asr: {timings['Asr']}\n"
            f"Maghrib: {timings['Maghrib']}\n"
            f"Isha: {timings['Isha']}\n"
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
def main() -> None:
    
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("next", next_prayer))
    app.add_handler(CommandHandler("today", today))

    if os.getenv('ENVIRONMENT') == 'PRODUCTION':
        #Webhook config for render
        PORT = int(os.getenv('PORT', 5000))
        WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}/webhook"

        print(f"Starting webhook on port {PORT}")
        app.run_webhook(
            listen = "0.0.0.0",
            port = PORT,
            webhook_url = WEBHOOK_URL,
            secret_token=os.getenv('WEBHOOK_SECRET')
        )
    else:
        print("Bot is starting...")
        app.run_polling()


if __name__ == '__main__':
    main()