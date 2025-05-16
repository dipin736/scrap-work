import requests
import csv
from datetime import datetime

# Define the URL for the scorecard API request
url = "https://lmt.fn.sportradar.com/common/en/Etc:UTC/cricket/get_scorecard/60061743?T=exp=1747140257~acl=/*~data=eyJvIjoiaHR0cHM6Ly93aWRnZXRzLnNpci5zcG9ydHJhZGFyLmNvbSIsImEiOiJiZXRyYWRhciIsImFjdCI6Im9yaWdpbmNoZWNrIiwib3NyYyI6InhyZWYifQ~hmac=4aa2bba4c71792b09c28f158c58f6bc6f8734bf1834264cc69caa6ce83dea2d6"

# Headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Origin": "https://widgets.sir.sportradar.com",
    "Referer": "https://widgets.sir.sportradar.com/",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9"
}

def fetch_data(url):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises exception for 4XX/5XX errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def extract_match_info(data):
    """Extract basic match information"""
    try:
        doc = data.get('doc', [{}])[0]
        score_data = doc.get('data', {}).get('score', {})
        
        return {
            'match_id': doc.get('_id', 'N/A'),
            'match_title': score_data.get('matchTitle', 'N/A'),
            'series_name': score_data.get('seriesName', 'N/A'),
            'home_team': score_data.get('home', {}).get('name', 'N/A'),
            'away_team': score_data.get('away', {}).get('name', 'N/A'),
            'match_status': score_data.get('matchstatus', 'N/A'),
            'current_score': score_data.get('currentScore', 'N/A'),
            'current_over': score_data.get('currentOver', 'N/A'),
            'run_rate': score_data.get('runRate', 'N/A'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        print(f"Error extracting match info: {e}")
        return None

def extract_batting_data(data):
    """Extract batting performance data"""
    try:
        innings = data.get('doc', [{}])[0].get('data', {}).get('score', {}).get('innings', [])
        batting_data = []
        
        for inning in innings:
            inning_num = inning.get('inningNumber', 'N/A')
            batting = inning.get('batting', {})
            
            for batsman in batting.get('batsman', []):
                batting_data.append({
                    'inning': inning_num,
                    'batsman': batsman.get('batsmanName', 'N/A'),
                    'runs': batsman.get('runs', 'N/A'),
                    'balls': batsman.get('balls', 'N/A'),
                    'fours': batsman.get('fours', 'N/A'),
                    'sixes': batsman.get('sixes', 'N/A'),
                    'strike_rate': batsman.get('strikeRate', 'N/A'),
                    'status': batsman.get('description', 'N/A'),
                    'bowler': batsman.get('bowlerName', 'N/A')
                })
        
        return batting_data
    except Exception as e:
        print(f"Error extracting batting data: {e}")
        return []

def extract_bowling_data(data):
    """Extract bowling performance data"""
    try:
        innings = data.get('doc', [{}])[0].get('data', {}).get('score', {}).get('innings', [])
        bowling_data = []
        
        for inning in innings:
            inning_num = inning.get('inningNumber', 'N/A')
            bowling = inning.get('bowling', {})
            
            for bowler in bowling.get('bowler', []):
                bowling_data.append({
                    'inning': inning_num,
                    'bowler': bowler.get('bowlerName', 'N/A'),
                    'overs': bowler.get('overs', 'N/A'),
                    'maidens': bowler.get('maidens', 'N/A'),
                    'runs': bowler.get('runs', 'N/A'),
                    'wickets': bowler.get('wickets', 'N/A'),
                    'economy': bowler.get('economy', 'N/A')
                })
        
        return bowling_data
    except Exception as e:
        print(f"Error extracting bowling data: {e}")
        return []

def write_to_csv(data, filename_prefix="cricket_scorecard"):
    """Write data to CSV files with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Write match info
    if 'match_info' in data:
        with open(f"{filename_prefix}_match_{timestamp}.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data['match_info'].keys())
            writer.writeheader()
            writer.writerow(data['match_info'])
    
    # Write batting data
    if 'batting' in data and data['batting']:
        with open(f"{filename_prefix}_batting_{timestamp}.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data['batting'][0].keys())
            writer.writeheader()
            writer.writerows(data['batting'])
    
    # Write bowling data
    if 'bowling' in data and data['bowling']:
        with open(f"{filename_prefix}_bowling_{timestamp}.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data['bowling'][0].keys())
            writer.writeheader()
            writer.writerows(data['bowling'])

def main():
    # Fetch the scorecard data
    scorecard_data = fetch_data(url)
    
    if not scorecard_data:
        print("Failed to fetch data. Exiting.")
        return
    
    # Process the data
    processed_data = {
        'match_info': extract_match_info(scorecard_data),
        'batting': extract_batting_data(scorecard_data),
        'bowling': extract_bowling_data(scorecard_data)
    }
    
    # Write to CSV files
    write_to_csv(processed_data)
    print("Data successfully written to CSV files.")

if __name__ == "__main__":
    main()