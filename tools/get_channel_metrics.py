from server import mcp
from mcp.types import TextContent
from typing import List
from utils import YouTubeAPIError, get_youtube_client
from googleapiclient.errors import HttpError

@mcp.tool()
def get_channel_metrics(arguments: dict) -> List[TextContent]:
    """Retrieve statistics for a specific YouTube channel.

    This function queries the YouTube Data API v3 to fetch metrics for a given channel,
    including subscriber count, total view count, and video count, formatted as a TextContent object.

    Args:
        arguments: A dictionary containing:
            - channel_id (str): The YouTube channel ID (required).

    Returns:
        List[TextContent]: A list containing a single TextContent object with a formatted string
            including the channel's title, subscriber count, total view count, and video count.
            If the channel is not found, returns a single TextContent with a "No channel found" message.

    Raises:
        YouTubeAPIError: If the API key is missing, the channel ID is invalid, the API request fails,
            or an unexpected error occurs.
    """
    youtube = get_youtube_client()

    try:
        channel_id = arguments.get("channel_id", "")
        if not channel_id:
            raise YouTubeAPIError("Channel ID is required")

        response = youtube.channels().list(
            part='snippet,statistics',
            id=channel_id
        ).execute()

        items = response.get('items', [])
        if not items:
            return [TextContent(type="text", text="No channel found for the given ID.")]

        item = items[0]
        channel_info = {
            'title': item['snippet']['title'],
            'subscriber_count': item['statistics'].get('subscriberCount', '0'),
            'view_count': item['statistics'].get('viewCount', '0'),
            'video_count': item['statistics'].get('videoCount', '0')
        }

        return [TextContent(
            type="text",
            text=(f"**{channel_info['title']}**\n"
                  f"Subscribers: {channel_info['subscriber_count']}\n"
                  f"Total Views: {channel_info['view_count']}\n"
                  f"Videos: {channel_info['video_count']}")
        )]

    except HttpError as e:
        raise YouTubeAPIError(f"YouTube API error for channel ID '{channel_id}': {e}")
    except Exception as e:
        raise YouTubeAPIError(f"Unexpected error for channel ID '{channel_id}': {e}")