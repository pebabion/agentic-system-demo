# Agentic System Demo

A RAG-enhanced agentic system that combines database querying capabilities with web search to answer questions about sales data from the AdventureWorks database.

## Overview

This project demonstrates an intelligent agent system that can:
- Query PostgreSQL databases using MCP (Model Context Protocol)
- Search the internet using Tavily Search
- Use RAG (Retrieval-Augmented Generation) to provide context-aware responses
- Answer complex questions about sales data by combining database insights with web research

## Features

- **RAG System**: Uses FAISS vector store with OpenAI embeddings to provide relevant schema documentation context
- **Multi-Tool Agent**: LangGraph ReAct agent with database and web search capabilities
- **PostgreSQL Integration**: MCP client for direct database interactions with AdventureWorks sales data
- **Streaming Responses**: Asynchronous streaming for real-time agent responses
- **Schema-Aware**: Automatically retrieves relevant database schema information based on user queries

## Architecture

The system consists of several key components:

1. **RAG System** (`create_rag_system`): Creates a vector store from sales schema documentation
2. **Context Retrieval** (`retrieve_relevant_context`): Finds relevant schema information for queries
3. **Enhanced Agent** (`create_enhanced_agent_with_rag`): Combines RAG context with LangGraph agent
4. **MCP Client**: Connects to PostgreSQL database server
5. **Tavily Search**: Provides web search capabilities

## Prerequisites

- Python 3.12+
- PostgreSQL database with AdventureWorks sample data
- OpenAI API key for embeddings and language model
- Tavily API key for web search

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd agentic-system-demo
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Set up environment variables:
```bash
# Create .env file with:
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

4. Ensure PostgreSQL is running with AdventureWorks data:
```bash
# The system expects PostgreSQL at: postgresql://postgres:secret@localhost:54321/Adventureworks
```

## Usage

Run the demo:
```bash
python main.py
```

The system will:
1. Create a RAG vector store from the sales schema documentation
2. Initialize the MCP client for database connections
3. Set up tools (database queries + web search)
4. Process the example query: "What is the total sales in different territories in 2012?"
5. Stream the agent's response

## Configuration

### Database Connection
The PostgreSQL connection is configured in `main.py`:
```python
"postgres": {
    "command": "npx",
    "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://postgres:secret@localhost:54321/Adventureworks",
    ],
    "transport": "stdio",
}
```

### LangGraph Configuration
The project includes `langgraph.json` for graph deployment configuration.

## Dependencies

Key dependencies include:
- **LangChain**: Framework for LLM applications
- **LangGraph**: Agent workflow orchestration
- **FAISS**: Vector similarity search
- **MCP Adapters**: Model Context Protocol integration
- **Tavily**: Web search API
- **OpenAI**: Embeddings and language models

## Example Queries

The system can handle complex questions like:
- "What is the total sales in different territories in 2012?"
- "Which customers have the highest order values?"
- "What are the trends in online vs offline sales?"
- "Compare our sales performance with industry benchmarks" (combines DB + web search)

## Schema Documentation

The system uses `sales_schema_documentation.md` which contains detailed information about:
- Customer tables and relationships
- Sales order structures
- Territory and geographic data
- Product and pricing information

This documentation is automatically embedded and used to provide relevant context for database queries.

## Development

To extend the system:

1. **Add new tools**: Register additional tools in the `tools` list
2. **Modify RAG context**: Update `sales_schema_documentation.md` for better query understanding
3. **Customize prompts**: Adjust the enhanced prompt in `create_enhanced_agent_with_rag`
4. **Add new data sources**: Extend the MCP client configuration

## License

[Add your license information here]