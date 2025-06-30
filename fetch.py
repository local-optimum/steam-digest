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

def fetch_user_snapshot(username: str, steam_id: str, api_key: str) -> Dict:
    """Fetch a snapshot of user's gaming activity."""
    logger.info(f"Fetching activity snapshot for user: {username}")
    
    snapshot = {
        'username': username,
        'steam_id': steam_id,
        'games': {}
    }
    
    # First, get all owned games (complete library)
    owned_games_data = get_owned_games(steam_id, api_key)
    if not owned_games_data or 'response' not in owned_games_data:
        logger.error(f"Failed to fetch owned games for {username}")
        return snapshot
        
    owned_games = owned_games_data['response'].get('games', [])
    logger.info(f"Found {len(owned_games)} owned games for {username}")
    
    # Get recently played games for supplementary data
    recent_games_data = get_recent_games(steam_id, api_key)
    recent_games = {}
    if recent_games_data and 'response' in recent_games_data:
        for game in recent_games_data['response'].get('games', []):
            recent_games[str(game['appid'])] = game
    
    # Process all owned games
    for game in owned_games:
        app_id = str(game['appid'])
        name = game.get('name', f"App {app_id}")
        
        # Base game data
        game_data = {
            'app_id': app_id,
            'playtime_forever': game.get('playtime_forever', 0),
            'playtime_2weeks': 0  # Default to 0 if not recently played
        }
        
        # Add recent activity data if available
        if app_id in recent_games:
            recent_game = recent_games[app_id]
            game_data['playtime_2weeks'] = recent_game.get('playtime_2weeks', 0)
        
        snapshot['games'][name] = game_data
    
    return snapshot

def fetch_all_users_snapshot(users: Dict[str, str], api_key: str, fetch_achievements: bool = True) -> Dict:
    """Fetch snapshots for all configured users."""
    all_snapshots = {}
    
    for username, steam_id in users.items():
        snapshot = fetch_user_snapshot(username, steam_id, api_key, fetch_achievements)
        all_snapshots[username] = snapshot
    
    return all_snapshots 