from server import mcp
import tools.search_videos  # Import the search_videos tool to register it with the MCP server
import tools.search_channels  # Import the search_channels tool to register it with the MCP server
import tools.search_playlists  # Import the search_playlists tool to register it with the MCP server
import tools.get_video_metrics  # Import the get_video_metrics tool to register it with the MCP server
import tools.get_channel_metrics  # Import the get_channel_metrics tool to register it with the MCP
import tools.get_playlist_metrics  # Import the get_playlist_metrics tool to register it with the MCP server
import tools.fetch_transcripts  # Import the fetch_transcripts tool to register it with the MCP server

# Entry point to run the server
if __name__ == "__main__":
    mcp.run()