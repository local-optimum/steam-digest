"""Steam API integration for fetching user activity."""

import requests
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def get_recent_games(steam_id: str, api_key: str) -> Optional[Dict]:
    """Fetch recently played games for a Steam user."""
    url = f"https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/"
    params = {
        'key': api_key,
        'steamid': steam_id,
        'format': 'json'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching recent games for {steam_id}: {e}")
        return None

def get_owned_games(steam_id: str, api_key: str) -> Optional[Dict]:
    """Fetch owned games for a Steam user."""
    url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        'key': api_key,
        'steamid': steam_id,
        'format': 'json',
        'include_appinfo': True,
        'include_played_free_games': True
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching owned games for {steam_id}: {e}")
        return None

def get_achievements(steam_id: str, app_id: str, api_key: str) -> Optional[Dict]:
    """Fetch achievements for a specific game and user."""
    url = f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/"
    params = {
        'key': api_key,
        'steamid': steam_id,
        'appid': app_id,
        'format': 'json'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        # Don't log warnings for common cases where games don't have achievements
        if hasattr(e, 'response') and e.response.status_code == 400:
            logger.debug(f"Game {app_id} has no achievements or restricted achievement API")
        else:
            logger.warning(f"Error fetching achievements for {steam_id}, app {app_id}: {e}")
        return None

def fetch_user_snapshot(username: str, steam_id: str, api_key: str, fetch_achievements: bool = True) -> Dict:
    """Fetch a snapshot of user's recent gaming activity (optimized for daily digest)."""
    logger.info(f"Fetching recent activity snapshot for user: {username}")
    
    snapshot = {
        'username': username,
        'steam_id': steam_id,
        'games': {}
    }
    
    # First, get recently played games (last 2 weeks)
    recent_games_data = get_recent_games(steam_id, api_key)
    recent_games = {}
    
    if recent_games_data and 'response' in recent_games_data and 'games' in recent_games_data['response']:
        recent_games_list = recent_games_data['response']['games']
        logger.info(f"Found {len(recent_games_list)} recently played games for {username}")
        
        # Create a lookup for recent games with their playtime
        for game in recent_games_list:
            app_id = str(game['appid'])
            recent_games[app_id] = {
                'name': game.get('name', f'Unknown Game {app_id}'),
                'playtime_2weeks': game.get('playtime_2weeks', 0),
                'playtime_forever': game.get('playtime_forever', 0)
            }
    else:
        logger.info(f"No recent games found for {username}, falling back to owned games")
        # Fallback: get all owned games but limit to those with recent activity
        owned_games_data = get_owned_games(steam_id, api_key)
        if owned_games_data and 'response' in owned_games_data:
            games = owned_games_data['response'].get('games', [])
            # Only include games with significant playtime (> 30 minutes total) to focus on active games
            for game in games:
                if game.get('playtime_forever', 0) > 30:
                    app_id = str(game['appid'])
                    recent_games[app_id] = {
                        'name': game.get('name', f'Unknown Game {app_id}'),
                        'playtime_2weeks': 0,  # We don't have 2-week data from owned games
                        'playtime_forever': game.get('playtime_forever', 0)
                    }
    
    if not recent_games:
        logger.warning(f"No games found for {username}")
        return snapshot
    
    logger.info(f"Processing {len(recent_games)} relevant games for {username}")
    
    # Process each game
    for i, (app_id, game_data) in enumerate(recent_games.items()):
        game_name = game_data['name']
        
        if i % 5 == 0:  # Progress indicator every 5 games (since we have fewer games now)
            logger.info(f"Processing game {i+1}/{len(recent_games)} for {username}: {game_name}")
        
        snapshot['games'][game_name] = {
            'app_id': app_id,
            'playtime_forever': game_data['playtime_forever'],
            'playtime_2weeks': game_data.get('playtime_2weeks', 0),
            'achievements': []
        }
        
        # Fetch achievements only for games with recent activity or significant playtime
        if fetch_achievements and (game_data.get('playtime_2weeks', 0) > 0 or game_data['playtime_forever'] > 60):
            achievements_data = get_achievements(steam_id, app_id, api_key)
            if achievements_data and 'playerstats' in achievements_data:
                if 'achievements' in achievements_data['playerstats']:
                    achieved = [
                        ach['apiname'] for ach in achievements_data['playerstats']['achievements']
                        if ach.get('achieved', 0) == 1
                    ]
                    snapshot['games'][game_name]['achievements'] = achieved
    
    logger.info(f"Completed optimized snapshot for {username}: {len(snapshot['games'])} games")
    return snapshot

def fetch_all_users_snapshot(users: Dict[str, str], api_key: str, fetch_achievements: bool = True) -> Dict:
    """Fetch snapshots for all configured users."""
    all_snapshots = {}
    
    for username, steam_id in users.items():
        snapshot = fetch_user_snapshot(username, steam_id, api_key, fetch_achievements)
        all_snapshots[username] = snapshot
    
    return all_snapshots 