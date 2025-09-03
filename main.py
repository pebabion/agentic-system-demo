import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent


async def main():
    tavily_search = TavilySearch(
        max_results=3, description="Search the internet for information using Tavily"
    )

    client = MultiServerMCPClient(
        {
            "postgres": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-postgres",
                    "postgresql://postgres:secret@localhost:54321/Adventureworks",
                ],
                "transport": "stdio",
            },
        }
    )

    mcp_tools = await client.get_tools()
    tools = mcp_tools + [tavily_search]

    agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=tools,
        prompt="""
        You are a helpful assistant that can answer questions about the data in the database or the internet.
        If you need to query the database, you should be looking into the `Adventureworks` database, `sales` schema.
        """,
    )

    # Use astream() for async streaming responses
    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": "What is  the total sales in 2012?"}]}
    ):
        print(chunk)
        print("---" * 20)


# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
