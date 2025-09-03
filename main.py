from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent

tavily_search = TavilySearch(
    max_results=3, description="Search the internet for information using Tavily"
)


agent = create_react_agent(
    model="anthropic:claude-3-7-sonnet-latest",
    tools=[tavily_search],
    prompt="You are a helpful assistant",
)


response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "what is the date today and what is the weather in sf",
            }
        ]
    }
)

for message in response["messages"]:
    message.pretty_print()
