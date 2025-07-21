from server import mcp
from mcp.types import TextContent
from typing import List
from utils import YouTubeAPIError, get_youtube_client
from googleapiclient.errors import HttpError
import re

@mcp.tool()
def search_playlists(arguments: dict) -> List[TextContent]:
    """Search YouTube for playlists based on a query and optional filters.

    This function queries the YouTube Data API v3 to retrieve playlists matching the provided
    search criteria. Each result includes the playlist title, ID, channel, creation date, and
    a truncated description, formatted as a single TextContent object.

    Args:
        arguments: A dictionary containing search parameters:
            - query (str): The search query (required).
            - max_results (int, optional): Maximum number of results (1 to 50). Defaults to 25.
            - published_after (str, optional): RFC 3339 timestamp (e.g., '2023-01-01T00:00:00Z') to filter playlists created after this date.

    Returns:
        List[TextContent]: A list containing a single TextContent object with a formatted string
            listing all found playlists, including their title, playlist ID, channel, creation date,
            and truncated description. If no playlists are found, returns a single TextContent with
            a "No playlists found" message.

    Raises:
        YouTubeAPIError: If the API key is missing, the API request fails, or an unexpected error occurs.
    """
    youtube = get_youtube_client()

    try:
        query = arguments.get("query", "")
        max_results = min(arguments.get("max_results", 25), 50)
        published_after = arguments.get("published_after", None)

        # Validate published_after format if provided
        if published_after and not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', published_after):
            raise ValueError(f"Invalid published_after format: {published_after}. Must be RFC 3339 (e.g., 2023-01-01T00:00:00Z)")

        search_params = {
            'part': 'snippet',
            'q': query,
            'type': 'playlist',
            'maxResults': max_results
        }

        if published_after:
            search_params['publishedAfter'] = published_after

        response = youtube.search().list(**search_params).execute()

        playlists = []
        for item in response.get('items', []):
            playlist_info = {
                'playlist_id': item['id']['playlistId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'][:200] + ('...' if item['snippet']['description'] else ''),
                'channel_title': item['snippet']['channelTitle'],
                'published_at': item['snippet']['publishedAt']
            }
            playlists.append(playlist_info)

        if not playlists:
            return [TextContent(type="text", text="No playlists found.")]

        return [TextContent(
            type="text",
            text=f"Found {len(playlists)} playlists:\n\n" +
                 "\n\n".join([f"**{p['title']}**\n"
                              f"Playlist ID: {p['playlist_id']}\n"
                              f"Channel: {p['channel_title']}\n"
                              f"Created: {p['published_at']}\n"
                              f"Description: {p['description']}"
                              for p in playlists])
        )]

    except HttpError as e:
        raise YouTubeAPIError(f"YouTube API error for query '{query}': {e}")
    except Exception as e:
        raise YouTubeAPIError(f"Unexpected error for query '{query}': {e}")