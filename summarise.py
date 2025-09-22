"""AI summary generation using Google's Gemini API."""

import json
import logging
import os
import requests
import base64
from typing import Dict, Optional, Tuple
# Import the load_dotenv function
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

logger = logging.getLogger(__name__)

# Character descriptions for image generation
CHARACTER_DESCRIPTIONS = {
    "DonkFresh": "a young skinny guy with a heavy metal t-shirt and long curly hair",
    "BoxFresh": "a muscular British guy who wears cargo joggers and has a short beard", 
    "ViralNinja": "a big British guy with a gamer hoodie and glasses",
    "GoplanaQueen": "a busty Polish woman with blonde hair"
}

# The system prompt remains the same, it's excellent!
SYSTEM_PROMPT = """You are a top gaming streamer that summarizes daily gaming activity for a group of sigma friends. 
Your summaries should be:
- Discord-friendly (under 2000 characters)
- Casual and fun in tone
- Tailored to the specific games being played
- Include gaming emojis where appropriate
- Highlight interesting patterns or achievements
- Mention and celebrate collaborative gaming when it happens
- Keep it concise but engaging

Focus on the most interesting aspects of the day's gaming session."""

def format_report_for_ai(report: Dict) -> str:
    """Format the daily report data for AI processing."""
    if not report['has_activity']:
        return "No gaming activity detected for today."
    
    # This function is perfect as is.
    summary_data = {
        'individual_activity': {},
        'group_highlights': {}
    }
    
    for username, user_data in report['individual_stats'].items():
        if user_data['total_minutes'] > 0:
            summary_data['individual_activity'][username] = {
                'total_minutes': user_data['total_minutes'],
                'games_played': dict(user_data['played']),
                'new_games': user_data['new_games'],
                'first_time_played': user_data['first_time_played']
            }
    
    return json.dumps(summary_data, indent=2)

def generate_summary(report: Dict, api_key: str) -> str:
    """Generate a natural language summary using Google's Gemini API."""
    if not report['has_activity']:
        return "🎮 No gaming activity detected today. Everyone must be taking a break! 🛋️"
    
    if not api_key:
        logger.error("Gemini API key is missing.")
        return generate_fallback_summary(report)

    formatted_data = format_report_for_ai(report)
    
    try:
        logger.info("Generating AI summary with Gemini...")
        
        # Configure the Gemini client with your API key
        genai.configure(api_key=api_key)
        
        # Set up the model with the system prompt and generation config
        # Using gemini-1.5-flash-latest is a great choice for speed and cost-effectiveness
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash-latest',
            system_instruction=SYSTEM_PROMPT,
        )
        
        generation_config = GenerationConfig(
            temperature=0.7,
            max_output_tokens=500,
            top_p=0.9,
        )

        # The user-facing prompt now only needs to contain the data
        prompt = f"Here is today's gaming activity data. Please create a fun Discord-friendly summary:\n\n{formatted_data}"
        
        # Generate the content
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        if response.text:
            summary = response.text.strip()
            logger.info("AI summary generated successfully")
            return summary
        else:
            # This case might happen if the response was blocked due to safety settings
            logger.error(f"No response text returned from Gemini. Response: {response}")
            return generate_fallback_summary(report)
            
    except Exception as e:
        logger.error(f"Error generating AI summary with Gemini: {e}")
        return generate_fallback_summary(report)


def generate_fallback_summary(report: Dict) -> str:
    """Generate a basic fallback summary when AI fails. This function is unchanged."""
    if not report['has_activity']:
        return "🎮 No gaming activity detected today."
    
    parts = ["🎮 **Daily Gaming Digest**"]
    
    individual_stats = report['individual_stats']
    active_users = [user for user, data in individual_stats.items() if data['total_minutes'] > 0]
    
    if active_users:
        parts.append(f"\n**Active Players:** {', '.join(active_users)}")
    
    group_stats = report['group_stats']
    
    if group_stats['total_group_minutes'] > 0:
        hours = group_stats['total_group_minutes'] // 60
        minutes = group_stats['total_group_minutes'] % 60
        time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        parts.append(f"**Total Group Time:** {time_str}")
    
    if group_stats['most_played_game']:
        game = group_stats['most_played_game']
        parts.append(f"**Most Played:** {game['name']}")
    
    if group_stats['games_played_together']:
        coop_games = [game['name'] for game in group_stats['games_played_together']]
        parts.append(f"**Co-op Games:** {', '.join(coop_games)}")
    
    for username, user_data in individual_stats.items():
        if user_data['new_games']:
            parts.append(f"**{username}'s New Games:** {', '.join(user_data['new_games'])}")
        if user_data['first_time_played']:
            parts.append(f"**{username} Tried for First Time:** {', '.join(user_data['first_time_played'])}")
    
    return "\n".join(parts)

def create_image_prompt(text_summary: str, report: Dict) -> str:
    """Create an image generation prompt based on the text summary and activity data."""
    
    # Build character descriptions for active players
    character_descriptions = []
    for player, data in report['individual_stats'].items():
        if data['total_minutes'] > 0 and player in CHARACTER_DESCRIPTIONS:
            character_descriptions.append(f"{player} is {CHARACTER_DESCRIPTIONS[player]}")
    
    # Create game-specific scenes based on who played what
    game_scenes = []
    for player, data in report['individual_stats'].items():
        if data['total_minutes'] > 0:
            for game, minutes in data['played'].items():
                game_scenes.append(f"{player} in {game}")
    
    # Check for collaborative gaming scenes
    group_scenes = []
    if report['group_stats']['games_played_together']:
        for game_info in report['group_stats']['games_played_together']:
            # Find who played this game
            players_in_game = []
            for player, data in report['individual_stats'].items():
                if game_info['name'] in data['played']:
                    players_in_game.append(player)
            if len(players_in_game) > 1:
                group_scenes.append(f"{', '.join(players_in_game)} together in {game_info['name']}")
    
    # Build the image prompt
    prompt_parts = [
        "Create an epic action movie montage showing multiple cinematic scenes based on the games being played:",
        ""
    ]
    
    # Add character descriptions
    if character_descriptions:
        prompt_parts.extend([
            "Characters:",
            *[f"- {desc}" for desc in character_descriptions],
            ""
        ])
    
    # Add individual game scenes
    if game_scenes:
        prompt_parts.extend([
            "Action Scenes to Include:",
            *[f"- Epic scene: {scene}, showing the character as a heroic legend in that game's world" for scene in game_scenes[:6]],  # Limit to avoid overly long prompts
            ""
        ])
    
    # Highlight collaborative scenes
    if group_scenes:
        prompt_parts.extend([
            "Team-Up Scenes:",
            *[f"- {scene}, working as legendary heroes with perfect coordination" for scene in group_scenes],
            ""
        ])
    
    # Style instructions
    prompt_parts.extend([
        "Style: Action movie montage with multiple dynamic scenes, cinematic lighting, and heroic poses.",
        "Each scene should authentically represent the specific game world with recognizable elements, environments, and visual style.",
        "Show the characters as cool, heroic versions of themselves, maintaining their friendship while looking legendary.",
        "Use dramatic lighting, particle effects, and dynamic composition to make each scene feel epic and larger-than-life.",
        "The overall mood: friends who are legendary heroes having the ultimate gaming adventure across multiple worlds."
    ])
    
    return "\n".join(prompt_parts)

def generate_image_with_gemini(prompt: str, api_key: str) -> Optional[bytes]:
    """Generate an image using Gemini 2.5 Flash Image Preview API."""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Generate an image based on this prompt: {prompt}"
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
            "responseModalities": ["IMAGE"]
        }
    }
    
    try:
        logger.info("Generating image with Gemini 2.0 Flash...")
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        
        # Check if we got a successful response with image data
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                for part in candidate['content']['parts']:
                    if 'inlineData' in part and 'data' in part['inlineData']:
                        # The image is base64 encoded
                        image_data = base64.b64decode(part['inlineData']['data'])
                        logger.info("Successfully generated image")
                        return image_data
        
        logger.error(f"No image data found in response: {result}")
        return None
        
    except requests.RequestException as e:
        logger.error(f"Error generating image with Gemini: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response text: {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error generating image: {e}")
        return None

def generate_summary_with_image(report: Dict, gemini_api_key: str) -> Tuple[str, Optional[bytes]]:
    """Generate both text summary and image for the gaming report."""
    
    # First generate the text summary
    text_summary = generate_summary(report, gemini_api_key)
    
    # Then generate an image based on the summary and report data
    image_prompt = create_image_prompt(text_summary, report)
    logger.info(f"Generated image prompt: {image_prompt}")
    
    image_data = generate_image_with_gemini(image_prompt, gemini_api_key)
    
    return text_summary, image_data

# Example of how to run it:
if __name__ == '__main__':
    # Load environment variables from .env file
    load_dotenv()
    
    logging.basicConfig(level=logging.INFO)
    
    # Get the Gemini API key from environment variables
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not found in .env file or environment variables.")
    else:
        # A mock report for testing purposes
        mock_report = {
            'has_activity': True,
            'individual_stats': {
                'PlayerOne': {'total_minutes': 125, 'played': {'Helldivers 2': 90, 'Lethal Company': 35}, 'new_games': [], 'first_time_played': []},
                'PlayerTwo': {'total_minutes': 90, 'played': {'Helldivers 2': 90}, 'new_games': ['Helldivers 2'], 'first_time_played': ['Helldivers 2']},
                'PlayerThree': {'total_minutes': 0, 'played': {}, 'new_games': [], 'first_time_played': []}
            },
            'group_stats': {
                'total_group_minutes': 215,
                'most_played_game': {'name': 'Helldivers 2', 'minutes': 180},
                'games_played_together': [{'name': 'Helldivers 2', 'minutes': 180}]
            }
        }
        
        # Make sure you have the required libraries installed:
        # pip install google-generativeai python-dotenv requests
        
        # Test both summary and image generation
        print("Testing text summary generation...")
        summary = generate_summary(mock_report, GEMINI_API_KEY)
        print("\n--- Generated Summary ---\n")
        print(summary)
        
        print("\nTesting text summary + image generation...")
        summary_with_image, image_data = generate_summary_with_image(mock_report, GEMINI_API_KEY)
        print("\n--- Generated Summary with Image ---\n")
        print(summary_with_image)
        
        if image_data:
            print(f"\n--- Generated Image ---")
            print(f"Image data: {len(image_data)} bytes")
            # Save the image for inspection
            with open('test_image.png', 'wb') as f:
                f.write(image_data)
            print("Image saved as 'test_image.png'")
        else:
            print("No image was generated")