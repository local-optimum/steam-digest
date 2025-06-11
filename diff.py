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

def calculate_daily_diff(yesterday: Dict, today: Dict) -> Dict:
    """Calculate the daily difference between two snapshots."""
    result = {}
    
    # Process each user in today's snapshot
    for username in today:
        if username not in today:
            continue
            
        result[username] = {
            'played': {},           # game_name -> minutes_played_today
            'achievements': {},     # game_name -> [new_achievements]
            'total_minutes': 0,     # total minutes played today
            'new_games': [],        # games not in yesterday's snapshot
            'games_played': 0,      # number of different games played
        }
        
        today_user = today[username]
        yesterday_user = yesterday.get(username, {})
        
        today_games = today_user.get('games', {})
        yesterday_games = yesterday_user.get('games', {})
        
        for game_name, game_data in today_games.items():
            # Get playtime data
            today_playtime = game_data.get('playtime_forever', 0)
            yesterday_game = yesterday_games.get(game_name, {})
            yesterday_playtime = yesterday_game.get('playtime_forever', 0)
            
            # Calculate time played today (prefer 2-week data if available for more recent activity)
            playtime_2weeks = game_data.get('playtime_2weeks', 0)
            time_delta = today_playtime - yesterday_playtime
            
            # If we have 2-week data and no yesterday snapshot, use recent activity as indicator
            if not yesterday_games and playtime_2weeks > 0:
                time_delta = playtime_2weeks  # Use 2-week playtime as recent activity indicator
            
            if time_delta > 0:
                result[username]['played'][game_name] = time_delta
                result[username]['total_minutes'] += time_delta
                result[username]['games_played'] += 1
                
                # Check for new achievements
                today_achievements = set(game_data.get('achievements', []))
                yesterday_achievements = set(yesterday_game.get('achievements', []))
                new_achievements = list(today_achievements - yesterday_achievements)
                
                if new_achievements:
                    result[username]['achievements'][game_name] = new_achievements
            
            # Check if this is a new game
            if game_name not in yesterday_games:
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

def generate_daily_report(today_snapshot: Dict, yesterday_snapshot: Dict) -> Dict:
    """Generate a complete daily activity report."""
    daily_diff = calculate_daily_diff(yesterday_snapshot, today_snapshot)
    group_stats = calculate_group_stats(daily_diff)
    
    return {
        'individual_stats': daily_diff,
        'group_stats': group_stats,
        'has_activity': any(
            user_data['total_minutes'] > 0 
            for user_data in daily_diff.values()
        )
    } 