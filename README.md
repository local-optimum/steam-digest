# Steam Activity Digest Bot

A lightweight Python application that fetches daily Steam activity for a small group of friends, summarizes the day's gaming session into a short, human-readable update using AI via Kluster.ai (OpenRouter), and posts that summary to a Discord channel once per day.

## Features

- **Steam Activity Tracking**: Uses Steam Web API to retrieve user activity, games played, and recent playtime
- **Snapshot Management**: Daily snapshots stored as JSON files for efficient activity comparison
- **AI-Powered Summaries**: Natural language summaries generated via Kluster.ai through OpenRouter
- **Discord Integration**: Automated posting to Discord via webhooks
- **Cloud Deployment**: Designed to run on Render as a scheduled job
- **Optimized Performance**: Focuses on recent activity for more relevant daily digests

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `env.example` to `.env` and fill in your API keys:
   - `STEAM_API_KEY`: Your Steam Web API key
   - `OPENROUTER_API_KEY`: Your Kluster.ai API key via OpenRouter
   - `DISCORD_WEBHOOK_URL`: Your Discord webhook URL
   - `STEAM_USER_IDS`: Comma-separated list of Steam user IDs to track
4. Test your setup: `python main.py test`
5. Test AI summaries: `python main.py summary`
6. Run full digest: `python main.py`

## Configuration

The application uses environment variables for configuration. See `.env.example` for required variables:
- `STEAM_API_KEY`: Steam Web API key
- `OPENROUTER_API_KEY`: Kluster.ai API key via OpenRouter
- `DISCORD_WEBHOOK_URL`: Discord webhook URL
- `STEAM_USER_IDS`: Comma-separated list of Steam user IDs to track

## Design Decisions

- **Recent Activity Focus**: The bot prioritizes recent activity over lifetime totals for more relevant daily digests
- **Snapshot System**: Uses daily snapshots to efficiently track changes in activity
- **Minimal API Usage**: Optimized to reduce unnecessary API calls while maintaining comprehensive tracking
- **Error Handling**: Robust error handling for API failures and missing data

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
├── .env              # Environment variables
└── CHANGELOG.md      # Project changelog
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.