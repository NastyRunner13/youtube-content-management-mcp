from server import mcp
from mcp.types import TextContent
from typing import List
from utils.tool_utils import YouTubeAPIError, get_youtube_client
from googleapiclient.errors import HttpError
from utils.models import PlaylistIdInput

@mcp.tool()
def get_playlist_metrics(arguments: dict) -> List[TextContent]:
    """Retrieve statistics for a specific YouTube playlist.

    This function queries the YouTube Data API v3 to fetch metrics for a given playlist,
    including item count and total view count of all videos, formatted as a TextContent object.

    Args:
        arguments: A dictionary containing:
            - playlist_id (str): The YouTube playlist ID (required).

    Returns:
        List[TextContent]: A list containing a single TextContent object with a formatted string
            including the playlist's title, item count, and total view count. If the playlist
            is not found, returns a single TextContent with a "No playlist found" message.

    Raises:
        YouTubeAPIError: If the API key is missing, the playlist ID is invalid, the API request fails,
            or the input arguments are invalid (via Pydantic).
    """
    try:
        input_data = PlaylistIdInput(**arguments)
    except ValueError as e:
        raise YouTubeAPIError(f"Invalid input arguments: {e}")

    youtube = get_youtube_client()

    try:
        playlist_response = youtube.playlists().list(
            part='snippet',
            id=input_data.playlist_id
        ).execute()

        playlist_items = playlist_response.get('items', [])
        if not playlist_items:
            return [TextContent(type="text", text="No playlist found for the given ID.")]

        playlist_title = playlist_items[0]['snippet']['title']

        playlist_items_response = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=input_data.playlist_id,
            maxResults=50
        ).execute()

        video_ids = [item['contentDetails']['videoId'] for item in playlist_items_response.get('items', [])]
        item_count = len(video_ids)

        total_views = 0
        if video_ids:
            videos_response = youtube.videos().list(
                part='statistics',
                id=','.join(video_ids)
            ).execute()
            total_views = sum(int(item['statistics'].get('viewCount', 0)) for item in videos_response.get('items', []))

        return [TextContent(
            type="text",
            text=(f"**{playlist_title}**\n"
                  f"Playlist ID: {input_data.playlist_id}\n"
                  f"Items: {item_count}\n"
                  f"Total Views: {total_views}")
        )]

    except HttpError as e:
        raise YouTubeAPIError(f"YouTube API error for playlist ID '{input_data.playlist_id}': {e}")
    except Exception as e:
        raise YouTubeAPIError(f"Unexpected error for playlist ID '{input_data.playlist_id}': {e}")