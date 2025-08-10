"""Configuration loader for Steam Digest Bot."""

import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    """Configuration class for Steam Digest Bot."""
    
    def __init__(self):
        self.steam_api_key = os.getenv('STEAM_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        self.users_raw = os.getenv('USERS', '')
        
        # Validate required environment variables
        self._validate_config()
        
        # Parse users configuration
        self.users = self._parse_users()
    
    def _validate_config(self):
        """Validate that all required environment variables are set."""
        required_vars = [
            ('STEAM_API_KEY', self.steam_api_key),
            ('GEMINI_API_KEY', self.gemini_api_key),
            ('DISCORD_WEBHOOK_URL', self.discord_webhook_url),
            ('USERS', self.users_raw)
        ]
        
        missing_vars = [var_name for var_name, var_value in required_vars if not var_value]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    def _parse_users(self):
        """Parse users configuration from environment variable."""
        users = {}
        if not self.users_raw:
            return users
            
        logger.info(f"Raw users string: {self.users_raw}")
        for user_config in self.users_raw.split(','):
            logger.info(f"Processing user config: {user_config}")
            if ':' in user_config:
                username, steam_id = user_config.strip().split(':', 1)
                users[username.strip()] = steam_id.strip()
                logger.info(f"Added user: {username.strip()} with steam_id: {steam_id.strip()}")
        
        logger.info(f"Final parsed users: {users}")
        return users

# Global configuration instance
config = Config() 