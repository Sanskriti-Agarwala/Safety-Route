from typing import Dict, Any, List, Optional, Literal
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
from collections import defaultdict

from app.ai.claude_client import ClaudeClient


class AIProvider(str, Enum):
    CLAUDE = "claude"
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"


class TaskType(str, Enum):
    ROUTE_SAFETY_SCORING = "route_safety_scoring"
    ROUTE_COMPARISON = "route_comparison"
    REROUTE_DECISION = "reroute_decision"
    TRIP_SUMMARY = "trip_summary"
    SOS_MESSAGE = "sos_message"
    ROUTE_EXPLANATION = "route_explanation"
    REPORT_VALIDATION = "report_validation"


class TaskComplexity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AIOrchestrator:
    def __init__(
        self,
        claude_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        enable_caching: bool = True,
        cache_ttl_minutes: int = 5
    ):
        self.providers = {}
        self.provider_health = defaultdict(lambda: {"available": True, "failures": 0, "last_check": None})
        self.task_routing = self._initialize_task_routing()
        
        if claude_api_key:
            try:
                self.providers[AIProvider.CLAUDE] = ClaudeClient(api_key=claude_api_key)
            except Exception as e:
                print(f"Failed to initialize Claude: {e}")
        
        self.enable_caching = enable_caching
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.cache = {}
        
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "provider_usage": defaultdict(int),
            "task_counts": defaultdict(int),
            "failures": defaultdict(int)
        }
    
    
    def _initialize_task_routing(self) -> Dict[TaskType, Dict[str, Any]]:
        return {
            TaskType.ROUTE_SAFETY_SCORING: {
                "complexity": TaskComplexity.HIGH,
                "preferred_providers": [AIProvider.CLAUDE],
                "requires_json": True,
                "cacheable": True,
                "timeout_seconds": 10
            },
            TaskType.ROUTE_COMPARISON: {
                "complexity": TaskComplexity.HIGH,
                "preferred_providers": [AIProvider.CLAUDE],
                "requires_json": True,
                "cacheable": True,
                "timeout_seconds": 15
            },
            TaskType.REROUTE_DECISION: {
                "complexity": TaskComplexity.CRITICAL,
                "preferred_providers": [AIProvider.CLAUDE],
                "requires_json": True,
                "cacheable": False,
                "timeout_seconds": 8
            },
            TaskType.TRIP_SUMMARY: {
                "complexity": TaskComplexity.MEDIUM,
                "preferred_providers": [AIProvider.CLAUDE],
                "requires_json": True,
                "cacheable": True,
                "timeout_seconds": 10
            },
            TaskType.SOS_MESSAGE: {
                "complexity": TaskComplexity.CRITICAL,
                "preferred_providers": [AIProvider.CLAUDE],
                "requires_json": False,
                "cacheable": False,
                "timeout_seconds": 5
            },
            TaskType.ROUTE_EXPLANATION: {
                "complexity": TaskComplexity.LOW,
                "preferred_providers": [AIProvider.CLAUDE],
                "requires_json": False,
                "cacheable": True,
                "timeout_seconds": 8
            },
            TaskType.REPORT_VALIDATION: {
                "complexity": TaskComplexity.MEDIUM,
                "preferred_providers": [AIProvider.CLAUDE],
                "requires_json": True,
                "cacheable": True,
                "timeout_seconds": 7
            }
        }
    
    
    def _get_cache_key(self, task_type: TaskType, **kwargs) -> str:
        content = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(f"{task_type}:{content}".encode()).hexdigest()
    
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        if not self.enable_caching or cache_key not in self.cache:
            return None
        
        cached_entry = self.cache[cache_key]
        if datetime.utcnow() - cached_entry["timestamp"] > self.cache_ttl:
            del self.cache[cache_key]
            return None
        
        self.stats["cache_hits"] += 1
        return cached_entry["data"]
    
    
    def _set_cache(self, cache_key: str, data: Dict[str, Any]):
        if self.enable_caching:
            self.cache[cache_key] = {
                "data": data,
                "timestamp": datetime.utcnow()
            }
    
    
    def _select_provider(self, task_type: TaskType) -> Optional[AIProvider]:
        task_config = self.task_routing.get(task_type)
        if not task_config:
            return None
        
        for provider in task_config["preferred_providers"]:
            if provider in self.providers and self.provider_health[provider]["available"]:
                return provider
        
        for provider in self.providers:
            if self.provider_health[provider]["available"]:
                return provider
        
        return None
    
    
    def _mark_provider_failure(self, provider: AIProvider):
        self.provider_health[provider]["failures"] += 1
        self.stats["failures"][provider] += 1
        
        if self.provider_health[provider]["failures"] >= 3:
            self.provider_health[provider]["available"] = False
            self.provider_health[provider]["last_check"] = datetime.utcnow()
    
    
    def _maybe_recover_provider(self, provider: AIProvider):
        health = self.provider_health[provider]
        if not health["available"] and health["last_check"]:
            if datetime.utcnow() - health["last_check"] > timedelta(minutes=5):
                health["available"] = True
                health["failures"] = 0
    
    
    def score_route_safety(
        self,
        route_data: Dict[str, Any],
        reports: List[Dict[str, Any]],
        time_of_day: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        task_type = TaskType.ROUTE_SAFETY_SCORING
        self.stats["total_requests"] += 1
        self.stats["task_counts"][task_type] += 1
        
        cache_key = self._get_cache_key(
            task_type,
            route=route_data,
            reports=reports,
            time=time_of_day,
            prefs=user_preferences
        )
        
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            cached_result["_cache_hit"] = True
            return cached_result
        
        self.stats["cache_misses"] += 1
        
        provider = self._select_provider(task_type)
        if not provider:
            return self._get_fallback_response(task_type)
        
        try:
            if provider == AIProvider.CLAUDE:
                result = self.providers[provider].score_route_safety(
                    route_data, reports, time_of_day, user_preferences
                )
            else:
                result = self._get_fallback_response(task_type)
            
            self.stats["provider_usage"][provider] += 1
            self._set_cache(cache_key, result)
            result["_provider"] = provider
            result["_cache_hit"] = False
            
            return result
        
        except Exception as e:
            self._mark_provider_failure(provider)
            return self._get_fallback_response(task_type, error=str(e))
    
    
    def compare_routes(
        self,
        routes: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        task_type = TaskType.ROUTE_COMPARISON
        self.stats["total_requests"] += 1
        self.stats["task_counts"][task_type] += 1
        
        cache_key = self._get_cache_key(task_type, routes=routes, context=context)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            cached_result["_cache_hit"] = True
            return cached_result
        
        self.stats["cache_misses"] += 1
        
        provider = self._select_provider(task_type)
        if not provider:
            return self._get_fallback_response(task_type)
        
        try:
            if provider == AIProvider.CLAUDE:
                result = self.providers[provider].compare_routes(routes, context)
            else:
                result = self._get_fallback_response(task_type)
            
            self.stats["provider_usage"][provider] += 1
            self._set_cache(cache_key, result)
            result["_provider"] = provider
            result["_cache_hit"] = False
            
            return result
        
        except Exception as e:
            self._mark_provider_failure(provider)
            return self._get_fallback_response(task_type, error=str(e))
    
    
    def decide_reroute(
        self,
        current_route: Dict[str, Any],
        new_reports: List[Dict[str, Any]],
        user_location: Dict[str, float],
        eta_remaining: int
    ) -> Dict[str, Any]:
        task_type = TaskType.REROUTE_DECISION
        self.stats["total_requests"] += 1
        self.stats["task_counts"][task_type] += 1
        
        provider = self._select_provider(task_type)
        if not provider:
            return self._get_fallback_response(task_type)
        
        try:
            if provider == AIProvider.CLAUDE:
                result = self.providers[provider].decide_reroute(
                    current_route, new_reports, user_location, eta_remaining
                )
            else:
                result = self._get_fallback_response(task_type)
            
            self.stats["provider_usage"][provider] += 1
            result["_provider"] = provider
            
            return result
        
        except Exception as e:
            self._mark_provider_failure(provider)
            return self._get_fallback_response(task_type, error=str(e))
    
    
    def generate_trip_summary(
        self,
        trip_data: Dict[str, Any],
        incidents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        task_type = TaskType.TRIP_SUMMARY
        self.stats["total_requests"] += 1
        self.stats["task_counts"][task_type] += 1
        
        cache_key = self._get_cache_key(task_type, trip=trip_data, incidents=incidents)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            cached_result["_cache_hit"] = True
            return cached_result
        
        self.stats["cache_misses"] += 1
        
        provider = self._select_provider(task_type)
        if not provider:
            return self._get_fallback_response(task_type)
        
        try:
            if provider == AIProvider.CLAUDE:
                result = self.providers[provider].generate_trip_summary(trip_data, incidents)
            else:
                result = self._get_fallback_response(task_type)
            
            self.stats["provider_usage"][provider] += 1
            self._set_cache(cache_key, result)
            result["_provider"] = provider
            result["_cache_hit"] = False
            
            return result
        
        except Exception as e:
            self._mark_provider_failure(provider)
            return self._get_fallback_response(task_type, error=str(e))
    
    
    def generate_sos_message(
        self,
        location: Dict[str, float],
        user_info: Optional[Dict[str, Any]] = None,
        context: Optional[str] = None
    ) -> str:
        task_type = TaskType.SOS_MESSAGE
        self.stats["total_requests"] += 1
        self.stats["task_counts"][task_type] += 1
        
        provider = self._select_provider(task_type)
        if not provider:
            lat = location.get("latitude", 0)
            lon = location.get("longitude", 0)
            return f"🚨 EMERGENCY: I need immediate help. My location: {lat}, {lon}. Please send assistance."
        
        try:
            if provider == AIProvider.CLAUDE:
                message = self.providers[provider].generate_sos_message(location, user_info, context)
            else:
                lat = location.get("latitude", 0)
                lon = location.get("longitude", 0)
                message = f"🚨 EMERGENCY: I need immediate help. My location: {lat}, {lon}. Please send assistance."
            
            self.stats["provider_usage"][provider] += 1
            return message
        
        except Exception as e:
            self._mark_provider_failure(provider)
            lat = location.get("latitude", 0)
            lon = location.get("longitude", 0)
            return f"🚨 EMERGENCY: I need immediate help. My location: {lat}, {lon}. Please send assistance."
    
    
    def explain_route_choice(
        self,
        chosen_route: Dict[str, Any],
        alternative_routes: List[Dict[str, Any]],
        decision_factors: Dict[str, Any]
    ) -> str:
        task_type = TaskType.ROUTE_EXPLANATION
        self.stats["total_requests"] += 1
        self.stats["task_counts"][task_type] += 1
        
        cache_key = self._get_cache_key(
            task_type,
            chosen=chosen_route,
            alternatives=alternative_routes,
            factors=decision_factors
        )
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            self.stats["cache_hits"] += 1
            return cached_result
        
        self.stats["cache_misses"] += 1
        
        provider = self._select_provider(task_type)
        if not provider:
            return "This route was selected based on safety considerations."
        
        try:
            if provider == AIProvider.CLAUDE:
                explanation = self.providers[provider].explain_route_choice(
                    chosen_route, alternative_routes, decision_factors
                )
            else:
                explanation = "This route was selected based on safety considerations."
            
            self.stats["provider_usage"][provider] += 1
            self._set_cache(cache_key, explanation)
            
            return explanation
        
        except Exception as e:
            self._mark_provider_failure(provider)
            return "This route was selected based on safety considerations."
    
    
    def classify_report_validity(self, report: Dict[str, Any]) -> Dict[str, Any]:
        task_type = TaskType.REPORT_VALIDATION
        self.stats["total_requests"] += 1
        self.stats["task_counts"][task_type] += 1
        
        cache_key = self._get_cache_key(task_type, report=report)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            cached_result["_cache_hit"] = True
            return cached_result
        
        self.stats["cache_misses"] += 1
        
        provider = self._select_provider(task_type)
        if not provider:
            return self._get_fallback_response(task_type)
        
        try:
            if provider == AIProvider.CLAUDE:
                result = self.providers[provider].classify_report_validity(report)
            else:
                result = self._get_fallback_response(task_type)
            
            self.stats["provider_usage"][provider] += 1
            self._set_cache(cache_key, result)
            result["_provider"] = provider
            result["_cache_hit"] = False
            
            return result
        
        except Exception as e:
            self._mark_provider_failure(provider)
            return self._get_fallback_response(task_type, error=str(e))
    
    
    def _get_fallback_response(self, task_type: TaskType, error: Optional[str] = None) -> Dict[str, Any]:
        fallbacks = {
            TaskType.ROUTE_SAFETY_SCORING: {
                "safety_score": 50,
                "risk_level": "moderate",
                "risk_factors": ["AI unavailable - using conservative estimate"],
                "positive_factors": [],
                "night_safety_concern": False,
                "recommended_action": "proceed",
                "explanation": "Unable to perform detailed AI analysis. Using conservative safety rating."
            },
            TaskType.ROUTE_COMPARISON: {
                "recommended_route_index": 0,
                "reasoning": "AI unavailable - selecting first route as default",
                "route_rankings": [],
                "safety_tradeoff": "Please verify route safety manually",
                "user_warning": "AI comparison unavailable"
            },
            TaskType.REROUTE_DECISION: {
                "should_reroute": True,
                "urgency": "medium",
                "reason": "New reports detected - AI unavailable for detailed analysis",
                "affected_segment": "Unknown area",
                "user_message": "Safety reports detected on route. Suggesting alternative path.",
                "alternative_action": "find_alternative"
            },
            TaskType.TRIP_SUMMARY: {
                "overall_safety_rating": "safe",
                "summary": "Trip completed successfully.",
                "safety_highlights": [],
                "areas_of_concern": [],
                "suggestions_for_next_time": [],
                "commendations": "Stay safe on your travels!"
            },
            TaskType.REPORT_VALIDATION: {
                "is_valid": True,
                "confidence": 0.5,
                "classification": "unclear",
                "suggested_category": "other",
                "severity_assessment": 3,
                "reasoning": "AI validation unavailable - accepting report by default"
            }
        }
        
        response = fallbacks.get(task_type, {})
        response["_fallback"] = True
        if error:
            response["_error"] = error
        
        return response
    
    
    def get_orchestrator_stats(self) -> Dict[str, Any]:
        return {
            **self.stats,
            "cache_hit_rate": (
                self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["cache_misses"])
                if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0
                else 0
            ),
            "provider_health": dict(self.provider_health),
            "cache_size": len(self.cache),
            "available_providers": [p for p in self.providers.keys()]
        }
    
    
    def clear_cache(self):
        self.cache.clear()
        self.stats["cache_hits"] = 0
        self.stats["cache_misses"] = 0