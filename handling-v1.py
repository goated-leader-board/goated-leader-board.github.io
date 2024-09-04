from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import logging
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Set up logging for the bot
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection
conn = sqlite3.connect('leaderboard.db', check_same_thread=False)  # Avoid threading issues
cursor = conn.cursor()

# Function to format leaderboard for Telegram message
def format_leaderboard(leaderboard):
    if not leaderboard:
        return "No data available."
    return "\n".join([f"{i + 1}. {row[1]} - {row[2]}" for i, row in enumerate(leaderboard[:10])])

def get_leaderboard_data(timeframe):
    today = datetime.today().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    if timeframe == 'daily':
        cursor.execute('SELECT * FROM leaderboard WHERE last_wager_date = ?', (today,))
    elif timeframe == 'weekly':
        cursor.execute('SELECT * FROM leaderboard WHERE last_wager_date >= ?', (week_start,))
    elif timeframe == 'monthly':
        cursor.execute('SELECT * FROM leaderboard WHERE last_wager_date >= ?', (month_start,))
    
    return cursor.fetchall()

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to the Affiliate Leaderboard Bot!\n"
        "Use /daily_lb, /weekly_lb, /monthly_lb, or /<UserName>_wager to view the leaderboard or wager info.\n"
        "Additional commands: /help for command list, /stats for bot statistics."
    )

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "/start - Welcome message\n"
        "/daily_lb - View the daily leaderboard\n"
        "/weekly_lb - View the weekly leaderboard\n"
        "/monthly_lb - View the monthly leaderboard\n"
        "/<UserName>_wager - View wager info for a specific user\n"
        "/help - Command list\n"
        "/stats - View bot statistics"
    )

def stats(update: Update, context: CallbackContext):
    try:
        cursor.execute('SELECT COUNT(*) FROM leaderboard')
        user_count = cursor.fetchone()[0]
        update.message.reply_text(f"Currently tracking {user_count} users in the leaderboard.")
    except Exception as e:
        logging.error(f"Error fetching stats: {e}")
        update.message.reply_text(f"Error fetching stats: {e}")

def daily_lb(update: Update, context: CallbackContext):
    try:
        leaderboard = get_leaderboard_data('daily')
        update.message.reply_text("Daily Leaderboard:\n" + format_leaderboard(leaderboard))
    except Exception as e:
        logging.error(f"Error fetching daily leaderboard: {e}")
        update.message.reply_text(f"Error fetching daily leaderboard: {e}")

def weekly_lb(update: Update, context: CallbackContext):
    try:
        leaderboard = get_leaderboard_data('weekly')
        update.message.reply_text("Weekly Leaderboard:\n" + format_leaderboard(leaderboard))
    except Exception as e:
        logging.error(f"Error fetching weekly leaderboard: {e}")
        update.message.reply_text(f"Error fetching weekly leaderboard: {e}")

def monthly_lb(update: Update, context: CallbackContext):
    try:
        leaderboard = get_leaderboard_data('monthly')
        update.message.reply_text("Monthly Leaderboard:\n" + format_leaderboard(leaderboard))
    except Exception as e:
        logging.error(f"Error fetching monthly leaderboard: {e}")
        update.message.reply_text(f"Error fetching monthly leaderboard: {e}")

def username_wager(update: Update, context: CallbackContext):
    try:
        username = update.message.text.replace('_wager', '').strip()
        cursor.execute('SELECT * FROM leaderboard WHERE LOWER(name) = ?', (username.lower(),))
        player = cursor.fetchone()

        if player:
            today = datetime.today().date()
            week_start = today - timedelta(days=today.weekday())
            month_start = today.replace(day=1)
            
            wager_date = datetime.strptime(player[3], "%Y-%m-%d").date()
            daily_wager = player[2] if wager_date == today else 0
            weekly_wager = player[2] if wager_date >= week_start else 0
            monthly_wager = player[2] if wager_date >= month_start else 0

            update.message.reply_text(f"{player[1]}\nDaily Wager: {daily_wager}\nWeekly Wager: {weekly_wager}\nMonthly Wager: {monthly_wager}")
        else:
            update.message.reply_text("That UserName is not part of this community.")
    except Exception as e:
        logging.error(f"Error fetching wager info: {e}")
        update.message.reply_text(f"Error fetching wager info: {e}")

def main():
    # Initialize the bot
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise EnvironmentError("Missing TELEGRAM_BOT_TOKEN environment variable.")

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    # Add command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("daily_lb", daily_lb))
    dp.add_handler(CommandHandler("weekly_lb", weekly_lb))
    dp.add_handler(CommandHandler("monthly_lb", monthly_lb))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("stats", stats))

    # Handler for dynamic username wager commands
    dp.add_handler(MessageHandler(Filters.regex(r'_wager$'), username_wager))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
    conn.close()
