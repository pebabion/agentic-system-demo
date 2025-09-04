# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Install dependencies
```bash
uv sync
```

### Run the application (development mode)
```bash
langgraph dev --allow-blocking
```

### Run Python scripts
```bash
uv run python <script.py>
```

## Architecture Overview

This is a hierarchical multi-agent system built with LangGraph that provides RAG-enhanced database querying and web search capabilities. The system architecture follows a supervisor pattern with specialized agents for different tasks.

### Core Components

1. **Hierarchical Supervisor System** (`enhanced_graph.py`)
   - Main entry point via `make_enhanced_graph()` function
   - Orchestrates task delegation between agents
   - Uses SQLite for memory persistence (`agent_memory.db`)

2. **Agent Hierarchy** (`agents/` directory)
   - `BaseAgent`: Abstract base class for all agents
   - `SupervisorAgent`: Orchestrates task coordination and delegation
   - `GeneralAgent`: Handles general queries and web search (via Tavily)
   - `DataAnalystAgent`: Specialized for statistical analysis and reporting

3. **RAG System**
   - Uses FAISS vector store with OpenAI embeddings
   - Sources context from `sales_schema_documentation.md`
   - Provides schema-aware query enhancement

4. **Database Integration**
   - MCP (Model Context Protocol) client for PostgreSQL
   - Connects to AdventureWorks database at `postgresql://postgres:secret@localhost:54321/Adventureworks`

### Key Files

- `enhanced_graph.py`: Main graph configuration and system initialization
- `agents/`: Agent implementations
- `sales_schema_documentation.md`: Database schema documentation for RAG
- `langgraph.json`: LangGraph deployment configuration
- `.env`: Environment variables (OPENAI_API_KEY, TAVILY_API_KEY)

### Environment Requirements

- Python 3.12+
- PostgreSQL with AdventureWorks database
- Required API keys in `.env`:
  - `OPENAI_API_KEY`
  - `TAVILY_API_KEY`