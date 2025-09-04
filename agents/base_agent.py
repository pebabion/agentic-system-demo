"""Base agent class with common functionality."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from langchain_core.messages import BaseMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_community.vectorstores import FAISS


class BaseAgent(ABC):
    """Base class for all agents in the hierarchical system."""
    
    def __init__(
        self, 
        agent_id: str, 
        name: str, 
        description: str,
        vector_store: Optional[FAISS] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.vector_store = vector_store
        self.mcp_client = None
        self.tools = []
    
    async def initialize(self):
        """Initialize the agent with necessary resources."""
        # Initialize MCP client for database access
        self.mcp_client = MultiServerMCPClient({
            "postgres": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-postgres",
                    "postgresql://postgres:secret@localhost:54321/Adventureworks",
                ],
                "transport": "stdio",
            },
        })
        
        # Get MCP tools
        if self.mcp_client:
            mcp_tools = await self.mcp_client.get_tools()
            self.tools.extend(mcp_tools)
    
    async def retrieve_context(self, query: str, k: int = 3) -> str:
        """Retrieve relevant context from vector store."""
        if not self.vector_store:
            return ""
        
        docs = self.vector_store.similarity_search(query, k=k)
        return "\n\n".join([doc.page_content for doc in docs])
    
    @abstractmethod
    async def process_message(self, messages: List[BaseMessage]) -> Dict[str, Any]:
        """Process incoming messages and return response."""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        return [
            f"Agent ID: {self.agent_id}",
            f"Name: {self.name}",
            f"Description: {self.description}",
            f"Available tools: {len(self.tools)}"
        ]