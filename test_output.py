import asyncio
import os
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def perform_test_search():
    # 1. Configuration: Use absolute path for reliability
    server_path = os.path.abspath("./gs_MCP")
    server_script = "google_scholar_server.py"
    
    server_params = StdioServerParameters(
        command="uv",
        args=["--directory", server_path, "run", server_script],
    )

    print("--- 🚀 Connecting to ScholarScout Server ---")

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # 2. Automatically discover the available search tool
                tools_result = await session.list_tools()
                if not tools_result.tools:
                    print("❌ No tools found in the server.")
                    return
                
                # We look for a tool that sounds like 'search'
                search_tool = next((t.name for t in tools_result.tools if "search" in t.name), tools_result.tools[0].name)
                print(f"--- 🔎 Using Tool: {search_tool} ---")

                # 3. Perform the actual search based on your Special Issue
                # Adjust 'query' to match the argument name found in your server (usually 'query' or 'name')
                test_topic = "Security and Privacy in Connected and Autonomous Vehicles"
                
                try:
                    # We try common argument patterns
                    response = await session.call_tool(search_tool, arguments={"query": test_topic})
                    
                    print("\n--- 📊 DATA OUTPUT RECEIVED ---")
                    # MCP returns a list of content blocks
                    for content in response.content:
                        if content.type == 'text':
                            # Try to pretty-print if it's JSON text
                            try:
                                data = json.loads(content.text)
                                print(json.dumps(data, indent=4))
                            except:
                                print(content.text)
                                
                except Exception as e:
                    print(f"❌ Execution Error: {e}")
                    print("Hint: Check if the tool uses 'query', 'keywords', or 'name' as the argument.")

    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    asyncio.run(perform_test_search())