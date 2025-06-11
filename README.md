# Steam Activity Digest Bot

A lightweight Python application that fetches daily Steam activity for a small group of friends, summarizes the day's gaming session into a short, human-readable update using AI via Kluster.ai (OpenRouter), and posts that summary to a Discord channel once per day.

## Features

- **Steam Activity Tracking**: Uses Steam Web API to retrieve user activity, games played, playtime, and achievements
- **Snapshot Management**: Daily snapshots stored as JSON files for comparison
- **AI-Powered Summaries**: Natural language summaries generated via Kluster.ai through OpenRouter
- **Discord Integration**: Automated posting to Discord via webhooks
- **Cloud Deployment**: Designed to run on Render as a scheduled job

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `env.example` to `.env` and fill in your API keys
4. Test your setup: `python main.py test`
5. Test AI summaries: `python main.py summary`
6. Run full digest: `python main.py`

## Configuration

See `.env.example` for required environment variables:
- Steam API key
- Kluster.ai API key via OpenRouter
- Discord webhook URL
- User Steam IDs

## File Structure

```
steam_digest_bot/
├── main.py            # Main orchestration
├── fetch.py           # Steam API integration
├── diff.py            # Snapshot comparison logic
├── summarise.py       # AI summary generation
├── send.py            # Discord webhook posting
├── config.py          # Configuration loader
├── snapshots/         # Daily snapshot storage
├── requirements.txt   # Dependencies
└── .env              # Environment variables
```