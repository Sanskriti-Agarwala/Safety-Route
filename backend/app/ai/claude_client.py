import os
import json
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
import anthropic
from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError
import time


class ClaudeClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 2000,
        temperature: float = 0.7
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.request_count = 0
        self.total_tokens = 0
    
    
    def _make_request(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        for attempt in range(max_retries):
            try:
                request_params = {
                    "model": self.model,
                    "max_tokens": tokens,
                    "temperature": temp,
                    "messages": messages
                }
                
                if system:
                    request_params["system"] = system
                
                response = self.client.messages.create(**request_params)
                
                self.request_count += 1
                self.total_tokens += response.usage.input_tokens + response.usage.output_tokens
                
                return {
                    "content": response.content[0].text,
                    "model": response.model,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens
                    },
                    "stop_reason": response.stop_reason
                }
            
            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                raise e
            
            except (APIError, APIConnectionError) as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                raise e
        
        raise Exception("Max retries exceeded")
    
    
    def score_route_safety(
        self,
        route_data: Dict[str, Any],
        reports: List[Dict[str, Any]],
        time_of_day: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        system_prompt = """You are a safety routing AI assistant specialized in evaluating route safety.
Your task is to analyze route data, community safety reports, and contextual factors to provide a safety assessment.
You must respond ONLY with valid JSON. Do not include any markdown, preambles, or explanations outside the JSON."""
        
        user_prompt = f"""Analyze this route for safety:

Route Information:
{json.dumps(route_data, indent=2)}

Community Safety Reports:
{json.dumps(reports, indent=2)}

Time of Day: {time_of_day}
User Preferences: {json.dumps(user_preferences or {}, indent=2)}

Provide a comprehensive safety assessment in JSON format with:
{{
    "safety_score": <integer 0-100, where 0=very safe, 100=very dangerous>,
    "risk_level": "<safe|moderate|risky|dangerous>",
    "risk_factors": ["list of identified risks"],
    "positive_factors": ["list of safety advantages"],
    "night_safety_concern": <boolean>,
    "recommended_action": "<proceed|warn_user|suggest_alternative>",
    "explanation": "<2-3 sentence clear explanation of the assessment>"
}}"""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self._make_request(
            messages=messages,
            system=system_prompt,
            temperature=0.3
        )
        
        try:
            content = response["content"].strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(content)
            result["_metadata"] = {
                "model": response["model"],
                "tokens_used": response["usage"]["input_tokens"] + response["usage"]["output_tokens"]
            }
            return result
        
        except json.JSONDecodeError as e:
            return {
                "safety_score": 50,
                "risk_level": "moderate",
                "risk_factors": ["Unable to parse AI response"],
                "positive_factors": [],
                "night_safety_concern": False,
                "recommended_action": "warn_user",
                "explanation": "AI assessment failed, using conservative moderate risk rating.",
                "error": str(e),
                "raw_response": response["content"]
            }
    
    
    def compare_routes(
        self,
        routes: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        system_prompt = """You are a safety routing AI that helps users choose the safest route.
Compare multiple routes and recommend the best option considering safety, time, and user context.
Respond ONLY with valid JSON."""
        
        user_prompt = f"""Compare these routes and recommend the safest option:

Routes:
{json.dumps(routes, indent=2)}

Context:
{json.dumps(context, indent=2)}

Provide comparison in JSON format:
{{
    "recommended_route_index": <integer index of safest route>,
    "reasoning": "<clear explanation why this route is safest>",
    "route_rankings": [
        {{
            "route_index": <integer>,
            "safety_score": <0-100>,
            "pros": ["list of advantages"],
            "cons": ["list of disadvantages"]
        }}
    ],
    "safety_tradeoff": "<explanation of any time vs safety tradeoffs>",
    "user_warning": "<optional warning message if all routes have concerns>"
}}"""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self._make_request(
            messages=messages,
            system=system_prompt,
            temperature=0.4
        )
        
        try:
            content = response["content"].strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "recommended_route_index": 0,
                "reasoning": "Unable to parse AI comparison",
                "route_rankings": [],
                "safety_tradeoff": "AI analysis unavailable",
                "error": "JSON parse error"
            }
    
    
    def decide_reroute(
        self,
        current_route: Dict[str, Any],
        new_reports: List[Dict[str, Any]],
        user_location: Dict[str, float],
        eta_remaining: int
    ) -> Dict[str, Any]:
        system_prompt = """You are a real-time safety decision AI for navigation.
Analyze incoming safety reports and decide if immediate rerouting is necessary.
Prioritize user safety while minimizing unnecessary disruptions.
Respond ONLY with valid JSON."""
        
        user_prompt = f"""New safety reports detected along the current route:

Current Route: {json.dumps(current_route, indent=2)}
New Reports: {json.dumps(new_reports, indent=2)}
User Location: {json.dumps(user_location, indent=2)}
ETA Remaining: {eta_remaining} minutes

Make a rerouting decision in JSON format:
{{
    "should_reroute": <boolean>,
    "urgency": "<low|medium|high|critical>",
    "reason": "<clear explanation for the decision>",
    "affected_segment": "<description of dangerous area>",
    "user_message": "<friendly message to show user>",
    "alternative_action": "<continue_with_caution|find_alternative|contact_emergency>"
}}"""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self._make_request(
            messages=messages,
            system=system_prompt,
            temperature=0.2
        )
        
        try:
            content = response["content"].strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "should_reroute": True,
                "urgency": "medium",
                "reason": "New safety reports detected",
                "affected_segment": "Unknown area",
                "user_message": "New safety concerns detected. Finding safer route...",
                "alternative_action": "find_alternative"
            }
    
    
    def generate_trip_summary(
        self,
        trip_data: Dict[str, Any],
        incidents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        system_prompt = """You are a safety assistant that creates helpful post-trip summaries.
Provide constructive feedback and safety suggestions in a friendly, encouraging tone.
Respond ONLY with valid JSON."""
        
        user_prompt = f"""Generate a trip summary:

Trip Data: {json.dumps(trip_data, indent=2)}
Incidents/Reports Encountered: {json.dumps(incidents, indent=2)}

Create a summary in JSON format:
{{
    "overall_safety_rating": "<safe|mostly_safe|some_concerns|unsafe>",
    "summary": "<2-3 sentence trip overview>",
    "safety_highlights": ["positive safety aspects of the trip"],
    "areas_of_concern": ["any safety issues encountered"],
    "suggestions_for_next_time": ["helpful tips for future trips"],
    "commendations": "<positive message if user made safe choices>"
}}"""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self._make_request(
            messages=messages,
            system=system_prompt,
            temperature=0.6
        )
        
        try:
            content = response["content"].strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "overall_safety_rating": "safe",
                "summary": "Trip completed successfully.",
                "safety_highlights": [],
                "areas_of_concern": [],
                "suggestions_for_next_time": [],
                "commendations": "Great job completing your trip!"
            }
    
    
    def generate_sos_message(
        self,
        location: Dict[str, float],
        user_info: Optional[Dict[str, Any]] = None,
        context: Optional[str] = None
    ) -> str:
        system_prompt = """You are an emergency assistant that generates clear, concise SOS messages.
Create messages that are immediately understandable by emergency contacts or responders."""
        
        user_prompt = f"""Generate an emergency SOS message:

Location: {json.dumps(location, indent=2)}
User Info: {json.dumps(user_info or {}, indent=2)}
Context: {context or "Emergency assistance needed"}

Create a clear, urgent message (2-3 sentences max) that includes:
- Clear statement of emergency
- Precise location
- Any relevant context
Keep it concise and actionable."""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self._make_request(
            messages=messages,
            system=system_prompt,
            temperature=0.3,
            max_tokens=300
        )
        
        return response["content"].strip()
    
    
    def explain_route_choice(
        self,
        chosen_route: Dict[str, Any],
        alternative_routes: List[Dict[str, Any]],
        decision_factors: Dict[str, Any]
    ) -> str:
        system_prompt = """You are a friendly navigation assistant explaining routing decisions.
Explain choices in simple, conversational language that builds user trust."""
        
        user_prompt = f"""Explain why this route was chosen:

Chosen Route: {json.dumps(chosen_route, indent=2)}
Alternative Routes: {json.dumps(alternative_routes, indent=2)}
Decision Factors: {json.dumps(decision_factors, indent=2)}

Provide a friendly 2-4 sentence explanation that:
- Highlights the safety advantages
- Acknowledges any tradeoffs (e.g., slightly longer time)
- Builds confidence in the choice
Keep it conversational and reassuring."""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self._make_request(
            messages=messages,
            system=system_prompt,
            temperature=0.7,
            max_tokens=400
        )
        
        return response["content"].strip()
    
    
    def classify_report_validity(
        self,
        report: Dict[str, Any]
    ) -> Dict[str, Any]:
        system_prompt = """You are a content moderation AI for safety reports.
Evaluate if reports are legitimate safety concerns or spam/abuse.
Respond ONLY with valid JSON."""
        
        user_prompt = f"""Evaluate this safety report:

{json.dumps(report, indent=2)}

Classify in JSON format:
{{
    "is_valid": <boolean>,
    "confidence": <0.0-1.0>,
    "classification": "<legitimate|spam|unclear|inappropriate>",
    "suggested_category": "<corrected category if misclassified>",
    "severity_assessment": <1-5>,
    "reasoning": "<brief explanation>"
}}"""
        
        messages = [{"role": "user", "content": user_prompt}]
        
        response = self._make_request(
            messages=messages,
            system=system_prompt,
            temperature=0.3
        )
        
        try:
            content = response["content"].strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "is_valid": True,
                "confidence": 0.5,
                "classification": "unclear",
                "suggested_category": report.get("category", "other"),
                "severity_assessment": report.get("severity", 3),
                "reasoning": "Unable to validate"
            }
    
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_requests": self.request_count,
            "total_tokens_used": self.total_tokens,
            "model": self.model
        }