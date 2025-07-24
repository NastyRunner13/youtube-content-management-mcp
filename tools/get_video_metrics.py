from server import mcp
from mcp.types import TextContent
from typing import List
from utils.tool_utils import YouTubeAPIError, get_youtube_client
from googleapiclient.errors import HttpError
from utils.models import VideoIdInput

@mcp.tool()
def get_video_metrics(arguments: dict) -> List[TextContent]:
    """Retrieve statistics for a specific YouTube video.

    This function queries the YouTube Data API v3 to fetch metrics for a given video,
    including view count, like count, and comment count, formatted as a TextContent object.

    Args:
        arguments: A dictionary containing:
            - video_id (str): The YouTube video ID (required).

    Returns:
        List[TextContent]: A list containing a single TextContent object with a formatted string
            including the video's title, view count, like count, and comment count. If the video
            is not found, returns a single TextContent with a "No video found" message.

    Raises:
        YouTubeAPIError: If the API key is missing, the video ID is invalid, the API request fails,
            or the input arguments are invalid (via Pydantic).
    """
    try:
        input_data = VideoIdInput(**arguments)
    except ValueError as e:
        raise YouTubeAPIError(f"Invalid input arguments: {e}")

    youtube = get_youtube_client()

    try:
        response = youtube.videos().list(
            part='snippet,statistics',
            id=input_data.video_id
        ).execute()

        items = response.get('items', [])
        if not items:
            return [TextContent(type="text", text="No video found for the given ID.")]

        item = items[0]
        video_info = {
            'title': item['snippet']['title'],
            'view_count': item['statistics'].get('viewCount', '0'),
            'like_count': item['statistics'].get('likeCount', '0'),
            'comment_count': item['statistics'].get('commentCount', '0')
        }

        return [TextContent(
            type="text",
            text=(f"**{video_info['title']}**\n"
                  f"Views: {video_info['view_count']}\n"
                  f"Likes: {video_info['like_count']}\n"
                  f"Comments: {video_info['comment_count']}")
        )]

    except HttpError as e:
        raise YouTubeAPIError(f"YouTube API error for video ID '{input_data.video_id}': {e}")
    except Exception as e:
        raise YouTubeAPIError(f"Unexpected error for video ID '{input_data.video_id}': {e}")