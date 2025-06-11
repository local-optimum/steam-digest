"""Discord webhook integration for posting summaries."""

import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def post_to_discord(message: str, webhook_url: str) -> bool:
    """Post a message to Discord via webhook."""
    if not message or not webhook_url:
        logger.error("Message or webhook URL is empty")
        return False
    
    payload = {
        "content": message,
        "username": "Steam Digest Bot",
        "avatar_url": "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/avatars/fe/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg"
    }
    
    try:
        logger.info("Posting message to Discord...")
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
        
        logger.info("Successfully posted to Discord")
        return True
        
    except requests.RequestException as e:
        logger.error(f"Error posting to Discord: {e}")
        if hasattr(e.response, 'text'):
            logger.error(f"Discord API response: {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error posting to Discord: {e}")
        return False

def test_webhook(webhook_url: str) -> bool:
    """Test if the Discord webhook is working."""
    test_message = "🔧 Steam Digest Bot test message - webhook is working!"
    return post_to_discord(test_message, webhook_url) 