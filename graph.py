import asyncio
import operator
from typing import Annotated, Optional, Sequence, TypedDict

import aiofiles
from langchain_community.vectorstores import FAISS
from langchain_core.messages import BaseMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import OpenAIEmbeddings
from langchain_tavily import TavilySearch
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END


async def create_rag_system(document_path: str) -> FAISS:
    """Create a RAG system using FAISS vector store from the schema documentation."""
    # Read the document asynchronously
    async with aiofiles.open(document_path, "r") as f:
        document_text = await f.read()

    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_text(document_text)

    # Create embeddings and vector store in a thread to avoid blocking
    embeddings = OpenAIEmbeddings()
    vector_store = await asyncio.to_thread(FAISS.from_texts, chunks, embeddings)

    return vector_store


async def retrieve_relevant_context(vector_store: FAISS, query: str, k: int = 3) -> str:
    """Retrieve relevant context from the vector store based on the query."""
    docs = await asyncio.to_thread(vector_store.similarity_search, query, k)
    return "\n\n".join([doc.page_content for doc in docs])


class AgentState(TypedDict):
    """State shared between agents in the multi-agent system."""

    messages: Annotated[Sequence[BaseMessage], operator.add]


def route_query(state: AgentState) -> str:
    """Route queries to the appropriate agent based on content."""
    last_message = state["messages"][-1]
    
    # Handle both dict and message object formats
    if hasattr(last_message, 'content'):
        content = last_message.content.lower()
    elif isinstance(last_message, dict) and 'content' in last_message:
        content = last_message['content'].lower()
    else:
        # Default to general agent if we can't parse the message
        return "general_agent"

    # Route to data analyst for analysis, statistics, reporting queries
    analysis_keywords = [
        "analyze",
        "analysis",
        "statistics",
        "report",
        "trend",
        "pattern",
        "aggregate",
        "summary",
        "insights",
        "metrics",
        "performance",
    ]

    if any(keyword in content for keyword in analysis_keywords):
        return "data_analyst"
    else:
        return "general_agent"


async def create_data_analyst_agent(mcp_tools, vector_store):
    """Create a specialized data analyst agent."""
    sample_context = await retrieve_relevant_context(
        vector_store, "sales performance metrics analysis reporting", k=3
    )

    return create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=mcp_tools,
        prompt=f"""
        You are a specialized Data Analyst AI assistant focused on statistical analysis and reporting.
        
        Your expertise includes:
        - Performing data analysis and generating insights
        - Creating statistical summaries and reports
        - Identifying trends and patterns in data
        - Calculating key performance metrics
        - Providing actionable business insights
        
        Database context: You work with the `Adventureworks` database, `sales` schema.
        
        Schema information:
        {sample_context}
        
        Always provide clear, data-driven insights with specific numbers and trends when analyzing data.
        Focus on actionable business intelligence in your responses.
        """,
    )


async def general_agent_node(state: AgentState):
    """Execute the general agent."""
    # Initialize Tavily search
    tavily_search = TavilySearch(
        max_results=3, description="Search the internet for information using Tavily"
    )

    # Initialize MCP client for database access
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

    # Create RAG system from schema documentation
    vector_store = await create_rag_system("sales_schema_documentation.md")

    # Get MCP tools
    mcp_tools = await client.get_tools()
    tools = mcp_tools + [tavily_search]

    # Get a sample of the documentation to include in the base prompt
    sample_context = await retrieve_relevant_context(
        vector_store, "sales orders revenue customers products", k=5
    )

    # Create the general agent
    general_agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=tools,
        prompt=f"""
        You are a helpful general assistant that can answer questions about the database or search the internet.
        If you need to query the database, you should be looking into the `Adventureworks` database, `sales` schema.
        
        Here is key schema documentation for the sales database:
        
        {sample_context}
        
        You have access to database tools and web search capabilities. Use the appropriate tools based on the user's query.
        Use this schema information to understand table structures and relationships when writing SQL queries.
        
        You handle general queries, basic database lookups, and web searches.
        """,
    )

    # Execute the agent
    result = await general_agent.ainvoke({"messages": state["messages"]})
    return {"messages": result["messages"]}


async def data_analyst_node(state: AgentState):
    """Execute the data analyst agent."""
    # Initialize MCP client for database access
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

    # Create RAG system from schema documentation
    vector_store = await create_rag_system("sales_schema_documentation.md")

    # Get MCP tools (data analyst doesn't need web search)
    mcp_tools = await client.get_tools()

    # Create the data analyst agent
    data_analyst = await create_data_analyst_agent(mcp_tools, vector_store)

    # Execute the agent
    result = await data_analyst.ainvoke({"messages": state["messages"]})
    return {"messages": result["messages"]}


async def make_graph():
    """Create and return a multi-agent LangGraph system."""

    # Create the state graph
    workflow = StateGraph(AgentState)

    # Add agent nodes
    workflow.add_node("general_agent", general_agent_node)
    workflow.add_node("data_analyst", data_analyst_node)

    # Add routing logic
    workflow.add_conditional_edges(
        "general_agent", lambda state: END, {END: END}  # General agent always ends
    )

    workflow.add_conditional_edges(
        "data_analyst", lambda state: END, {END: END}  # Data analyst always ends
    )

    # Set entry point with routing
    workflow.set_conditional_entry_point(
        route_query, {"general_agent": "general_agent", "data_analyst": "data_analyst"}
    )

    return workflow.compile()
