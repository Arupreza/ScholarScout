import asyncio
import pandas as pd
from langgraph.graph import StateGraph, END
from src.state import ScholarState  # Define your TypedDict here
from src.nodes import discovery_node, enrichment_node, save_node

async def run_scholar_scout():
    # 1. Define the Workflow Graph
    workflow = StateGraph(ScholarState)

    # 2. Add your logic nodes
    workflow.add_node("discovery", discovery_node)   # This node will call the MCP tools
    workflow.add_node("enrichment", enrichment_node) # This node finds emails
    workflow.add_node("save", save_node)             # This node creates the CSV

    # 3. Define the path
    workflow.set_entry_point("discovery")
    workflow.add_edge("discovery", "enrichment")
    workflow.add_edge("enrichment", "save")
    workflow.add_edge("save", END)

    # 4. Compile and Execute
    app = workflow.compile()
    
    initial_input = {
        "topic": "Security and Privacy in Connected and Autonomous Vehicles",
        "candidates": []
    }
    
    print("--- Starting ScholarScout Agent ---")
    async for event in app.astream(initial_input):
        print(event)

if __name__ == "__main__":
    asyncio.run(run_scholar_scout())