# Agentic System Demo

A RAG-enhanced agentic system that combines database querying capabilities with web search to answer questions about sales data from the AdventureWorks database.

## Overview

This project demonstrates an advanced hierarchical multi-agent system that can:
- **Hierarchical Coordination**: Supervisor agent intelligently delegates tasks to specialized agents
- **Memory Persistence**: Maintains conversation context across sessions using SQLite checkpointer
- **Database Integration**: Query PostgreSQL databases using MCP (Model Context Protocol)
- **Web Search**: Search the internet using Tavily Search via specialized general agent
- **RAG Enhancement**: Use RAG (Retrieval-Augmented Generation) to provide context-aware responses
- **Intelligent Routing**: Automatically route queries to appropriate specialized agents
- **Task Decomposition**: Break complex queries into manageable subtasks

## Features

- **Hierarchical Supervisor**: Coordinates task delegation and monitors execution across specialized agents
- **Memory Persistence**: SQLite checkpointer maintains conversation state across sessions
- **Specialized Agents**: Purpose-built agents for general queries, data analysis, and web research
- **RAG System**: Uses FAISS vector store with OpenAI embeddings to provide relevant schema documentation context
- **PostgreSQL Integration**: MCP client for direct database interactions with AdventureWorks sales data
- **Intelligent Routing**: Automatic agent selection based on query complexity and type
- **Task Decomposition**: Breaks complex queries into manageable, coordinated subtasks
- **Schema-Aware**: Automatically retrieves relevant database schema information based on user queries

## Architecture

The enhanced hierarchical system consists of several key components:

1. **Supervisor Agent** (`SupervisorAgent`): Orchestrates task coordination, decomposition, and delegation
2. **General Agent** (`GeneralAgent`): Handles general queries, basic database operations, and web search
3. **Data Analyst Agent** (`DataAnalystAgent`): Specialized for statistical analysis, reporting, and business insights
4. **RAG System** (`create_rag_system`): Creates a vector store from sales schema documentation
5. **Memory Persistence** (`SqliteSaver`): Maintains conversation state across sessions
6. **MCP Client**: Connects to PostgreSQL database server
7. **Hierarchical Graph** (`HierarchicalSystem`): Coordinates agent interactions and workflow

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

Run the enhanced hierarchical system:
```bash
langgraph dev --allow-blocking
```

The system will:
1. Start the LangGraph development server
2. Initialize the hierarchical supervisor with specialized agents
3. Set up memory persistence with SQLite checkpointer
4. Create RAG-enhanced context from sales schema documentation
5. Provide intelligent task coordination and delegation

Access the system via the LangGraph Studio interface or API calls to the `agent_system` graph.

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
The project includes `langgraph.json` for graph deployment configuration with the `agent_system` graph endpoint.

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