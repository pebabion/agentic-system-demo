import asyncio
import aiofiles
from langchain_community.vectorstores import FAISS
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import OpenAIEmbeddings
from langchain_tavily import TavilySearch
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.prebuilt import create_react_agent


async def create_rag_system(document_path: str) -> FAISS:
    """Create a RAG system using FAISS vector store from the schema documentation."""
    # Read the document asynchronously
    async with aiofiles.open(document_path, "r") as f:
        document_text = await f.read()
    
    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
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


async def make_graph():
    """Create and return the LangGraph agent with RAG capabilities."""
    
    # Initialize Tavily search
    tavily_search = TavilySearch(
        max_results=3, 
        description="Search the internet for information using Tavily"
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
    sample_context = await retrieve_relevant_context(vector_store, "sales orders revenue customers products", k=5)
    
    # Create the base agent with comprehensive context
    base_agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=tools,
        prompt=f"""
        You are a helpful assistant that can answer questions about the data in the database or the internet.
        If you need to query the database, you should be looking into the `Adventureworks` database, `sales` schema.
        
        Here is key schema documentation for the sales database:
        
        {sample_context}
        
        You have access to database tools and web search capabilities. Use the appropriate tools based on the user's query.
        Use this schema information to understand table structures and relationships when writing SQL queries.
        """
    )
    
    return base_agent