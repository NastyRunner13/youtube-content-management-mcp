from server import mcp
from mcp.types import TextContent
from typing import List
from utils import YouTubeAPIError, get_youtube_client
from googleapiclient.errors import HttpError

@mcp.tool()
def search_channels(arguments: dict) -> List[TextContent]:
    """Search YouTube for channels based on a query.

    This function queries the YouTube Data API v3 to retrieve channels matching the provided
    search query. Each result includes the channel title, ID, creation date, and a truncated
    description, formatted as a single TextContent object.

    Args:
        arguments: A dictionary containing search parameters:
            - query (str): The search query (required).
            - max_results (int, optional): Maximum number of results (1 to 50). Defaults to 25.

    Returns:
        List[TextContent]: A list containing a single TextContent object with a formatted string
            listing all found channels, including their title, channel ID, creation date, and
            truncated description. If no channels are found, returns a single TextContent with
            a "No channels found" message.

    Raises:
        YouTubeAPIError: If the API key is missing, the API request fails, or an unexpected error occurs.
    """
    youtube = get_youtube_client()

    try:
        query = arguments.get("query", "")
        max_results = min(arguments.get("max_results", 25), 50)
        
        response = youtube.search().list(
            part='snippet',
            q=query,
            type='channel',
            maxResults=max_results
        ).execute()
        
        channels = []
        for item in response.get('items', []):
            channel_info = {
                'channel_id': item['id']['channelId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'][:200] + ('...' if item['snippet']['description'] else ''),
                'published_at': item['snippet']['publishedAt']
            }
            channels.append(channel_info)
        
        if not channels:
            return [TextContent(type="text", text="No channels found.")]
        
        return [TextContent(
            type="text",
            text=f"Found {len(channels)} channels:\n\n" + 
                 "\n\n".join([f"**{c['title']}**\n"
                              f"Channel ID: {c['channel_id']}\n"
                              f"Created: {c['published_at']}\n"
                              f"Description: {c['description']}"
                              for c in channels])
        )]
        
    except HttpError as e:
        raise YouTubeAPIError(f"YouTube API error for query '{query}': {e}")
    except Exception as e:
        raise YouTubeAPIError(f"Unexpected error for query '{query}': {e}")