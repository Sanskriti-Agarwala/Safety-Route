from app.agents.route_generator_agent import RouteGeneratorAgent
from app.agents.safety_reasoning_agent import SafetyReasoningAgent
from app.agents.decision_agent import DecisionAgent
from app.ai.orchestrator import AIOrchestrator
import os

# Initialize
orchestrator = AIOrchestrator(claude_api_key=os.getenv("ANTHROPIC_API_KEY"))
route_agent = RouteGeneratorAgent(orchestrator)
safety_agent = SafetyReasoningAgent(orchestrator)
decision_agent = DecisionAgent(orchestrator)

# Test route generation
result = route_agent.plan_safe_route(
    start_lat=37.7749,
    start_lon=-122.4194,
    end_lat=37.8044,
    end_lon=-122.2712,
    community_reports=[]
)

print("✅ All agents working!")
print(f"Routes generated: {result['total_routes']}")