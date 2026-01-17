from app.ai.openai_client import call_llm
from typing import Optional, Dict
import json
import re


class SafetyReasoningAgent:
    def __init__(self):
        pass
    
    def analyze_safety_risk(
        self,
        risk_score: int,
        time_of_day: Optional[str] = None,
        route_name: Optional[str] = None,
        location_label: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Analyze safety risk using AI reasoning.
        """
        context_parts = []
        if time_of_day:
            context_parts.append(f"Time: {time_of_day}")
        if route_name:
            context_parts.append(f"Route: {route_name}")
        if location_label:
            context_parts.append(f"Location: {location_label}")

        context_str = " | ".join(context_parts) if context_parts else "No additional context"

        prompt = f"""You are a safety reasoning agent for a navigation system.

Risk Score: {risk_score}/100 (0 = very safe, 100 = extremely dangerous)
Context: {context_str}

Task:
1. Classify risk level as:
   - "low" (0–30)
   - "medium" (31–70)
   - "high" (71–100)
2. Provide a clear 1–2 sentence explanation
3. Recommend an action (continue, use caution, or reroute)

Respond ONLY with valid JSON:
{{
  "risk_level": "low|medium|high",
  "explanation": "brief safety explanation",
  "recommendation": "specific action recommendation"
}}"""

        response = call_llm(prompt, max_tokens=300, temperature=0.3)

        try:
            clean_response = re.sub(r"```json|```", "", response).strip()
            result = json.loads(clean_response)

            return {
                "risk_level": result.get("risk_level", "medium"),
                "explanation": result.get(
                    "explanation", "Unable to assess safety conditions."
                ),
                "recommendation": result.get(
                    "recommendation", "Proceed with caution."
                )
            }

        except Exception:
            return {
                "risk_level": "medium",
                "explanation": "Safety analysis temporarily unavailable.",
                "recommendation": "Proceed with caution and stay alert."
            }