"""Main orchestration script for Steam Digest Bot."""

import os
import logging
import shutil
from datetime import datetime
from pathlib import Path

from config import config
from fetch import fetch_all_users_snapshot
from diff import load_snapshot, save_snapshot, generate_daily_report
from summarise import generate_summary
from send import post_to_discord

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('steam_digest.log')
    ]
)

# Reduce noisy debug logs from requests/urllib3
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def setup_snapshots():
    """Ensure snapshot directory and files exist."""
    snapshots_dir = Path('snapshots')
    snapshots_dir.mkdir(exist_ok=True)
    
    today_file = snapshots_dir / 'today.json'
    yesterday_file = snapshots_dir / 'yesterday.json'
    
    return str(today_file), str(yesterday_file)

def rotate_snapshots(today_file: str, yesterday_file: str):
    """Rotate today's snapshot to yesterday's for the next run."""
    try:
        logger.info(f"Starting snapshot rotation...")
        logger.info(f"Checking for today's snapshot at: {today_file}")
        
        if os.path.exists(today_file):
            logger.info("Found today's snapshot")
            if os.path.exists(yesterday_file):
                logger.info(f"Removing old yesterday's snapshot: {yesterday_file}")
                os.remove(yesterday_file)
            logger.info(f"Moving today's snapshot to yesterday's: {today_file} -> {yesterday_file}")
            shutil.move(today_file, yesterday_file)
            logger.info("Successfully rotated today's snapshot to yesterday's")
        else:
            logger.warning(f"No today snapshot found at {today_file} to rotate")
            
        # Log the state of files after rotation
        logger.info("File state after rotation:")
        if os.path.exists(today_file):
            logger.info(f"today.json exists at {today_file}")
        else:
            logger.info("today.json does not exist")
        if os.path.exists(yesterday_file):
            logger.info(f"yesterday.json exists at {yesterday_file}")
        else:
            logger.info("yesterday.json does not exist")
            
    except Exception as e:
        logger.error(f"Error rotating snapshots: {e}")
        # Log the full exception details
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

def main():
    """Main execution function."""
    try:
        logger.info("Starting Steam Digest Bot...")
        
        # Setup file paths
        today_file, yesterday_file = setup_snapshots()
        
        # Rotate previous snapshots
        rotate_snapshots(today_file, yesterday_file)
        
        # Load yesterday's snapshot (for comparison)
        logger.info("Loading yesterday's snapshot...")
        yesterday_snapshot = load_snapshot(yesterday_file)
        
        # Fetch today's snapshot
        logger.info("Fetching today's Steam activity...")
        today_snapshot = fetch_all_users_snapshot(config.users, config.steam_api_key)
        
        if not today_snapshot:
            logger.error("Failed to fetch today's snapshot")
            return False
        
        # Save today's snapshot
        save_snapshot(today_snapshot, today_file)
        
        # Generate daily report
        logger.info("Generating daily activity report...")
        daily_report = generate_daily_report(today_snapshot, yesterday_snapshot)
        
        # Generate AI summary
        logger.info("Generating AI summary...")
        summary = generate_summary(daily_report, config.kluster_api_key)
        
        if not summary:
            logger.error("Failed to generate summary")
            return False
        
        logger.info(f"Generated summary: {summary}")
        
        # Post to Discord
        logger.info("Posting to Discord...")
        success = post_to_discord(summary, config.discord_webhook_url)
        
        if success:
            logger.info("Steam Digest Bot completed successfully!")
            return True
        else:
            logger.error("Failed to post to Discord")
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}")
        return False

def test_summary():
    """Test AI summary generation without posting to Discord."""
    try:
        logger.info("Testing AI summary generation...")
        
        # Setup file paths
        today_file, yesterday_file = setup_snapshots()
        
        # Load snapshots (create dummy data if needed)
        yesterday_snapshot = load_snapshot(yesterday_file)
        
        # Fetch today's snapshot (optimized for recent activity + achievements)
        logger.info("Fetching recent Steam activity (optimized approach with achievements)...")
        today_snapshot = fetch_all_users_snapshot(config.users, config.steam_api_key, fetch_achievements=True)
        
        if not today_snapshot:
            logger.error("Failed to fetch today's snapshot")
            return False
        
        # Save today's snapshot for future reference
        save_snapshot(today_snapshot, today_file)
        
        # Generate daily report
        logger.info("Generating daily activity report...")
        daily_report = generate_daily_report(today_snapshot, yesterday_snapshot)
        
        # Generate AI summary
        logger.info("Generating AI summary...")
        summary = generate_summary(daily_report, config.kluster_api_key)
        
        if summary:
            print("\n" + "="*60)
            print("🎮 GENERATED SUMMARY:")
            print("="*60)
            print(summary)
            print("="*60)
            logger.info("AI summary test completed successfully!")
            return True
        else:
            logger.error("Failed to generate summary")
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error in summary test: {e}")
        return False

def test_configuration():
    """Test that all configuration and APIs are working."""
    logger.info("Testing configuration...")
    
    try:
        # Test configuration loading
        logger.info(f"Loaded {len(config.users)} users: {list(config.users.keys())}")
        
        # Test Discord webhook
        from send import test_webhook
        if test_webhook(config.discord_webhook_url):
            logger.info("Discord webhook test successful")
        else:
            logger.error("Discord webhook test failed")
            return False
        
        # Test Steam API with first user
        if config.users:
            first_user = list(config.users.items())[0]
            username, steam_id = first_user
            logger.info(f"Testing Steam API with user: {username}")
            
            from fetch import fetch_user_snapshot
            test_snapshot = fetch_user_snapshot(username, steam_id, config.steam_api_key)
            
            if test_snapshot and test_snapshot.get('games'):
                logger.info(f"Steam API test successful - found {len(test_snapshot['games'])} games")
            else:
                logger.warning("Steam API test returned no games (this might be normal)")
        
        logger.info("Configuration test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Configuration test failed: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # Run configuration test
            success = test_configuration()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "summary":
            # Test AI summary generation without Discord posting
            success = test_summary()
            sys.exit(0 if success else 1)
        else:
            print("Usage:")
            print("  python main.py          - Run full digest (fetch, analyze, summarize, post)")
            print("  python main.py test     - Test configuration and APIs")
            print("  python main.py summary  - Test AI summary generation only (no Discord)")
            sys.exit(1)
    else:
        # Run main digest process
        success = main()
        sys.exit(0 if success else 1) 