"""Data analyst agent specialized in statistical analysis and reporting."""

from typing import Dict, List, Any
from langchain_core.messages import BaseMessage, AIMessage
from langgraph.prebuilt import create_react_agent

from .base_agent import BaseAgent


class DataAnalystAgent(BaseAgent):
    """Specialized agent for data analysis, statistical reporting, and business insights."""
    
    def __init__(self, vector_store=None):
        super().__init__(
            agent_id="data_analyst",
            name="Data Analyst Agent",
            description="Specialized in statistical analysis, reporting, and data insights",
            vector_store=vector_store
        )
        self.agent = None
    
    async def initialize(self):
        """Initialize the data analyst agent with specialized capabilities."""
        await super().initialize()
        
        # Get analysis-specific context
        sample_context = ""
        if self.vector_store:
            sample_context = await self.retrieve_context(
                "sales performance metrics analysis reporting statistics", k=3
            )
        
        # Create the specialized React agent
        self.agent = create_react_agent(
            model="anthropic:claude-3-7-sonnet-latest",
            tools=self.tools,  # Only database tools, no web search
            prompt=f"""
            You are a specialized Data Analyst AI assistant focused on statistical analysis and reporting.
            
            Your expertise includes:
            - Performing comprehensive data analysis and generating insights
            - Creating statistical summaries and detailed reports
            - Identifying trends, patterns, and anomalies in data
            - Calculating key performance metrics (KPIs)
            - Providing actionable business intelligence
            - Creating data visualizations and summaries
            - Comparative analysis across time periods and segments
            
            Database context: You work with the `Adventureworks` database, `sales` schema.
            
            Relevant schema information:
            {sample_context}
            
            When handling queries, you should:
            1. **Ask clarifying questions** if the analysis scope is unclear
            2. **Use appropriate SQL queries** to gather comprehensive data
            3. **Perform statistical calculations** (averages, totals, percentages, growth rates)
            4. **Identify trends and patterns** in the data
            5. **Provide business insights** and recommendations
            6. **Format results clearly** with numbers, percentages, and key findings
            7. **Compare metrics** across different dimensions (time, geography, products, etc.)
            
            Always provide:
            - Clear numerical results with proper formatting
            - Trend analysis when relevant
            - Business context and implications
            - Actionable insights and recommendations
            
            Focus on delivering data-driven insights that support business decision-making.
            """,
        )
    
    async def generate_analysis_summary(self, query: str, raw_results: str) -> str:
        """Generate an executive summary of the analysis."""
        # This would typically use an LLM to create a summary
        # For now, return a structured format
        return f"""
## Data Analysis Summary

**Query Analyzed:** {query}

**Key Findings:**
{raw_results}

**Business Implications:**
- Analysis completed by specialized Data Analyst Agent
- Results include statistical insights and trends
- Recommendations based on data patterns identified

**Data Quality Notes:**
- Analysis performed on Adventureworks sales database
- Results reflect database state at time of query
        """
    
    async def process_message(self, messages: List[BaseMessage]) -> Dict[str, Any]:
        """Process messages through the data analyst agent."""
        if not self.agent:
            await self.initialize()
        
        # Execute the specialized agent
        result = await self.agent.ainvoke({"messages": messages})
        return result
    
    def get_capabilities(self) -> List[str]:
        """Return specific capabilities of the data analyst agent."""
        base_capabilities = super().get_capabilities()
        specific_capabilities = [
            "Statistical analysis and reporting",
            "Trend identification and pattern analysis",
            "Key Performance Indicator (KPI) calculation",
            "Comparative analysis across dimensions",
            "Business intelligence insights",
            "Data visualization recommendations",
            "Complex SQL query construction",
            "Time-series analysis",
            "Cohort and segment analysis",
            "Revenue and sales performance analysis"
        ]
        return base_capabilities + specific_capabilities
    
    async def perform_statistical_analysis(self, data_query: str) -> Dict[str, Any]:
        """Perform specialized statistical analysis on queried data."""
        # This would contain specific statistical operations
        # For now, return a structure indicating the type of analysis
        return {
            "analysis_type": "statistical_summary",
            "query": data_query,
            "capabilities_applied": [
                "Descriptive statistics",
                "Trend analysis", 
                "Comparative metrics",
                "Business insights"
            ],
            "status": "ready_for_execution"
        }