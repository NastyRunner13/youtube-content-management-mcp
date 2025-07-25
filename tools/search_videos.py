from server import mcp
from mcp.types import TextContent
from typing import List
from utils.tool_utils import YouTubeAPIError, get_youtube_client
from googleapiclient.errors import HttpError
from tools.get_video_metrics import get_video_metrics
from utils.models import SearchVideosInput

@mcp.tool()
def search_videos(arguments: dict) -> List[TextContent]:
    """Search YouTube for videos based on a query and optional filters, excluding short videos, with metrics.

    This function queries the YouTube Data API v3 to retrieve videos matching the provided
    search criteria. Short videos (under 4 minutes) are excluded. Each result includes the
    video title, channel, ID, publication date, description, thumbnail URL, view count,
    like count, and comment count, formatted as a TextContent object. Metrics are fetched
    using the get_video_metrics tool.

    Args:
        arguments: A dictionary containing search parameters:
            - query (str): The search query (required).
            - max_results (int, optional): Maximum number of results (1 to 50). Defaults to 25.
            - order (str, optional): Sort order ('relevance', 'date', 'rating', 'viewCount'). Defaults to 'relevance'.
            - duration (str, optional): Video duration filter ('medium', 'long'). Defaults to 'medium'.
            - published_after (str, optional): RFC 3339 timestamp (e.g., '2023-01-01T00:00:00Z') to filter videos uploaded after this date.

    Returns:
        List[TextContent]: A list of TextContent objects, each containing a formatted string
            with video details (title, channel, video ID, publication date, truncated description,
            view count, like count, and comment count). If no videos are found, returns a single
            TextContent with a "No videos found" message.

    Raises:
        YouTubeAPIError: If the API key is missing, the API request fails, the input arguments are invalid (via Pydantic), or an unexpected error occurs.
    """
    try:
        input_data = SearchVideosInput(**arguments)
    except ValueError as e:
        raise YouTubeAPIError(f"Invalid input arguments: {e}")

    youtube = get_youtube_client()
    
    try:
        search_params = {
            'part': 'snippet',
            'q': input_data.query,
            'type': 'video',
            'maxResults': input_data.max_results,
            'order': input_data.order,
            'videoDuration': input_data.duration
        }
        
        if input_data.published_after:
            search_params['publishedAfter'] = input_data.published_after
        
        search_response = youtube.search().list(**search_params).execute()
        
        results = []
        for item in search_response.get('items', []):
            video_id = item['id']['videoId']
            description = item['snippet']['description']
            truncated_desc = description[:200] + ('...' if description else '')
            video_info = {
                'video_id': video_id,
                'title': item['snippet']['title'],
                'description': truncated_desc,
                'channel_title': item['snippet']['channelTitle'],
                'published_at': item['snippet']['publishedAt'],
                'thumbnail_url': item['snippet']['thumbnails'].get('default', {}).get('url', '')
            }
            
            # Fetch metrics using get_video_metrics
            metrics_response = get_video_metrics({"video_id": video_id})
            if metrics_response[0].text.startswith("No video found"):
                continue
            metrics_text = metrics_response[0].text.split('\n')
            view_count = next((line.split(': ')[1] for line in metrics_text if line.startswith('Views')), '0')
            like_count = next((line.split(': ')[1] for line in metrics_text if line.startswith('Likes')), '0')
            comment_count = next((line.split(': ')[1] for line in metrics_text if line.startswith('Comments')), '0')
            
            results.append(TextContent(
                type="text",
                text=(f"**{video_info['title']}**\n"
                      f"Channel: {video_info['channel_title']}\n"
                      f"Video ID: {video_info['video_id']}\n"
                      f"Published: {video_info['published_at']}\n"
                      f"Views: {view_count}\n"
                      f"Likes: {like_count}\n"
                      f"Comments: {comment_count}\n"
                      f"Description: {video_info['description']}")
            ))
        
        return results if results else [TextContent(type="text", text="No videos found.")]
    
    except HttpError as e:
        raise YouTubeAPIError(f"YouTube API error for query '{input_data.query}': {e}")
    except Exception as e:
        raise YouTubeAPIError(f"Unexpected error for query '{input_data.query}': {e}")