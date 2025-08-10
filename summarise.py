"""AI summary generation using Google's Gemini."""

import json
import logging
from typing import Dict
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

logger = logging.getLogger(__name__)

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
    
    # Create a structured summary of the data
    summary_data = {
        'individual_activity': {},
        'group_highlights': {}
    }
    
    # Format individual user activity
    for username, user_data in report['individual_stats'].items():
        if user_data['total_minutes'] > 0:
            summary_data['individual_activity'][username] = {
                'total_minutes': user_data['total_minutes'],
                'games_played': dict(user_data['played']),
                'new_games': user_data['new_games'],
                'first_time_played': user_data['first_time_played']
            }
    
    # Convert to JSON for consistent formatting
    return json.dumps(summary_data, indent=2)

def generate_summary(report: Dict, api_key: str) -> str:
    """Generate a natural language summary using Google's Gemini."""
    if not report['has_activity']:
        return "🎮 No gaming activity detected today. Everyone must be taking a break! 🛋️"
    
    formatted_data = format_report_for_ai(report)
    
    try:
        logger.info("Generating AI summary with Gemini...")
        
        # Configure Gemini client
        genai.configure(api_key=api_key)
        
        # Create the model client
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare the chat
        chat = model.start_chat(history=[])
        
        # Send the prompts
        response = chat.send_message(
            f"{SYSTEM_PROMPT}\n\nHere is today's gaming activity data. Please create a fun Discord-friendly summary:\n\n{formatted_data}",
            generation_config=GenerationConfig(
                temperature=0.7,
                candidate_count=1,
                max_output_tokens=500,
                top_p=1,
                top_k=40
            )
        )
        
        if response.text:
            summary = response.text.strip()
            logger.info("AI summary generated successfully")
            return summary
        else:
            logger.error("No response text returned from Gemini")
            return generate_fallback_summary(report)
            
    except Exception as e:
        logger.error(f"Error generating AI summary: {e}")
        return generate_fallback_summary(report)

def generate_fallback_summary(report: Dict) -> str:
    """Generate a basic fallback summary when AI fails."""
    if not report['has_activity']:
        return "🎮 No gaming activity detected today."
    
    parts = ["🎮 **Daily Gaming Digest**"]
    
    # Individual activity
    individual_stats = report['individual_stats']
    active_users = [user for user, data in individual_stats.items() if data['total_minutes'] > 0]
    
    if active_users:
        parts.append(f"\n**Active Players:** {', '.join(active_users)}")
    
    # Group stats
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
    
    # Add new games and first time played games
    for username, user_data in individual_stats.items():
        if user_data['new_games']:
            parts.append(f"**{username}'s New Games:** {', '.join(user_data['new_games'])}")
        if user_data['first_time_played']:
            parts.append(f"**{username} Tried for First Time:** {', '.join(user_data['first_time_played'])}")
    
    return "\n".join(parts) 
