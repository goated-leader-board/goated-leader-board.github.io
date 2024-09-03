import requests
import os
import json

# Configuration
BASE_URL = "https://europe-west2-g3casino.cloudfunctions.net/user/affiliate/referral-leaderboard"
OUTPUT_HTML_FILE = "docs/index.html"  # GitHub Pages looks for index.html in the 'docs' folder
AUTHORIZATION_HEADER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiI1a1V0ZzFPTWV0SzhvZkFvRTFteiIsImlhdCI6MTcyMzExMzQ3MH0.GpTH9ix0WrKeWOh7B__wQEwRrzzeaNZkUSMU4wamBiA"

# Function to fetch leaderboard data
def fetch_leaderboard_data():
    try:
        headers = {
            "Authorization": f"Bearer {AUTHORIZATION_HEADER}"
        }
        response = requests.get(BASE_URL, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch data: {e}")

# Function to generate HTML content
def generate_html(leaderboard_data):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Casino Leaderboard</title>
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        <h1>Casino Leaderboard</h1>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Username</th>
                    <th>Wagered Today</th>
                    <th>Wagered This Week</th>
                    <th>Wagered All Time</th>
                </tr>
            </thead>
            <tbody>
    """

    players = leaderboard_data.get('data', [])
    if not players:
        html_content += '<tr><td colspan="5">No data available.</td></tr>'
    else:
        for index, player in enumerate(players):
            html_content += f"""
            <tr>
                <td>{index + 1}</td>
                <td>{player.get('name', 'N/A')}</td>
                <td>${player.get('wagered', {}).get('today', 'N/A'):.2f}</td>
                <td>${player.get('wagered', {}).get('this_week', 'N/A'):.2f}</td>
                <td>${player.get('wagered', {}).get('all_time', 'N/A'):.2f}</td>
            </tr>
            """

    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    return html_content

# Function to save HTML content to a file
def save_html_to_file(html_content, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

# Main script execution
if __name__ == "__main__":
    try:
        # Fetch leaderboard data
        leaderboard_data = fetch_leaderboard_data()
        print("Fetched data:", json.dumps(leaderboard_data, indent=2))  # Log data for debugging

        # Generate HTML content
        html_content = generate_html(leaderboard_data)

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(OUTPUT_HTML_FILE), exist_ok=True)

        # Save the HTML to file
        save_html_to_file(html_content, OUTPUT_HTML_FILE)

        print(f"Leaderboard HTML generated and saved to {OUTPUT_HTML_FILE}")
    except Exception as e:
        print(f"An error occurred: {e}")
