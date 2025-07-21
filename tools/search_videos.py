from server import mcp
from mcp.types import TextContent
from typing import List
from utils import validate_youtube_params, YouTubeAPIError, get_youtube_client
from googleapiclient.errors import HttpError

@mcp.tool()
def search_videos(arguments: dict) -> List[TextContent]:
    """Search YouTube for videos based on a query and optional filters.

    This function queries the YouTube Data API v3 to retrieve videos matching the provided
    search criteria. Each result includes the video title, channel, ID, publication date,
    description, and thumbnail URL, formatted as a TextContent object.

    Args:
        arguments: A dictionary containing search parameters:
            - query (str): The search query (required).
            - max_results (int, optional): Maximum number of results (1 to 50). Defaults to 25.
            - order (str, optional): Sort order ('relevance', 'date', 'rating', 'viewCount'). Defaults to 'relevance'.
            - duration (str, optional): Video duration filter ('any', 'short', 'medium', 'long'). Defaults to 'any'.
            - published_after (str, optional): RFC 3339 timestamp (e.g., '2023-01-01T00:00:00Z') to filter videos uploaded after this date.

    Returns:
        List[TextContent]: A list of TextContent objects, each containing a formatted string
            with video details (title, channel, video ID, publication date, and truncated description).
            If no results are found, returns a single TextContent with a "No videos found" message.

    Raises:
        YouTubeAPIError: If the API key is missing, the API request fails, or an unexpected error occurs.
    """

    youtube = get_youtube_client()
    
    try:
        query = arguments.get("query", "")
        max_results = min(arguments.get("max_results", 25), 50)  # API limit
        order = arguments.get("order", "relevance")
        duration = arguments.get("duration", "medium")
        upload_date = arguments.get("published_after", None)
        
        # Validate parameters
        validate_youtube_params(order, duration, upload_date)
        
        search_params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': max_results,
            'order': order
        }
        
        if duration != "any":
            search_params['videoDuration'] = duration
        if upload_date:
            search_params['publishedAfter'] = upload_date
        
        response = youtube.search().list(**search_params).execute()
        
        results = []
        for item in response.get('items', []):
            description = item['snippet']['description']
            truncated_desc = description[:200] + ('...' if description else '')
            video_info = {
                'video_id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'description': truncated_desc,
                'channel_title': item['snippet']['channelTitle'],
                'published_at': item['snippet']['publishedAt'],
                'thumbnail_url': item['snippet']['thumbnails'].get('default', {}).get('url', '')
            }
            # Create one TextContent per video
            results.append(TextContent(
                type="text",
                text=(f"**{video_info['title']}**\n"
                      f"Channel: {video_info['channel_title']}\n"
                      f"Video ID: {video_info['video_id']}\n"
                      f"Published: {video_info['published_at']}\n"
                      f"Description: {video_info['description']}")
            ))
        
        return results if results else [TextContent(type="text", text="No videos found.")]
    
    except HttpError as e:
        raise YouTubeAPIError(f"YouTube API error for query '{query}': {e}")
    except Exception as e:
        raise YouTubeAPIError(f"Unexpected error for query '{query}': {e}")