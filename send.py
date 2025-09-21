"""Discord webhook integration for posting summaries."""

import requests
import logging
import io
from typing import Optional

logger = logging.getLogger(__name__)

def post_to_discord(message: str, webhook_url: str) -> bool:
    """Post a message to Discord via webhook."""
    if not message or not webhook_url:
        logger.error("Message or webhook URL is empty")
        return False
    
    # Prepend user mention to the message
    message_with_mention = f"<@&1061692252981837885> {message}"
    
    payload = {
        "content": message_with_mention,
        "username": "Sigma Gaming News",
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

def post_to_discord_with_image(message: str, webhook_url: str, image_data: Optional[bytes] = None) -> bool:
    """Post a message with optional image to Discord via webhook."""
    if not message or not webhook_url:
        logger.error("Message or webhook URL is empty")
        return False
    
    # Prepend user mention to the message
    message_with_mention = f"<@&1061692252981837885> {message}"
    
    try:
        logger.info("Posting message with image to Discord...")
        
        # Prepare the multipart form data
        files = {}
        data = {
            "content": message_with_mention,
            "username": "Sigma Gaming News",
            "avatar_url": "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/avatars/fe/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg"
        }
        
        # Add image if provided
        if image_data:
            files['file'] = ('gaming_digest.png', io.BytesIO(image_data), 'image/png')
        
        response = requests.post(
            webhook_url,
            data=data,
            files=files if image_data else None,
            timeout=30
        )
        response.raise_for_status()
        
        logger.info("Successfully posted to Discord with image")
        return True
        
    except requests.RequestException as e:
        logger.error(f"Error posting to Discord: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Discord API response: {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error posting to Discord: {e}")
        return False

def test_webhook(webhook_url: str) -> bool:
    """Test if the Discord webhook is working."""
    test_message = "🔧 Steam Digest Bot test message - webhook is working!"
    return post_to_discord(test_message, webhook_url) 