import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_diagnostics():
    # 1. Define the server parameters
    # Note: Using absolute path ensures uv finds the directory regardless of where you run the script
    server_path = os.path.abspath("./gs_MCP")
    server_script = "google_scholar_server.py"
    
    print(f"--- Starting Diagnostics for: {server_script} ---")
    print(f"Directory: {server_path}")

    server_params = StdioServerParameters(
        command="uv",
        args=["--directory", server_path, "run", server_script],
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Step 1: Initialize Connection
                print("[1/3] Initializing connection...")
                await session.initialize()
                print("✅ Connection initialized successfully.")

                # Step 2: List Tools
                print("[2/3] Fetching available tools...")
                tools_result = await session.list_tools()
                
                if not tools_result.tools:
                    print("⚠️  Warning: Server connected but returned 0 tools.")
                else:
                    print(f"✅ Found {len(tools_result.tools)} tools:")
                    for tool in tools_result.tools:
                        print(f"   - {tool.name}: {tool.description[:60]}...")

                # Step 3: Test a simple search (Optional)
                print("[3/3] Testing tool call (search_author)...")
                # Note: Replace 'search_author' with a tool name found in step 2 if different
                try:
                    # We use a famous name to guarantee a result if the server is working
                    test_call = await session.call_tool("search_author", arguments={"name": "Geoffrey Hinton"})
                    print("✅ Tool call successful. Server is fully operational.")
                except Exception as e:
                    print(f"❌ Tool call failed: {e}")
                    print("Hint: This might be due to a tool name mismatch or Google Scholar rate limiting.")

    except FileNotFoundError:
        print("❌ Error: 'uv' command not found. Ensure uv is installed and in your PATH.")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nPossible solutions:")
        print("1. Ensure 'google_scholar_server.py' exists in 'gs_MCP' folder.")
        print("2. Check if all dependencies (scholarly, mcp) are installed in the gs_MCP environment.")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())