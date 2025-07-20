import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import os

load_dotenv()

class YouTubeAPIError(Exception):
    """Custom exception for YouTube API errors"""
    pass

def validate_youtube_params(order: str, duration: str, published_after: str | None) -> None:
    """Validate YouTube API parameters"""
    valid_orders = {"relevance", "date", "rating", "viewCount"}
    valid_durations = {"any", "short", "medium", "long"}
    
    if order not in valid_orders:
        raise ValueError(f"Invalid order parameter: {order}. Must be one of {valid_orders}")
    if duration not in valid_durations:
        raise ValueError(f"Invalid duration parameter: {duration}. Must be one of {valid_durations}")
    if published_after and not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', published_after):
        raise ValueError(f"Invalid published_after format: {published_after}. Must be RFC 3339 (e.g., 2023-01-01T00:00:00Z)")

def get_youtube_client():
    """Get a singleton YouTube API client instance."""
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        raise YouTubeAPIError("YouTube API key is not set in environment variables")
    
    # Cache the client instance (module-level singleton)
    if not hasattr(get_youtube_client, 'client'):
        get_youtube_client.client = build('youtube', 'v3', developerKey=api_key)
    
    return get_youtube_client.client