import asyncio

from langchain_community.vectorstores import FAISS
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import OpenAIEmbeddings
from langchain_tavily import TavilySearch
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.prebuilt import create_react_agent


def create_rag_system(document_path: str) -> FAISS:
    """Create a RAG system using FAISS vector store from the schema documentation."""
    # Read the document
    with open(document_path, "r") as f:
        document_text = f.read()

    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_text(document_text)

    # Create embeddings and vector store
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_texts(chunks, embeddings)

    return vector_store


def retrieve_relevant_context(vector_store: FAISS, query: str, k: int = 3) -> str:
    """Retrieve relevant context from the vector store based on the query."""
    docs = vector_store.similarity_search(query, k=k)
    return "\n\n".join([doc.page_content for doc in docs])


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

    # Create RAG system from schema documentation
    print("Creating RAG system from schema documentation...")
    vector_store = create_rag_system("sales_schema_documentation.md")

    mcp_tools = await client.get_tools()
    tools = mcp_tools + [tavily_search]

    # Create enhanced agent with RAG capability
    def create_enhanced_agent_with_rag(user_query: str):
        # Retrieve relevant context based on user query
        relevant_context = retrieve_relevant_context(vector_store, user_query)

        print("*" * 20)
        print("With user_query: ", user_query)
        print("The relevant context is: ", relevant_context)
        print("*" * 20)

        enhanced_prompt = f"""
        You are a helpful assistant that can answer questions about the data in the database or the internet.
        If you need to query the database, you should be looking into the `Adventureworks` database, `sales` schema.
        
        Based on the user's question, here is the most relevant schema documentation:
        
        {relevant_context}
        
        Use this documentation to understand the table structure and relationships when writing SQL queries.
        Focus on the information provided above as it's most relevant to the current query.
        """

        return create_react_agent(
            model="anthropic:claude-3-7-sonnet-latest",
            tools=tools,
            prompt=enhanced_prompt,
        )

    # Example query
    user_query = "What is the total sales in different territories in 2012?"
    print(f"Processing query: {user_query}")

    # Create agent with RAG-enhanced context
    agent = create_enhanced_agent_with_rag(user_query)

    # Use astream() for async streaming responses
    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": user_query}]}
    ):
        print(chunk)
        print("---" * 20)


# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
