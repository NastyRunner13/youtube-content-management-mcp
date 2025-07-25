from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
import re

class SearchVideosInput(BaseModel):
    query: str = Field(..., min_length=1, description="The search query (required)")
    max_results: Optional[int] = Field(25, ge=1, le=50, description="Maximum number of results (1 to 50)")
    order: Optional[str] = Field("relevance", description="Sort order: relevance, date, rating, viewCount")
    duration: Optional[str] = Field("medium", description="Video duration: medium, long")
    published_after: Optional[str] = Field(None, description="RFC 3339 timestamp (e.g., 2023-01-01T00:00:00Z)")

    @field_validator("order")
    @classmethod
    def validate_order(cls, v):
        valid_orders = {"relevance", "date", "rating", "viewCount"}
        if v not in valid_orders:
            raise ValueError(f"Invalid order: {v}. Must be one of {valid_orders}")
        return v

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, v):
        valid_durations = {"medium", "long"}
        if v not in valid_durations:
            raise ValueError(f"Invalid duration: {v}. Must be one of {valid_durations}")
        return v

    @field_validator("published_after")
    @classmethod
    def validate_published_after(cls, v):
        if v and not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', v):
            raise ValueError(f"Invalid published_after format: {v}. Must be RFC 3339 (e.g., 2023-01-01T00:00:00Z)")
        return v

class SearchChannelsInput(BaseModel):
    query: str = Field(..., min_length=1, description="The search query (required)")
    max_results: Optional[int] = Field(25, ge=1, le=50, description="Maximum number of results (1 to 50)")
    published_after: Optional[str] = Field(None, description="RFC 3339 timestamp (e.g., 2023-01-01T00:00:00Z)")

    @field_validator("published_after")
    @classmethod
    def validate_published_after(cls, v):
        if v and not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', v):
            raise ValueError(f"Invalid published_after format: {v}. Must be RFC 3339 (e.g., 2023-01-01T00:00:00Z)")
        return v

class SearchPlaylistsInput(BaseModel):
    query: str = Field(..., min_length=1, description="The search query (required)")
    max_results: Optional[int] = Field(25, ge=1, le=50, description="Maximum number of results (1 to 50)")
    published_after: Optional[str] = Field(None, description="RFC 3339 timestamp (e.g., 2023-01-01T00:00:00Z)")

    @field_validator("published_after")
    @classmethod
    def validate_published_after(cls, v):
        if v and not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', v):
            raise ValueError(f"Invalid published_after format: {v}. Must be RFC 3339 (e.g., 2023-01-01T00:00:00Z)")
        return v

class VideoIdInput(BaseModel):
    video_id: str = Field(..., min_length=1, description="The YouTube video ID (required)")

class ChannelIdInput(BaseModel):
    channel_id: str = Field(..., min_length=1, description="The YouTube channel ID (required)")

class PlaylistIdInput(BaseModel):
    playlist_id: str = Field(..., min_length=1, description="The YouTube playlist ID (required)")

class FetchTranscriptsInput(BaseModel):
    video_id: Optional[str] = Field(None, min_length=1, description="The YouTube video ID")
    video_url: Optional[str] = Field(None, description="The YouTube video URL")
    language_code: Optional[str] = Field("en", description="Language code for the transcript (e.g., 'en')")

    @model_validator(mode='before')
    @classmethod
    def check_id_or_url(cls, values):
        # Handle both dict and object inputs
        if hasattr(values, '__dict__'):
            values = values.__dict__
        
        video_id = values.get("video_id")
        video_url = values.get("video_url")
        
        if not video_id and not video_url:
            raise ValueError("Either video_id or video_url must be provided")
        
        if video_url:
            # Extract video ID from URL
            patterns = [
                r"(?:v=|v\/|embed\/|youtu.be\/)([A-Za-z0-9_-]{11})",
                r"watch\?v=([A-Za-z0-9_-]{11})"
            ]
            for pattern in patterns:
                match = re.search(pattern, video_url)
                if match:
                    values["video_id"] = match.group(1)
                    break
            else:
                raise ValueError("Invalid YouTube URL: could not extract video ID")
        
        return values

    @field_validator("language_code")
    @classmethod
    def validate_language_code(cls, v):
        if not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', v):
            raise ValueError(f"Invalid language code: {v}. Must be a valid ISO 639-1 code (e.g., 'en', 'en-US')")
        return v