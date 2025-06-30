import os
import json
from datetime import datetime
from dotenv import load_dotenv
from fetch import fetch_user_snapshot
from diff import calculate_daily_diff
from summarise import generate_summary

def load_snapshot(filename: str):
    """Load a snapshot from file if it exists."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_snapshot(data, filename: str):
    """Save snapshot to file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    api_key = os.getenv('STEAM_API_KEY')
    users_config = os.getenv('USERS', '')
    
    if not api_key or not users_config:
        print("Error: Missing required environment variables (STEAM_API_KEY, USERS)")
        return
    
    # Parse users
    users = {}
    for user_entry in users_config.split(','):
        if ':' in user_entry:
            username, steam_id = user_entry.split(':')
            users[username] = steam_id
    
    # Create snapshots directory if it doesn't exist
    os.makedirs('snapshots', exist_ok=True)
    
    # Load previous snapshot if it exists
    previous_snapshot = load_snapshot('snapshots/test_previous.json')
    
    # Fetch current snapshot
    current_snapshot = {}
    for username, steam_id in users.items():
        print(f"\nFetching data for {username}...")
        current_snapshot[username] = fetch_user_snapshot(username, steam_id, api_key)
    
    # Save current snapshot
    save_snapshot(current_snapshot, 'snapshots/test_current.json')
    
    if previous_snapshot:
        print("\nCalculating diff...")
        # Calculate diff
        diff = calculate_daily_diff(previous_snapshot, current_snapshot)
        save_snapshot(diff, 'snapshots/test_diff.json')
        
        # Generate summary
        print("\nGenerating summary...")
        summary = generate_summary(diff, api_key)
        print("\nSummary:")
        print("--------")
        print(summary)
    else:
        print("\nNo previous snapshot found. This run will create the initial snapshot.")
        print("Run the script again tomorrow to see the diff and summary.")

if __name__ == "__main__":
    main() 