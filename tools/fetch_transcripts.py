from server import mcp
from mcp.types import TextContent
from typing import List
from utils.tool_utils import YouTubeAPIError
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

@mcp.tool()
def fetch_transcripts(arguments: dict) -> List[TextContent]:
    """Retrieve and analyze YouTube video transcripts for detailed information extraction.

    This function fetches the complete transcript of a YouTube video, making it ideal for:
    - Analyzing video content in detail when users ask about specific topics covered in videos
    - Extracting key information, quotes, or explanations from educational content
    - Summarizing long-form video content (lectures, tutorials, presentations, interviews)
    - Finding specific details or timestamps within video discussions
    - Understanding the full context of video content for comprehensive responses
    
    Use this tool when users:
    - Ask detailed questions about YouTube video content
    - Request summaries or key points from video material  
    - Need specific information or quotes from video discussions
    - Want to understand complex topics explained in video format
    - Ask about timestamps or specific moments in videos

    Technical Implementation:
    This function queries the YouTube Data API v3 to fetch available captions for a video
    and retrieves the transcript in the specified language (default: English). The transcript
    is returned as a single TextContent object with timestamped text entries. If no transcript
    is available, a message indicating the reason is returned.

    Args:
        arguments: A dictionary containing:
            - video_id (str, optional): The YouTube video ID.
            - video_url (str, optional): The YouTube video URL (e.g., 'https://www.youtube.com/watch?v=VIDEO_ID').
            - language_code (str, optional): Language code for the transcript (e.g., 'en'). Defaults to 'en'.
            Either video_id or video_url must be provided.

    Returns:
        List[TextContent]: A list containing a single TextContent object with the transcript
            as a formatted string (timestamp and text). If no transcript is available or the
            video is not found, returns a TextContent with an appropriate message.

    Raises:
        YouTubeAPIError: If the API key is missing, the API request fails, the input arguments
            are invalid (via Pydantic), or an unexpected error occurs.
    """
    from utils.models import FetchTranscriptsInput  # Moved import here to avoid circular import issues

    try:
        input_data = FetchTranscriptsInput(**arguments)
    except ValueError as e:
        raise YouTubeAPIError(f"Invalid input arguments: {e}")
    
    ytt_api = YouTubeTranscriptApi()

    try:
        # Try to fetch transcript directly first
        try:
            transcript = ytt_api.fetch(
                video_id=input_data.video_id, 
                languages=[input_data.language_code]
            )
        except NoTranscriptFound:
            # If specific language not found, try to get any available transcript
            try:
                transcript = ytt_api.fetch(video_id=input_data.video_id)
            except NoTranscriptFound:
                return [TextContent(type="text", text=f"No transcript available for this video in any language.")]
        
        transcript_text = "".join(snippet.text for snippet in transcript.snippets)

        if not transcript_text.strip():
            return [TextContent(type="text", text="Transcript is empty or unavailable.")]

        return [TextContent(
            type="text",
            text=f"Transcript for video ID {input_data.video_id} (language: {input_data.language_code}):\n\n{transcript_text}"
        )]

    except TranscriptsDisabled:
        return [TextContent(type="text", text="Transcripts are disabled for this video or access is restricted.")]
    except NoTranscriptFound:
        return [TextContent(type="text", text=f"No transcript available for this video.")]
    except Exception as e:
        raise YouTubeAPIError(f"Unexpected error for video ID '{input_data.video_id}': {e}")