"""Snapshot comparison logic for calculating daily gaming differences."""

import json
import logging
from typing import Dict, List, Set
from pathlib import Path

logger = logging.getLogger(__name__)

def load_snapshot(filepath: str) -> Dict:
    """Load a snapshot from JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info(f"No previous snapshot found at {filepath} (this is normal for first run)")
        return {}
    except json.JSONDecodeError as e:
        logger.warning(f"Could not parse snapshot from {filepath}: {e}")
        return {}

def save_snapshot(snapshot: Dict, filepath: str) -> None:
    """Save a snapshot to JSON file."""
    try:
        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2)
        logger.info(f"Saved snapshot to {filepath}")
    except Exception as e:
        logger.error(f"Error saving snapshot to {filepath}: {e}")

def calculate_daily_diff(previous: Dict, current: Dict) -> Dict:
    """Calculate the daily difference between two snapshots."""
    result = {}
    
    # Process each user in current snapshot
    for username in current:
        if username not in current:
            continue
            
        result[username] = {
            'played': {},           # game_name -> minutes_played_since_last_run
            'achievements': {},     # game_name -> [new_achievements]
            'total_minutes': 0,     # total minutes played since last run
            'new_games': [],        # games not in previous snapshot
            'games_played': 0,      # number of different games played
        }
        
        current_user = current[username]
        previous_user = previous.get(username, {})
        
        current_games = current_user.get('games', {})
        previous_games = previous_user.get('games', {})
        
        for game_name, game_data in current_games.items():
            # Get playtime data
            current_playtime = game_data.get('playtime_forever', 0)
            previous_game = previous_games.get(game_name, {})
            previous_playtime = previous_game.get('playtime_forever', 0)
            
            # Calculate time played since last run
            time_delta = current_playtime - previous_playtime
            
            # If there's no previous snapshot, use 2-week activity as recent activity indicator
            if not previous and game_data.get('playtime_2weeks', 0) > 0:
                time_delta = game_data.get('playtime_2weeks', 0)
                logger.info(f"First run: Using 2-week activity for {username}/{game_name}: {time_delta} minutes")
            
            # Only count activity if we have a positive time difference
            if time_delta > 0:
                result[username]['played'][game_name] = time_delta
                result[username]['total_minutes'] += time_delta
                result[username]['games_played'] += 1
                
                # Check for new achievements (on first run, show all achievements as "new")
                current_achievements = set(game_data.get('achievements', []))
                previous_achievements = set(previous_game.get('achievements', []))
                new_achievements = list(current_achievements - previous_achievements)
                
                if new_achievements:
                    result[username]['achievements'][game_name] = new_achievements
            
            # Check if this is a new game (on first run, all games are "new")
            if game_name not in previous_games:
                result[username]['new_games'].append(game_name)
    
    return result

def calculate_group_stats(daily_diff: Dict) -> Dict:
    """Calculate group-wide statistics from individual user diffs."""
    stats = {
        'total_group_minutes': 0,
        'most_active_player': None,
        'most_played_game': None,
        'games_played_together': [],
        'longest_session': None,
        'total_achievements': 0,
        'new_games_discovered': []
    }
    
    # Track all games played by any user
    all_games_played = {}
    user_totals = {}
    all_achievements = 0
    all_new_games = set()
    
    for username, user_data in daily_diff.items():
        user_total = user_data['total_minutes']
        user_totals[username] = user_total
        stats['total_group_minutes'] += user_total
        
        # Count achievements
        for game_achievements in user_data['achievements'].values():
            all_achievements += len(game_achievements)
        
        # Track new games
        all_new_games.update(user_data['new_games'])
        
        # Track games played by each user
        for game_name, minutes in user_data['played'].items():
            if game_name not in all_games_played:
                all_games_played[game_name] = {'players': [], 'total_minutes': 0}
            all_games_played[game_name]['players'].append(username)
            all_games_played[game_name]['total_minutes'] += minutes
    
    # Find most active player
    if user_totals:
        stats['most_active_player'] = max(user_totals, key=user_totals.get)
    
    # Find most played game
    if all_games_played:
        most_played = max(all_games_played, key=lambda x: all_games_played[x]['total_minutes'])
        stats['most_played_game'] = {
            'name': most_played,
            'total_minutes': all_games_played[most_played]['total_minutes'],
            'players': all_games_played[most_played]['players']
        }
    
    # Find games played together (by multiple players)
    stats['games_played_together'] = [
        {
            'name': game_name,
            'players': game_data['players'],
            'total_minutes': game_data['total_minutes']
        }
        for game_name, game_data in all_games_played.items()
        if len(game_data['players']) > 1
    ]
    
    # Find longest single session
    longest_session = None
    longest_minutes = 0
    for username, user_data in daily_diff.items():
        for game_name, minutes in user_data['played'].items():
            if minutes > longest_minutes:
                longest_minutes = minutes
                longest_session = {
                    'player': username,
                    'game': game_name,
                    'minutes': minutes
                }
    stats['longest_session'] = longest_session
    
    stats['total_achievements'] = all_achievements
    stats['new_games_discovered'] = list(all_new_games)
    
    return stats

def generate_daily_report(current_snapshot: Dict, previous_snapshot: Dict) -> Dict:
    """Generate a complete daily activity report."""
    daily_diff = calculate_daily_diff(previous_snapshot, current_snapshot)
    group_stats = calculate_group_stats(daily_diff)
    
    return {
        'individual_stats': daily_diff,
        'group_stats': group_stats,
        'has_activity': any(
            user_data['total_minutes'] > 0 
            for user_data in daily_diff.values()
        )
    } 