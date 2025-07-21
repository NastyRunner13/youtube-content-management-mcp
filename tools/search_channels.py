from server import mcp
from mcp.types import TextContent
from typing import List
from utils import YouTubeAPIError, get_youtube_client
from googleapiclient.errors import HttpError
from get_channel_metrics import get_channel_metrics
import re

@mcp.tool()
def search_channels(arguments: dict) -> List[TextContent]:
    """Search YouTube for channels based on a query, with metrics.

    This function queries the YouTube Data API v3 to retrieve channels matching the provided
    search query. Each result includes the channel title, ID, creation date, description,
    subscriber count, video count, and total view count, formatted as a single TextContent object.
    Metrics are fetched using the get_channel_metrics tool.

    Args:
        arguments: A dictionary containing search parameters:
            - query (str): The search query (required).
            - max_results (int, optional): Maximum number of results (1 to 50). Defaults to 25.
            - published_after (str, optional): RFC 3339 timestamp (e.g., '2023-01-01T00:00:00Z') to filter channels created after this date.

    Returns:
        List[TextContent]: A list containing a single TextContent object with a formatted string
            listing all found channels, including their title, channel ID, creation date, 
            truncated description, subscriber count, video count, and total view count.
            If no channels are found, returns a single TextContent with a "No channels found" message.

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
            'type': 'channel',
            'maxResults': max_results
        }

        if published_after:
            search_params['publishedAfter'] = published_after

        search_response = youtube.search().list(**search_params).execute()

        channels = []
        for item in search_response.get('items', []):
            channel_id = item['id']['channelId']
            channel_info = {
                'channel_id': channel_id,
                'title': item['snippet']['title'],
                'description': item['snippet']['description'][:200] + ('...' if item['snippet']['description'] else ''),
                'published_at': item['snippet']['publishedAt']
            }

            # Fetch metrics using get_channel_metrics
            metrics_response = get_channel_metrics({"channel_id": channel_id})
            if metrics_response[0].text.startswith("No channel found"):
                continue  # Skip if metrics not found
            metrics_text = metrics_response[0].text.split('\n')
            subscriber_count = next((line.split(': ')[1] for line in metrics_text if line.startswith('Subscribers')), '0')
            video_count = next((line.split(': ')[1] for line in metrics_text if line.startswith('Videos')), '0')
            view_count = next((line.split(': ')[1] for line in metrics_text if line.startswith('Total Views')), '0')

            channel_info.update({
                'subscriber_count': subscriber_count,
                'video_count': video_count,
                'view_count': view_count
            })
            channels.append(channel_info)

        if not channels:
            return [TextContent(type="text", text="No channels found.")]

        return [TextContent(
            type="text",
            text=f"Found {len(channels)} channels:\n\n" +
                 "\n\n".join([f"**{c['title']}**\n"
                              f"Channel ID: {c['channel_id']}\n"
                              f"Created: {c['published_at']}\n"
                              f"Subscribers: {c['subscriber_count']}\n"
                              f"Videos: {c['video_count']}\n"
                              f"Total Views: {c['view_count']}\n"
                              f"Description: {c['description']}"
                              for c in channels])
        )]

    except HttpError as e:
        raise YouTubeAPIError(f"YouTube API error for query '{query}': {e}")
    except Exception as e:
        raise YouTubeAPIError(f"Unexpected error for query '{query}': {e}")