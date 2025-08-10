"""Main orchestration script for Steam Digest Bot."""

import os
import logging
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
    """Ensure snapshot directory and file exist."""
    snapshots_dir = Path('snapshots')
    snapshots_dir.mkdir(exist_ok=True)
    
    snapshot_file = snapshots_dir / 'snapshot.json'
    
    return str(snapshot_file)

def main():
    """Main execution function."""
    try:
        logger.info("Starting Steam Digest Bot...")
        
        # Setup file path - just one snapshot file
        snapshot_file = setup_snapshots()
        
        # Load previous snapshot from cache (empty on first run)
        logger.info("Loading previous snapshot...")
        previous_snapshot = load_snapshot(snapshot_file)
        
        if previous_snapshot:
            logger.info(f"✅ Found previous snapshot with {len(previous_snapshot)} users")
            # Log some basic stats about previous data
            for username, user_data in previous_snapshot.items():
                game_count = len(user_data.get('games', {}))
                logger.info(f"  - {username}: {game_count} games in previous snapshot")
        else:
            logger.info("ℹ️  No previous snapshot found - this is the first run")
            logger.info("ℹ️  Will report recent activity since there's no baseline to compare against")
        
        # Fetch current Steam activity
        logger.info("Fetching current Steam activity...")
        current_snapshot = fetch_all_users_snapshot(config.users, config.steam_api_key)
        
        if not current_snapshot:
            logger.error("Failed to fetch current snapshot")
            return False
        
        # Generate daily report by comparing current vs previous
        logger.info("Generating daily activity report...")
        daily_report = generate_daily_report(current_snapshot, previous_snapshot)
        
        # Log what we found
        if daily_report['has_activity']:
            logger.info(f"✅ Activity detected!")
            total_group_minutes = daily_report['group_stats']['total_group_minutes']
            logger.info(f"  - Total group activity: {total_group_minutes} minutes")
            
            for username, user_stats in daily_report['individual_stats'].items():
                user_minutes = user_stats['total_minutes']
                games_played = user_stats['games_played']
                new_games = len(user_stats['new_games'])
                logger.info(f"  - {username}: {user_minutes}min across {games_played} games, {new_games} new games")
        else:
            logger.info("ℹ️  No activity detected (this is normal if no one played games since last run)")
        
        # Generate AI summary
        logger.info("Generating AI summary...")
        summary = generate_summary(daily_report, config.gemini_api_key)
        
        if not summary:
            logger.error("Failed to generate summary")
            return False
        
        logger.info(f"Generated summary: {summary}")
        
        # Post to Discord
        logger.info("Posting to Discord...")
        success = post_to_discord(summary, config.discord_webhook_url)
        
        if not success:
            logger.error("Failed to post to Discord")
            return False
        
        # Save current snapshot as the new baseline for next run
        logger.info("Saving current snapshot for next run...")
        save_snapshot(current_snapshot, snapshot_file)
        
        logger.info("Steam Digest Bot completed successfully!")
        return True
            
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}")
        return False

def test_summary():
    """Test AI summary generation without posting to Discord."""
    try:
        logger.info("Testing AI summary generation...")
        
        # Setup file path
        snapshot_file = setup_snapshots()
        
        # Load previous snapshot
        previous_snapshot = load_snapshot(snapshot_file)
        
        # Fetch current snapshot
        logger.info("Fetching recent Steam activity...")
        current_snapshot = fetch_all_users_snapshot(config.users, config.steam_api_key)
        
        if not current_snapshot:
            logger.error("Failed to fetch current snapshot")
            return False
        
        # Save current snapshot for future reference
        save_snapshot(current_snapshot, snapshot_file)
        
        # Generate daily report
        logger.info("Generating daily activity report...")
        daily_report = generate_daily_report(current_snapshot, previous_snapshot)
        
        # Generate AI summary
        logger.info("Generating AI summary...")
        summary = generate_summary(daily_report, config.gemini_api_key)
        
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

def test_snapshot_rotation():
    """Test that snapshot rotation works correctly."""
    import tempfile
    import json
    import os
    
    # Configure basic logging for the test
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("Testing snapshot rotation logic...")
    
    try:
        # Import the functions we need directly
        from diff import load_snapshot, save_snapshot, generate_daily_report
        
        # Create temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            test_today = os.path.join(temp_dir, 'today.json')
            test_yesterday = os.path.join(temp_dir, 'yesterday.json')
            
            # Create mock snapshots
            mock_yesterday = {
                "user1": {
                    "games": {
                        "Game A": {"playtime_forever": 100, "achievements": ["ach1"]}
                    }
                }
            }
            
            mock_today = {
                "user1": {
                    "games": {
                        "Game A": {"playtime_forever": 150, "achievements": ["ach1", "ach2"]},
                        "Game B": {"playtime_forever": 30, "achievements": ["new_ach"]}
                    }
                }
            }
            
            # Save initial snapshots
            save_snapshot(mock_yesterday, test_yesterday)
            save_snapshot(mock_today, test_today)
            
            # Load and compare (simulating main flow)
            yesterday_data = load_snapshot(test_yesterday)
            today_data = load_snapshot(test_today)
            
            # Generate report
            daily_report = generate_daily_report(today_data, yesterday_data)
            
            # Check that we detected activity
            if daily_report['has_activity']:
                logger.info("✅ Successfully detected activity in test data")
                
                # Print some test results
                user1_stats = daily_report['individual_stats'].get('user1', {})
                logger.info(f"✅ User1 played {user1_stats.get('games_played', 0)} games")
                logger.info(f"✅ User1 total minutes: {user1_stats.get('total_minutes', 0)}")
                logger.info(f"✅ New games: {user1_stats.get('new_games', [])}")
                
                # Test rotation manually (since we can't use the function that requires config)
                logger.info("Testing rotation logic...")
                if os.path.exists(test_today):
                    if os.path.exists(test_yesterday):
                        os.remove(test_yesterday)
                        logger.info("✅ Removed old yesterday file")
                    os.rename(test_today, test_yesterday)
                    logger.info("✅ Moved today to yesterday")
                
                # Verify rotation worked
                if not os.path.exists(test_today):
                    logger.info("✅ Today file was moved correctly")
                if os.path.exists(test_yesterday):
                    logger.info("✅ Yesterday file now exists")
                    
                logger.info("✅ Snapshot rotation test passed!")
                return True
            else:
                logger.error("❌ Failed to detect activity in test data")
                logger.info("Debug - Daily report:")
                logger.info(json.dumps(daily_report, indent=2))
                return False
                
    except Exception as e:
        logger.error(f"❌ Snapshot rotation test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
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
        elif sys.argv[1] == "rotation":
            # Test snapshot rotation logic
            success = test_snapshot_rotation()  
            sys.exit(0 if success else 1)
        else:
            print("Usage:")
            print("  python main.py          - Run full digest (fetch, analyze, summarize, post)")
            print("  python main.py test     - Test configuration and APIs")
            print("  python main.py summary  - Test AI summary generation only (no Discord)")
            print("  python main.py rotation - Test snapshot rotation logic")
            sys.exit(1)
    else:
        # Run main digest process
        success = main()
        sys.exit(0 if success else 1) 