"""AI summary generation using Google's Gemini API."""

import json
import logging
import os
from typing import Dict
# Import the load_dotenv function
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

logger = logging.getLogger(__name__)

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
        # pip install google-generativeai python-dotenv
        summary = generate_summary(mock_report, GEMINI_API_KEY)
        print("\n--- Generated Summary ---\n")
        print(summary)