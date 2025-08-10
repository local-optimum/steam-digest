# Steam Activity Digest Bot

A lightweight Python application that fetches daily Steam activity for a small group of friends, summarizes the day's gaming session into a short, human-readable update using Google's Gemini AI, and posts that summary to a Discord channel once per day.

## Features

- **Steam Activity Tracking**: Uses Steam Web API to retrieve user activity, games played, and recent playtime
- **Single-Snapshot Management**: Simplified snapshot system using one file for efficient activity comparison
- **AI-Powered Summaries**: Natural language summaries generated using Google's Gemini AI
- **Discord Integration**: Automated posting to Discord via webhooks
- **GitHub Actions Deployment**: Automated daily execution with persistent snapshot caching
- **Optimized Performance**: Focuses on recent activity for more relevant daily digests

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `env.example` to `.env` and fill in your API keys:
   - `STEAM_API_KEY`: Your Steam Web API key
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `DISCORD_WEBHOOK_URL`: Your Discord webhook URL
   - `USERS`: Comma-separated list of `username:steamid64` pairs
4. Test your setup: `python main.py test`
5. Test AI summaries: `python main.py summary`
6. Run full digest: `python main.py`

## Configuration

The application uses environment variables for configuration. See `.env.example` for required variables:
- `STEAM_API_KEY`: Steam Web API key
- `GEMINI_API_KEY`: Google Gemini API key
- `DISCORD_WEBHOOK_URL`: Discord webhook URL
- `USERS`: Comma-separated list of `username:steamid64` pairs (e.g., `alice:76561198000000000,bob:76561198000000001`)

## Deployment

### GitHub Actions (Recommended)

The bot is designed to run automatically via GitHub Actions:

1. **Fork this repository**
2. **Set up GitHub Secrets** in your repository settings:
   - `STEAM_API_KEY`
   - `KLUSTER_API_KEY`
   - `DISCORD_WEBHOOK_URL`
   - `USERS`
3. **Enable GitHub Actions** in your repository
4. **The workflow runs daily at 12:00 BST** (11:00 UTC during BST)
5. **Manual triggers** available via "Actions" tab → "Run workflow"

The GitHub Actions workflow:
- ✅ **Persistent snapshots** via GitHub Actions cache
- ✅ **Automatic daily execution**
- ✅ **Debug logging** for troubleshooting
- ✅ **No server maintenance** required

### Local/Server Deployment

For local testing or server deployment, use cron or similar scheduling:
```bash
# Run daily at noon
0 12 * * * cd /path/to/steam-digest && python main.py
```

## How It Works

### Simplified Snapshot System

The bot uses a single-snapshot approach for maximum reliability:

1. **Load Previous**: Restore `snapshot.json` from cache (empty on first run)
2. **Fetch Current**: Get fresh Steam activity data
3. **Compare & Report**: Generate daily differences and AI summary
4. **Save Current**: Overwrite `snapshot.json` for next run

**First Run**: Reports recent 2-week activity (no baseline to compare)
**Subsequent Runs**: Reports only activity since last run

### Activity Detection

- **Games Played**: Based on `playtime_forever` increases
- **New Games**: Games not in previous snapshot
- **Achievements**: New achievements earned since last run
- **Group Stats**: Co-op sessions, most active player, longest session

## Design Decisions

- **Single Snapshot**: Simplified from complex yesterday/today rotation to single file approach
- **Recent Activity Focus**: Prioritizes recent activity over lifetime totals for relevant daily digests
- **GitHub Actions Native**: Designed specifically for GitHub Actions caching and scheduling
- **Minimal API Usage**: Optimized to reduce unnecessary API calls while maintaining comprehensive tracking
- **Robust Error Handling**: Graceful handling of API failures, missing data, and first-run scenarios

## File Structure

```
steam_digest_bot/
├── main.py                           # Main orchestration
├── fetch.py                          # Steam API integration
├── diff.py                           # Snapshot comparison logic
├── summarise.py                      # AI summary generation
├── send.py                           # Discord webhook posting
├── config.py                         # Configuration loader
├── snapshots/                        # Single snapshot storage
│   └── snapshot.json                 # Current baseline snapshot
├── .github/workflows/daily-digest.yml # GitHub Actions workflow
├── requirements.txt                  # Dependencies
├── .env                             # Environment variables (local)
└── README.md                        # This file
```

## Testing

The bot includes several test modes:

```bash
python main.py test      # Test configuration and APIs
python main.py summary   # Test AI summary generation (no Discord post)
python main.py rotation  # Test snapshot logic
python main.py           # Full digest run
```

## Troubleshooting

### GitHub Actions Issues

- **Check Secrets**: Ensure all required secrets are set in repository settings
- **View Logs**: Check Actions tab for detailed execution logs
- **Cache Issues**: Workflow uses unique cache keys per run to avoid stale data
- **Manual Trigger**: Use "Run workflow" button for immediate testing

### Common Issues

- **No Activity Detected**: Normal if no one played games since last run
- **API Rate Limits**: Steam API has rate limits; bot includes retry logic
- **First Run**: Will show 2-week recent activity instead of daily differences

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes locally: `python main.py test`
4. Commit your changes
5. Push to the branch
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.