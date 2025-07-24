from server import mcp
from mcp.types import TextContent
from typing import List
from utils.tool_utils import YouTubeAPIError, get_youtube_client
from googleapiclient.errors import HttpError
from utils.models import SearchPlaylistsInput

@mcp.tool()
def search_playlists(arguments: dict) -> List[TextContent]:
    """Search YouTube for playlists based on a query.

    This function queries the YouTube Data API v3 to retrieve playlists matching the provided
    search query. Each result includes the playlist title, ID, creation date, and description,
    formatted as a single TextContent object.

    Args:
        arguments: A dictionary containing search parameters:
            - query (str): The search query (required).
            - max_results (int, optional): Maximum number of results (1 to 50). Defaults to 25.
            - published_after (str, optional): RFC 3339 timestamp (e.g., '2023-01-01T00:00:00Z') to filter playlists created after this date.

    Returns:
        List[TextContent]: A list containing a single TextContent object with a formatted string
            listing all found playlists, including their title, playlist ID, creation date, and
            truncated description. If no playlists are found, returns a single TextContent with a
            "No playlists found" message.

    Raises:
        YouTubeAPIError: If the API key is missing, the API request fails, or the input arguments are invalid (via Pydantic).
    """
    try:
        input_data = SearchPlaylistsInput(**arguments)
    except ValueError as e:
        raise YouTubeAPIError(f"Invalid input arguments: {e}")

    youtube = get_youtube_client()

    try:
        search_params = {
            'part': 'snippet',
            'q': input_data.query,
            'type': 'playlist',
            'maxResults': input_data.max_results
        }

        if input_data.published_after:
            search_params['publishedAfter'] = input_data.published_after

        search_response = youtube.search().list(**search_params).execute()

        playlists = []
        for item in search_response.get('items', []):
            playlist_info = {
                'playlist_id': item['id']['playlistId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'][:200] + ('...' if item['snippet']['description'] else ''),
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
                              f"Created: {p['published_at']}\n"
                              f"Description: {p['description']}"
                              for p in playlists])
        )]

    except HttpError as e:
        raise YouTubeAPIError(f"YouTube API error for query '{input_data.query}': {e}")
    except Exception as e:
        raise YouTubeAPIError(f"Unexpected error for query '{input_data.query}': {e}")