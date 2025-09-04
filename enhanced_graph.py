"""Enhanced multi-agent system with hierarchical supervision and memory persistence."""

import asyncio
import operator
from typing import Annotated, Optional, Sequence, TypedDict, Literal

import aiofiles
from langchain_community.vectorstores import FAISS
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from agents import SupervisorAgent, GeneralAgent, DataAnalystAgent


class AgentState(TypedDict):
    """Enhanced state shared between agents in the hierarchical system."""
    
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_agent: Optional[str]
    task_breakdown: Optional[dict]
    execution_plan: Optional[dict]
    agent_results: Optional[dict]
    supervision_active: bool


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


class HierarchicalSystem:
    """Hierarchical multi-agent system with supervisor coordination."""
    
    def __init__(self):
        self.vector_store = None
        self.supervisor = None
        self.general_agent = None
        self.data_analyst = None
        self.checkpointer = None
        self.graph = None
    
    async def initialize(self, schema_doc_path: str = "sales_schema_documentation.md"):
        """Initialize the hierarchical system with all agents and persistence."""
        print("🚀 Initializing hierarchical multi-agent system...")
        
        # Create RAG system
        print("📚 Creating RAG system from schema documentation...")
        self.vector_store = await create_rag_system(schema_doc_path)
        
        # Initialize SQLite checkpointer for memory persistence
        print("💾 Setting up memory persistence with SQLite...")
        self.checkpointer = SqliteSaver.from_conn_string("agent_memory.db")
        
        # Initialize agents
        print("🤖 Initializing agents...")
        self.supervisor = SupervisorAgent(self.vector_store)
        self.general_agent = GeneralAgent(self.vector_store)
        self.data_analyst = DataAnalystAgent(self.vector_store)
        
        # Initialize all agents
        await self.supervisor.initialize()
        await self.general_agent.initialize()
        await self.data_analyst.initialize()
        
        # Create the graph
        print("🔗 Building hierarchical coordination graph...")
        self.graph = await self._create_graph()
        
        print("✅ Hierarchical system initialized successfully!")
    
    def route_to_supervisor(self, state: AgentState) -> Literal["supervisor", "general_agent", "data_analyst"]:
        """Route initial queries to supervisor for coordination."""
        # Always route to supervisor first for hierarchical coordination
        return "supervisor"
    
    def route_from_supervisor(self, state: AgentState) -> Literal["general_agent", "data_analyst", "END"]:
        """Route from supervisor to appropriate specialized agent."""
        if not state.get("task_breakdown"):
            return "END"
        
        # Get the primary agent from task breakdown
        task_breakdown = state["task_breakdown"]
        primary_agent = task_breakdown.get("primary_agent", "general_agent")
        
        # For this implementation, route to the primary agent
        # In a full implementation, this would handle multiple subtasks
        if primary_agent == "data_analyst":
            return "data_analyst"
        else:
            return "general_agent"
    
    async def supervisor_node(self, state: AgentState):
        """Execute the supervisor agent."""
        print("🎯 Supervisor: Analyzing and coordinating task...")
        
        # Update state to indicate supervision is active
        state["supervision_active"] = True
        state["current_agent"] = "supervisor"
        
        # Process through supervisor
        result = await self.supervisor.process_message(state["messages"])
        
        # Extract task breakdown from supervisor's analysis
        # In a real implementation, the supervisor would return structured data
        # For now, we'll simulate this
        latest_message = state["messages"][-1]
        if hasattr(latest_message, 'content'):
            query = latest_message.content
        else:
            query = str(latest_message)
        
        # Get task breakdown from supervisor
        task_breakdown = await self.supervisor.decompose_task(query)
        
        return {
            "messages": result["messages"],
            "current_agent": "supervisor",
            "task_breakdown": task_breakdown,
            "supervision_active": True
        }
    
    async def general_agent_node(self, state: AgentState):
        """Execute the general agent."""
        print("🔧 General Agent: Processing general query...")
        
        state["current_agent"] = "general_agent"
        
        # If supervised, use the original query but with supervisor context
        if state.get("supervision_active"):
            # Add supervision context to messages
            supervision_context = AIMessage(
                content="[Supervised Task] The supervisor has analyzed your query and determined it requires general assistance with database queries and/or web search."
            )
            enhanced_messages = list(state["messages"]) + [supervision_context]
        else:
            enhanced_messages = state["messages"]
        
        result = await self.general_agent.process_message(enhanced_messages)
        
        return {
            "messages": result["messages"],
            "current_agent": "general_agent",
            "agent_results": {"general_agent": result}
        }
    
    async def data_analyst_node(self, state: AgentState):
        """Execute the data analyst agent."""
        print("📊 Data Analyst: Performing statistical analysis...")
        
        state["current_agent"] = "data_analyst"
        
        # If supervised, enhance with supervision context
        if state.get("supervision_active"):
            supervision_context = AIMessage(
                content="[Supervised Task] The supervisor has identified this as a data analysis task requiring statistical insights, reporting, and business intelligence."
            )
            enhanced_messages = list(state["messages"]) + [supervision_context]
        else:
            enhanced_messages = state["messages"]
        
        result = await self.data_analyst.process_message(enhanced_messages)
        
        return {
            "messages": result["messages"],
            "current_agent": "data_analyst", 
            "agent_results": {"data_analyst": result}
        }
    
    async def _create_graph(self):
        """Create the hierarchical coordination graph with memory persistence."""
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        workflow.add_node("supervisor", self.supervisor_node)
        workflow.add_node("general_agent", self.general_agent_node)
        workflow.add_node("data_analyst", self.data_analyst_node)
        
        # Set entry point - always start with supervisor
        workflow.set_conditional_entry_point(
            self.route_to_supervisor,
            {
                "supervisor": "supervisor",
                "general_agent": "general_agent", 
                "data_analyst": "data_analyst"
            }
        )
        
        # Add routing from supervisor to specialized agents
        workflow.add_conditional_edges(
            "supervisor",
            self.route_from_supervisor,
            {
                "general_agent": "general_agent",
                "data_analyst": "data_analyst",
                "END": END
            }
        )
        
        # Specialized agents end after completion
        workflow.add_conditional_edges(
            "general_agent",
            lambda state: END,
            {END: END}
        )
        
        workflow.add_conditional_edges(
            "data_analyst", 
            lambda state: END,
            {END: END}
        )
        
        # Compile with memory persistence
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def process_query(
        self, 
        query: str, 
        thread_id: str = "default_session",
        stream: bool = True
    ):
        """Process a query through the hierarchical system with memory persistence."""
        config = {"configurable": {"thread_id": thread_id}}
        input_data = {"messages": [HumanMessage(content=query)]}
        
        print(f"\n🎯 Processing query: {query}")
        print(f"💾 Thread ID: {thread_id}")
        print("-" * 60)
        
        if stream:
            # Stream the response
            async for chunk in self.graph.astream(input_data, config=config):
                print(f"🔄 {chunk}")
                print("-" * 40)
        else:
            # Get final result
            result = await self.graph.ainvoke(input_data, config=config)
            return result
    
    async def get_memory_summary(self, thread_id: str = "default_session"):
        """Get a summary of the conversation memory for a thread."""
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get the current state
        try:
            state = await self.graph.aget_state(config)
            if state and state.values:
                messages = state.values.get("messages", [])
                return {
                    "thread_id": thread_id,
                    "message_count": len(messages),
                    "last_agent": state.values.get("current_agent"),
                    "supervision_active": state.values.get("supervision_active", False),
                    "recent_messages": [
                        {"type": type(msg).__name__, "content": str(msg.content)[:100] + "..."}
                        for msg in messages[-3:]  # Last 3 messages
                    ]
                }
            else:
                return {"thread_id": thread_id, "status": "No conversation history"}
        except Exception as e:
            return {"thread_id": thread_id, "error": str(e)}
    
    def get_system_status(self):
        """Get status of the hierarchical system."""
        return {
            "system": "Hierarchical Multi-Agent System",
            "agents": {
                "supervisor": self.supervisor.get_agent_status() if self.supervisor else None,
                "general_agent": self.general_agent.get_capabilities() if self.general_agent else None,
                "data_analyst": self.data_analyst.get_capabilities() if self.data_analyst else None
            },
            "features": [
                "Hierarchical task coordination",
                "Automatic agent routing",
                "Memory persistence (SQLite)",
                "RAG-enhanced context",
                "Task decomposition",
                "Cross-session continuity"
            ],
            "memory_persistence": "SQLite checkpointer enabled" if self.checkpointer else "Not configured"
        }


# Convenience function for easy usage
async def create_hierarchical_system(schema_doc_path: str = "sales_schema_documentation.md"):
    """Create and initialize the hierarchical system."""
    system = HierarchicalSystem()
    await system.initialize(schema_doc_path)
    return system

# Function for LangGraph dev compatibility
async def make_enhanced_graph():
    """Create the enhanced hierarchical graph for LangGraph dev."""
    system = HierarchicalSystem()
    await system.initialize("sales_schema_documentation.md")
    return system.graph