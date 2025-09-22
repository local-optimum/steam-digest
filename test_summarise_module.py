#!/usr/bin/env python3
"""
Test script for the summarise module end-to-end functionality.

This script tests the core summarise module functions with mock data
to verify text summary and image generation work correctly.

Usage:
    python test_summarise_module.py

Prerequisites:
    - GEMINI_API_KEY set in environment or .env file
    - All dependencies installed (see requirements.txt)
"""

import logging
import os
from dotenv import load_dotenv
from summarise import generate_summary, generate_summary_with_image

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_mock_report():
    """Create a mock report for testing purposes."""
    return {
        'has_activity': True,
        'individual_stats': {
            'PlayerOne': {
                'total_minutes': 125, 
                'played': {'Helldivers 2': 90, 'Lethal Company': 35}, 
                'new_games': [], 
                'first_time_played': []
            },
            'PlayerTwo': {
                'total_minutes': 90, 
                'played': {'Helldivers 2': 90}, 
                'new_games': ['Helldivers 2'], 
                'first_time_played': ['Helldivers 2']
            },
            'PlayerThree': {
                'total_minutes': 0, 
                'played': {}, 
                'new_games': [], 
                'first_time_played': []
            }
        },
        'group_stats': {
            'total_group_minutes': 215,
            'most_played_game': {'name': 'Helldivers 2', 'minutes': 180},
            'games_played_together': [{'name': 'Helldivers 2', 'minutes': 180}]
        }
    }

def test_text_summary():
    """Test text summary generation only."""
    logger.info("Testing text summary generation...")
    
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        logger.error("GEMINI_API_KEY not found in environment variables!")
        return False
    
    mock_report = create_mock_report()
    
    try:
        summary = generate_summary(mock_report, gemini_api_key)
        
        print("\n" + "="*60)
        print("📝 GENERATED TEXT SUMMARY:")
        print("="*60)
        print(summary)
        print("="*60)
        
        logger.info("✅ Text summary test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Text summary test failed: {e}")
        return False

def test_summary_with_image():
    """Test both text summary and image generation."""
    logger.info("Testing text summary + image generation...")
    
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        logger.error("GEMINI_API_KEY not found in environment variables!")
        return False
    
    mock_report = create_mock_report()
    
    try:
        summary_with_image, image_data = generate_summary_with_image(mock_report, gemini_api_key)
        
        print("\n" + "="*60)
        print("🎮 GENERATED SUMMARY WITH IMAGE:")
        print("="*60)
        print(summary_with_image)
        print("="*60)
        
        if image_data:
            print(f"\n🖼️ GENERATED IMAGE: {len(image_data)} bytes")
            # Save the image for inspection
            image_filename = 'test_module_image.png'
            with open(image_filename, 'wb') as f:
                f.write(image_data)
            print(f"💾 Image saved as '{image_filename}' for inspection")
            
            logger.info("✅ Summary + image test completed successfully!")
            return True
        else:
            print("⚠️ No image was generated")
            logger.warning("Image generation failed, but text summary succeeded")
            return False
            
    except Exception as e:
        logger.error(f"❌ Summary + image test failed: {e}")
        return False

def main():
    """Run the summarise module tests."""
    print("🧪 Testing Summarise Module End-to-End")
    print("="*60)
    
    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not found in environment variables!")
        print("Please set your GEMINI_API_KEY in your .env file or environment")
        return
    
    # Test 1: Text summary only
    text_success = test_text_summary()
    
    # Test 2: Summary with image
    print("\n🎨 Testing with image generation...")
    image_success = test_summary_with_image()
    
    print("\n" + "="*60)
    if text_success and image_success:
        print("✅ All summarise module tests passed!")
        print("\n📝 The summarise module is working correctly:")
        print("- Text summary generation: ✅")
        print("- Image generation: ✅")
        print("- End-to-end flow: ✅")
    else:
        print("❌ Some tests failed:")
        print(f"- Text summary: {'✅' if text_success else '❌'}")
        print(f"- Image generation: {'✅' if image_success else '❌'}")
    print("="*60)

if __name__ == "__main__":
    main()
