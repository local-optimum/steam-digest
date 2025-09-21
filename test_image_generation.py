#!/usr/bin/env python3
"""
Test script for the new image generation functionality.

This script tests the image generation feature added to the Steam Digest Bot.
It creates mock data and tests both text summary and image generation.

Usage:
    python test_image_generation.py

Prerequisites:
    - GEMINI_API_KEY set in environment or .env file
    - All dependencies installed (see requirements.txt)
"""

import logging
import os
from dotenv import load_dotenv
from summarise import generate_summary_with_image, create_image_prompt

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_mock_report_with_activity():
    """Create a mock report with racing games activity for testing."""
    return {
        'has_activity': True,
        'individual_stats': {
            'DonkFresh': {
                'total_minutes': 90, 
                'played': {'Trackmania': 60, 'Dakar Desert Rally': 30}, 
                'new_games': [], 
                'first_time_played': [],
                'games_played': 2
            },
            'BoxFresh': {
                'total_minutes': 120, 
                'played': {'Trackmania': 90, 'Dakar Desert Rally': 30}, 
                'new_games': [], 
                'first_time_played': [],
                'games_played': 2
            },
            'ViralNinja': {
                'total_minutes': 75,
                'played': {'Dakar Desert Rally': 75},
                'new_games': ['Dakar Desert Rally'],
                'first_time_played': ['Dakar Desert Rally'],
                'games_played': 1
            }
        },
        'group_stats': {
            'total_group_minutes': 285,
            'most_played_game': {'name': 'Trackmania', 'minutes': 150},
            'games_played_together': [
                {'name': 'Trackmania', 'minutes': 150},
                {'name': 'Dakar Desert Rally', 'minutes': 135}
            ]
        }
    }

def create_mock_report_no_activity():
    """Create a mock report with no gaming activity for testing."""
    return {
        'has_activity': False,
        'individual_stats': {
            'DonkFresh': {'total_minutes': 0, 'played': {}, 'new_games': [], 'first_time_played': [], 'games_played': 0},
            'BoxFresh': {'total_minutes': 0, 'played': {}, 'new_games': [], 'first_time_played': [], 'games_played': 0},
            'ViralNinja': {'total_minutes': 0, 'played': {}, 'new_games': [], 'first_time_played': [], 'games_played': 0}
        },
        'group_stats': {
            'total_group_minutes': 0,
            'most_played_game': None,
            'games_played_together': []
        }
    }

def test_image_prompt_generation():
    """Test the image prompt generation function."""
    logger.info("Testing image prompt generation...")
    
    # Test with activity
    mock_report = create_mock_report_with_activity()
    mock_summary = "🏎️ Epic racing day! DonkFresh dominated both Trackmania (60 mins) and Dakar Desert Rally (30 mins), while BoxFresh crushed Trackmania for 90 minutes and tackled the desert for 30 more. ViralNinja spent 75 minutes conquering Dakar Desert Rally for the first time! All three legends tearing up the tracks together! 🏁"
    
    image_prompt = create_image_prompt(mock_summary, mock_report)
    
    print("\n" + "="*60)
    print("🖼️ GENERATED IMAGE PROMPT:")
    print("="*60)
    print(image_prompt)
    print("="*60)
    
    # Test with no activity
    mock_report_no_activity = create_mock_report_no_activity()
    mock_summary_no_activity = "🎮 No gaming activity detected today. Everyone must be taking a break! 🛋️"
    
    image_prompt_no_activity = create_image_prompt(mock_summary_no_activity, mock_report_no_activity)
    
    print("\n" + "="*60)
    print("🖼️ IMAGE PROMPT (NO ACTIVITY):")
    print("="*60)
    print(image_prompt_no_activity)
    print("="*60)
    
    logger.info("Image prompt generation test completed!")

def test_full_generation():
    """Test the full summary and image generation."""
    logger.info("Testing full summary and image generation...")
    
    # Get API key
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        logger.error("GEMINI_API_KEY not found in environment variables!")
        logger.info("Please set your GEMINI_API_KEY in your .env file or environment")
        return False
    
    # Test with activity
    mock_report = create_mock_report_with_activity()
    
    try:
        summary, image_data = generate_summary_with_image(mock_report, gemini_api_key)
        
        print("\n" + "="*60)
        print("🎮 GENERATED SUMMARY:")
        print("="*60)
        print(summary)
        print("="*60)
        
        if image_data:
            print(f"\n🖼️ GENERATED IMAGE: {len(image_data)} bytes")
            
            # Save the image for inspection
            image_filename = 'test_generated_image.png'
            with open(image_filename, 'wb') as f:
                f.write(image_data)
            print(f"💾 Image saved as '{image_filename}' for inspection")
            
            logger.info("✅ Full generation test completed successfully!")
            return True
        else:
            print("⚠️ No image was generated")
            logger.warning("Image generation failed, but text summary succeeded")
            return False
            
    except Exception as e:
        logger.error(f"❌ Full generation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Steam Digest Image Generation Tests")
    print("="*60)
    
    # Test 1: Image prompt generation (doesn't require API)
    test_image_prompt_generation()
    
    # Test 2: Full generation (requires API key)
    print("\n🔥 Testing with actual Gemini API...")
    success = test_full_generation()
    
    print("\n" + "="*60)
    if success:
        print("✅ All tests passed! Your image generation is ready to go!")
        print("\n📝 Next steps:")
        print("1. Run 'python main.py image' to test with real Steam data")
        print("2. Run 'python main.py' to execute the full digest with images")
        print("3. Check your Discord channel for the posted summary and image")
    else:
        print("❌ Some tests failed. Check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure GEMINI_API_KEY is set correctly")
        print("2. Check your internet connection")
        print("3. Verify the Gemini API key has image generation permissions")
    print("="*60)

if __name__ == "__main__":
    main()
