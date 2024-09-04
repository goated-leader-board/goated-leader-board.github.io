import requests
from datetime import datetime, timedelta
import os
import logging
import sqlite3
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
BASE_URL = os.getenv("LEADERBOARD_API_URL", "https://europe-west2-g3casino.cloudfunctions.net/user/affiliate/referral-leaderboard")
AUTHORIZATION_HEADER = os.getenv("AUTHORIZATION_HEADER")

if not AUTHORIZATION_HEADER:
    raise EnvironmentError("Missing AUTHORIZATION_HEADER environment variable.")

# Database connection
conn = sqlite3.connect('leaderboard.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS leaderboard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    wagered_all_time REAL,
    last_wager_date TEXT
)
''')
conn.commit()

# Retry logic for network requests
def fetch_leaderboard_data(retries=3, backoff_factor=0.3):
    headers = {"Authorization": f"Bearer {AUTHORIZATION_HEADER}"}
    for attempt in range(retries):
        try:
            response = requests.get(BASE_URL, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                sleep_time = backoff_factor * (2 ** attempt)
                logging.warning(f"Request failed: {e}. Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                logging.error(f"Request failed after {retries} attempts: {e}")
                raise
    return None

# Save data to database
def save_data_to_db(players):
    cursor.execute('DELETE FROM leaderboard')  # Clear the table before inserting new data
    for player in players:
        if validate_player_data(player):
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO leaderboard (name, wagered_all_time, last_wager_date)
                    VALUES (?, ?, ?)
                ''', (player['name'], player['wagered'].get('all_time', 0), player['wagered'].get('last_wager_date')))
            except sqlite3.Error as e:
                logging.error(f"Database error: {e}")
    conn.commit()

def validate_player_data(player):
    if 'name' not in player or 'wagered' not in player:
        logging.warning(f"Invalid player data: {player}")
        return False
    return True

def main():
    try:
        players = fetch_leaderboard_data()
        if players:
            save_data_to_db(players)
            logging.info("Leaderboard data saved to the database successfully.")
        else:
            logging.error("No data fetched from the API.")
    except Exception as e:
        logging.error(f"Error during the main process: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
