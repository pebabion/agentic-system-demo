"""Supervisor agent for hierarchical coordination."""

import asyncio
from typing import Dict, List, Any, Optional, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent

from .base_agent import BaseAgent


class SupervisorAgent(BaseAgent):
    """Supervisor agent that coordinates and delegates tasks to specialized agents."""
    
    def __init__(self, vector_store=None):
        super().__init__(
            agent_id="supervisor",
            name="Supervisor Agent", 
            description="Coordinates tasks and delegates to specialized agents",
            vector_store=vector_store
        )
        self.available_agents = {
            "general_agent": "General purpose agent for basic queries and web search",
            "data_analyst": "Specialized agent for data analysis, reporting, and insights"
        }
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    def route_query(self, query: str) -> Literal["general_agent", "data_analyst"]:
        """Route queries to appropriate agents based on content analysis."""
        query_lower = query.lower()
        
        # Keywords that indicate data analysis tasks
        analysis_keywords = [
            "analyze", "analysis", "statistics", "report", "trend",
            "pattern", "aggregate", "summary", "insights", "metrics",
            "performance", "calculate", "sum", "average", "count",
            "total", "sales", "revenue", "data", "chart", "graph"
        ]
        
        # Check if query contains analysis keywords
        if any(keyword in query_lower for keyword in analysis_keywords):
            return "data_analyst"
        else:
            return "general_agent"
    
    async def decompose_task(self, query: str) -> Dict[str, Any]:
        """Decompose complex tasks into smaller, manageable subtasks."""
        decomposition_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a supervisor agent that decomposes complex queries into manageable subtasks.
            
            Analyze the user query and determine:
            1. Task complexity (simple/medium/complex)
            2. Required agent type (general_agent or data_analyst)
            3. Subtasks if the task is complex
            4. Dependencies between subtasks
            5. Expected deliverables
            
            Available agents:
            - general_agent: General queries, web search, basic database lookups
            - data_analyst: Statistical analysis, reporting, data insights, complex SQL queries
            
            Respond in JSON format with:
            {{
                "complexity": "simple|medium|complex",
                "primary_agent": "general_agent|data_analyst", 
                "subtasks": [
                    {{
                        "id": "task_1",
                        "description": "Task description",
                        "agent": "agent_type",
                        "dependencies": [],
                        "priority": 1
                    }}
                ],
                "expected_output": "Description of expected deliverables"
            }}
            """),
            ("user", "{query}")
        ])
        
        response = await self.llm.ainvoke(
            decomposition_prompt.format_messages(query=query)
        )
        
        try:
            import json
            return json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback to simple routing
            return {
                "complexity": "simple",
                "primary_agent": self.route_query(query),
                "subtasks": [{
                    "id": "main_task",
                    "description": query,
                    "agent": self.route_query(query),
                    "dependencies": [],
                    "priority": 1
                }],
                "expected_output": "Direct response to user query"
            }
    
    async def create_delegation_plan(self, task_breakdown: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create execution plan based on task breakdown."""
        execution_plan = []
        
        # Sort subtasks by priority and dependencies
        subtasks = sorted(
            task_breakdown["subtasks"], 
            key=lambda x: (len(x["dependencies"]), x["priority"])
        )
        
        for i, subtask in enumerate(subtasks):
            plan_item = {
                "step": i + 1,
                "task_id": subtask["id"],
                "description": subtask["description"],
                "assigned_agent": subtask["agent"],
                "dependencies": subtask["dependencies"],
                "status": "pending",
                "result": None
            }
            execution_plan.append(plan_item)
        
        return execution_plan
    
    async def monitor_execution(self, execution_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Monitor and coordinate the execution of delegated tasks."""
        results = {"steps": [], "final_output": "", "status": "in_progress"}
        
        for step in execution_plan:
            # Check if dependencies are completed
            if step["dependencies"]:
                incomplete_deps = [
                    dep for dep in step["dependencies"] 
                    if not any(s["task_id"] == dep and s["status"] == "completed" 
                             for s in results["steps"])
                ]
                if incomplete_deps:
                    step["status"] = "waiting_for_dependencies"
                    step["result"] = f"Waiting for: {', '.join(incomplete_deps)}"
                    results["steps"].append(step)
                    continue
            
            # Execute the step (this would delegate to the appropriate agent)
            step["status"] = "in_progress"
            results["steps"].append(step.copy())
            
            # Simulate delegation result (in real implementation, this would call the agent)
            step["result"] = f"Task '{step['description']}' assigned to {step['assigned_agent']}"
            step["status"] = "delegated"
        
        results["status"] = "delegated" 
        return results
    
    async def synthesize_results(self, execution_results: Dict[str, Any], original_query: str) -> str:
        """Synthesize results from multiple agents into a coherent response."""
        synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a supervisor agent synthesizing results from multiple specialized agents.
            
            Your task is to:
            1. Combine the results from different agents
            2. Ensure consistency and coherence
            3. Provide a comprehensive answer to the original query
            4. Highlight key insights and findings
            
            Present the final response in a clear, structured format."""),
            ("user", """
            Original Query: {query}
            
            Execution Results: {results}
            
            Please synthesize these results into a comprehensive response.
            """)
        ])
        
        response = await self.llm.ainvoke(
            synthesis_prompt.format_messages(
                query=original_query,
                results=str(execution_results)
            )
        )
        
        return response.content
    
    async def process_message(self, messages: List[BaseMessage]) -> Dict[str, Any]:
        """Process messages through the hierarchical coordination workflow."""
        if not messages:
            return {"messages": [AIMessage(content="No messages to process.")]}
        
        # Get the latest user message
        latest_message = messages[-1]
        if hasattr(latest_message, 'content'):
            query = latest_message.content
        else:
            query = str(latest_message)
        
        # Step 1: Decompose the task
        task_breakdown = await self.decompose_task(query)
        
        # Step 2: Create execution plan
        execution_plan = await self.create_delegation_plan(task_breakdown)
        
        # Step 3: Monitor execution (delegate to agents)
        execution_results = await self.monitor_execution(execution_plan)
        
        # Step 4: Synthesize results
        final_response = await self.synthesize_results(execution_results, query)
        
        # For now, return the coordination plan and delegation info
        coordination_summary = f"""
## Task Coordination Summary

**Original Query:** {query}

**Task Complexity:** {task_breakdown['complexity']}

**Execution Plan:**
{chr(10).join([f"Step {step['step']}: {step['description']} → {step['assigned_agent']}" for step in execution_plan])}

**Status:** Tasks have been analyzed and delegation plan created.

**Next Steps:** The following agents will be coordinated:
{chr(10).join([f"- {step['assigned_agent']}: {step['description']}" for step in execution_plan])}

**Supervisor Coordination:** This query requires {task_breakdown['complexity']} coordination with {len(execution_plan)} subtask(s).
        """
        
        return {"messages": [AIMessage(content=coordination_summary)]}
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of all supervised agents."""
        return {
            "supervisor_id": self.agent_id,
            "available_agents": self.available_agents,
            "coordination_capabilities": [
                "Task decomposition",
                "Agent routing", 
                "Execution monitoring",
                "Result synthesis"
            ]
        }