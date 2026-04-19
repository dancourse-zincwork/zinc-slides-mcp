import os
from zinc_slides_tools import mcp

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    mcp.run(transport="sse", port=port)
