﻿# YouTube Content Management MCP Server

A Model Context Protocol (MCP) server that provides YouTube Data API v3 integration for content discovery and analytics. This server enables AI assistants to search for YouTube videos, channels, playlists, and retrieve detailed metrics for videos, channels, and playlists.

## Features

### Current Tools

- **🎥 search_videos**: Search YouTube for videos with advanced filtering options, including view count, like count, and comment count.
- **📺 search_channels**: Find YouTube channels based on search queries, including subscriber count, video count, and total view count.
- **📋 search_playlists**: Search YouTube for playlists based on search queries.
- **📊 get_video_metrics**: Retrieve statistics (views, likes, comments) for a specific video by ID.
- **📈 get_channel_metrics**: Retrieve statistics (subscribers, total views, video count) for a specific channel by ID.
- **📑 get_playlist_metrics**: Retrieve statistics (item count, total views) for a specific playlist by ID.

### Planned Features

- Playlist creation and management
- Comment retrieval and analysis
- Video upload and management (with proper authentication)
- Trending videos by region
- Video transcription access

## Prerequisites

- Python 3.8 or higher
- YouTube Data API v3 key
- VSCode with MCP extension (for VSCode usage)
- Required Python packages: `google-api-python-client`, `python-dotenv`, `pydantic`

## Getting Your YouTube API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3:
   - Navigate to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click on it and press "Enable"
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the generated API key
5. (Recommended) Restrict the API key:
   - Click on the API key to edit it
   - Under "API restrictions", select "Restrict key"
   - Choose "YouTube Data API v3"
   - Save the changes

## Installation

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/NastyRunner13/youtube-content-management-mcp
   cd youtube-content-management-mcp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or if using `uv`:
   ```bash
   uv install
   ```

3. **Set up your environment** (Optional)
   Create a `.env` file in the project root:
   ```env
   YOUTUBE_API_KEY=your_youtube_api_key_here
   ```

## Usage

### With VSCode (Recommended)

1. **Install the MCP extension** in VSCode

2. **Configure the MCP server** by adding this to your VSCode `settings.json`:

   ```json
   {
     "mcp.servers": {
       "youtube-content-management": {
         "command": "python",
         "args": [
           "/path/to/youtube-content-management-mcp/main.py"
         ],
         "env": {
           "YOUTUBE_API_KEY": "your_youtube_api_key_here"
         }
       }
     }
   }
   ```

   **Alternative using uv:**
   ```json
   {
     "mcp.servers": {
       "youtube-content-management": {
         "command": "uv",
         "args": [
           "--directory",
           "/path/to/youtube-content-management-mcp",
           "run",
           "main.py"
         ],
         "env": {
           "YOUTUBE_API_KEY": "your_youtube_api_key_here"
         }
       }
     }
   }
   ```

3. **Restart VSCode** or reload the window

4. **Use the tools** through the MCP panel or by asking your AI assistant

### With Claude Desktop

Add this configuration to your Claude Desktop config file:

**Windows:** `%APPDATA%/Claude/claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "youtube-content-management": {
      "command": "python",
      "args": ["/path/to/youtube-content-management-mcp/main.py"],
      "env": {
        "YOUTUBE_API_KEY": "your_youtube_api_key_here"
      }
    }
  }
}
```

### With Other MCP Clients

The server implements the standard MCP protocol and should work with any compatible MCP client. Refer to your client's documentation for configuration instructions.

## Available Tools

### search_videos

Search YouTube for videos with advanced filtering options, including metrics like view count, like count, and comment count.

**Parameters:**
- `query` (string, required): Search query
- `max_results` (integer, optional): Maximum number of results (1-50, default: 25)
- `order` (string, optional): Sort order - "relevance", "date", "rating", "viewCount" (default: "relevance")
- `duration` (string, optional): Video duration - "medium", "long" (default: "medium")
- `published_after` (string, optional): RFC 3339 timestamp (e.g., "2023-01-01T00:00:00Z")

**Example usage:**
```
Search for Python tutorials uploaded in the last year, sorted by view count
```

### search_channels

Find YouTube channels based on search queries, including metrics like subscriber count, video count, and total view count.

**Parameters:**
- `query` (string, required): Search query for channels
- `max_results` (integer, optional): Maximum number of results (1-50, default: 25)
- `published_after` (string, optional): RFC 3339 timestamp (e.g., "2023-01-01T00:00:00Z")

**Example usage:**
```
Find coding tutorial channels
```

### search_playlists

Search YouTube for playlists based on search queries.

**Parameters:**
- `query` (string, required): Search query for playlists
- `max_results` (integer, optional): Maximum number of results (1-50, default: 25)
- `published_after` (string, optional): RFC 3339 timestamp (e.g., "2023-01-01T00:00:00Z")

**Example usage:**
```
Find playlists about machine learning
```

### get_video_metrics

Retrieve statistics for a specific YouTube video, including view count, like count, and comment count.

**Parameters:**
- `video_id` (string, required): The YouTube video ID

**Example usage:**
```
Get metrics for the video with ID dQw4w9WgXcQ
```

### get_channel_metrics

Retrieve statistics for a specific YouTube channel, including subscriber count, total view count, and video count.

**Parameters:**
- `channel_id` (string, required): The YouTube channel ID

**Example usage:**
```
Get metrics for the channel with ID UC_x5XG1OV2P6uZZ5FSM9Ttw
```

### get_playlist_metrics

Retrieve statistics for a specific YouTube playlist, including item count and total view count of all videos.

**Parameters:**
- `playlist_id` (string, required): The YouTube playlist ID

**Example usage:**
```
Get metrics for the playlist with ID PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU
```

## Example Interactions

Once the MCP server is configured, you can interact with it through your AI assistant:

**Video Search with Metrics:**
> "Search for machine learning tutorials from the last 6 months, sorted by view count, and show view counts"

**Channel Discovery with Metrics:**
> "Find top cooking channels on YouTube with their subscriber counts"

**Playlist Search:**
> "Show me playlists about Python programming"

**Video Metrics:**
> "Get the view count and like count for the video with ID dQw4w9WgXcQ"

**Channel Metrics:**
> "What are the subscriber count and total views for the channel UC_x5XG1OV2P6uZZ5FSM9Ttw?"

**Playlist Metrics:**
> "How many videos and total views are in the playlist PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU?"

## Input Validation

All tools use [Pydantic](https://pydantic-docs.helpmanual.io/) for robust input validation, ensuring:
- Required fields (e.g., `query`, `video_id`) are provided and non-empty.
- Numeric fields (e.g., `max_results`) are within valid ranges (1-50).
- String fields (e.g., `order`, `duration`) match allowed values.
- Timestamps (e.g., `published_after`) follow RFC 3339 format.

Invalid inputs result in clear error messages, improving reliability and user experience.

## Security Notes

- **Never commit your API key** to version control
- Consider using environment variables instead of hardcoding API keys
- Regularly rotate your API keys
- Monitor your API usage in Google Cloud Console
- Set up API key restrictions to limit usage to YouTube Data API v3

## Troubleshooting

### Common Issues

1. **"YouTube API key is not set"**
   - Ensure your API key is properly configured in the environment variables
   - Check that the key is valid and has YouTube Data API v3 enabled

2. **"quotaExceeded" errors**
   - You've hit your daily API quota limit (default: 10,000 units)
   - Wait until the quota resets (daily) or increase your quota in Google Cloud Console
   - Note: Metrics tools and search tools with metrics may consume more quota due to multiple API calls

3. **"keyInvalid" errors**
   - Your API key is invalid or has been revoked
   - Generate a new API key and update your configuration

4. **"Invalid input arguments" errors**
   - Check the Pydantic error message for details (e.g., missing `query`, invalid `order`)
   - Ensure inputs match the tool's parameter requirements

5. **MCP server not starting**
   - Check that all dependencies (`google-api-python-client`, `python-dotenv`, `pydantic`) are installed
   - Verify the Python path in your configuration is correct
   - Check the MCP extension logs for detailed error messages

### Debug Mode

To enable debug logging, add this to your environment:
```json
"env": {
  "YOUTUBE_API_KEY": "your_key_here",
  "DEBUG": "true"
}
```

## Contributing

We welcome contributions! Areas where you can help:
- Additional YouTube API endpoints (comments, transcriptions)
- Optimizing API quota usage (e.g., batching metrics calls)
- Enhancing Pydantic validation rules
- Performance optimizations
- Documentation improvements
- Testing and bug reports

## API Limits

- **YouTube Data API v3**: 10,000 units per day (default)
- **Search operations**: 100 units per request
- **List operations (videos, channels, playlists)**: 1 unit per request
- **Playlist items**: 5 units per request
- **Rate limiting**: Be mindful of making too many requests in quick succession, especially with metrics tools

## Support

- Create an issue for bugs or feature requests
- Check the [YouTube Data API documentation](https://developers.google.com/youtube/v3) for API-specific questions
- Review MCP protocol documentation for integration issues
- Refer to [Pydantic documentation](https://pydantic-docs.helpmanual.io/) for validation-related questions