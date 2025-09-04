"""General purpose agent for basic queries and web search."""

from typing import Dict, List, Any
from langchain_core.messages import BaseMessage, AIMessage
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent

from .base_agent import BaseAgent


class GeneralAgent(BaseAgent):
    """General purpose agent that handles basic queries and web search."""
    
    def __init__(self, vector_store=None):
        super().__init__(
            agent_id="general_agent",
            name="General Agent",
            description="Handles general queries, basic database lookups, and web searches",
            vector_store=vector_store
        )
        self.tavily_search = None
        self.agent = None
    
    async def initialize(self):
        """Initialize the general agent with tools and capabilities."""
        await super().initialize()
        
        # Initialize Tavily search
        self.tavily_search = TavilySearch(
            max_results=3, 
            description="Search the internet for information using Tavily"
        )
        
        # Add web search to tools
        self.tools.append(self.tavily_search)
        
        # Get context for the agent prompt
        sample_context = ""
        if self.vector_store:
            sample_context = await self.retrieve_context(
                "sales orders revenue customers products", k=5
            )
        
        # Create the React agent
        self.agent = create_react_agent(
            model="anthropic:claude-3-7-sonnet-latest",
            tools=self.tools,
            prompt=f"""
            You are a helpful general assistant that can answer questions about the database or search the internet.
            If you need to query the database, you should be looking into the `Adventureworks` database, `sales` schema.
            
            Here is key schema documentation for the sales database:
            
            {sample_context}
            
            You have access to database tools and web search capabilities. Use the appropriate tools based on the user's query.
            Use this schema information to understand table structures and relationships when writing SQL queries.
            
            You handle:
            - General queries and conversations
            - Basic database lookups and simple queries
            - Web searches for external information
            - Product information and basic customer queries
            
            When you receive a query, analyze whether it needs:
            1. Database access - use the MCP tools for PostgreSQL
            2. Web search - use the Tavily search tool
            3. Both - combine results appropriately
            4. Neither - provide a direct response
            
            Always be helpful and provide accurate information.
            """,
        )
    
    async def process_message(self, messages: List[BaseMessage]) -> Dict[str, Any]:
        """Process messages through the general agent."""
        if not self.agent:
            await self.initialize()
        
        # Execute the agent
        result = await self.agent.ainvoke({"messages": messages})
        return result
    
    def get_capabilities(self) -> List[str]:
        """Return specific capabilities of the general agent."""
        base_capabilities = super().get_capabilities()
        specific_capabilities = [
            "Web search via Tavily",
            "Basic SQL queries",
            "General conversation",
            "Product information lookup",
            "Customer basic queries",
            "External information research"
        ]
        return base_capabilities + specific_capabilities