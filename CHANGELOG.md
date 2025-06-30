# Changelog

All notable changes to the Steam Activity Digest Bot project will be documented in this file.

## [Unreleased]

### Added
- Initial project setup with core functionality
- Steam API integration for activity tracking
- AI-powered summary generation via Kluster.ai (OpenRouter)
- Discord webhook integration
- Snapshot-based activity tracking system

### Changed
- Optimized activity tracking to focus on recent activity rather than lifetime totals
- Improved performance by reducing unnecessary API calls
- Enhanced daily digest relevance by focusing on current session data
- Removed achievement tracking to significantly improve performance and reliability
- Optimized API calls to only fetch essential game data
- Updated diff calculation to better handle new games vs first-time plays
- Improved error handling and logging

### Fixed
- Achievement fetching issues for games
- Snapshot comparison logic for more accurate activity tracking
- Environment variable handling and validation

## [0.1.0] - 2024-03-XX

### Added
- Basic project structure
- Core functionality for Steam activity tracking
- AI summary generation
- Discord integration
- Snapshot management system 