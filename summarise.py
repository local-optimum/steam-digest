"""AI summary generation using Kluster.ai."""

import json
import logging
from typing import Dict
from openai import OpenAI

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
        'group_highlights': report['group_stats']
    }
    
    # Format individual user activity
    for username, user_data in report['individual_stats'].items():
        if user_data['total_minutes'] > 0:
            summary_data['individual_activity'][username] = {
                'total_minutes': user_data['total_minutes'],
                'games_played': dict(user_data['played']),
                'achievements_earned': user_data['achievements'],
                'new_games': user_data['new_games'],
                'games_count': user_data['games_played']
            }
    
    return json.dumps(summary_data, indent=2)

def generate_summary(report: Dict, api_key: str) -> str:
    """Generate a natural language summary using Kluster.ai."""
    if not report['has_activity']:
        return "🎮 No gaming activity detected today. Everyone must be taking a break! 🛋️"
    
    formatted_data = format_report_for_ai(report)
    
    try:
        logger.info("Generating AI summary with Kluster.ai...")
        
        # Configure Kluster.ai client
        client = OpenAI(
            base_url="https://api.kluster.ai/v1", 
            api_key=api_key
        )
        
        chat_completion = client.chat.completions.create(
            model="klusterai/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Here is today's gaming activity data. Please create a fun Discord-friendly summary:\n\n{formatted_data}"}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        if chat_completion.choices and len(chat_completion.choices) > 0:
            summary = chat_completion.choices[0].message.content.strip()
            logger.info("AI summary generated successfully")
            return summary
        else:
            logger.error("No choices returned from Kluster.ai")
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
    
    if group_stats['total_achievements'] > 0:
        parts.append(f"**Achievements Unlocked:** {group_stats['total_achievements']}")
    
    if group_stats['new_games_discovered']:
        parts.append(f"**New Games Tried:** {', '.join(group_stats['new_games_discovered'])}")
    
    return "\n".join(parts) 
