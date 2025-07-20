from server import mcp
import tools.search_videos  # Import the search_videos tool to register it with the MCP server
import tools.search_channels  # Import the search_channels tool to register it with the MCP server

# Entry point to run the server
if __name__ == "__main__":
    mcp.run()