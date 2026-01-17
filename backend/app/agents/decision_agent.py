from typing import Dict, Any, List, Optional
from datetime import datetime

from app.ai.orchestrator import AIOrchestrator
from app.services.safety_score_service import calculate_report_risk


class DecisionAgent:
    def __init__(self, ai_orchestrator: Optional[AIOrchestrator] = None):
        self.ai_orchestrator = ai_orchestrator
        self.reroute_threshold = 60
        self.warning_threshold = 50
    
    
    def should_reroute(
        self,
        current_route: Dict[str, Any],
        new_reports: List[Dict[str, Any]],
        user_location: Dict[str, float],
        eta_remaining: int
    ) -> Dict[str, Any]:
        """
        Decide if rerouting is necessary based on new safety reports.
        """
        report_analysis = calculate_report_risk(new_reports)
        
        critical_reports = [r for r in new_reports if r.get("severity", 1) >= 4]
        
        deterministic_decision = {
            "should_reroute": False,
            "urgency": "low",
            "reason": "No significant threats detected"
        }
        
        if report_analysis["risk_score"] >= self.reroute_threshold:
            deterministic_decision = {
                "should_reroute": True,
                "urgency": "high",
                "reason": f"High risk area detected (score: {report_analysis['risk_score']})"
            }
        elif len(critical_reports) >= 2:
            deterministic_decision = {
                "should_reroute": True,
                "urgency": "critical",
                "reason": f"{len(critical_reports)} critical incidents reported ahead"
            }
        elif report_analysis["risk_score"] >= self.warning_threshold:
            deterministic_decision = {
                "should_reroute": False,
                "urgency": "medium",
                "reason": "Moderate risk detected - proceed with caution"
            }
        
        ai_decision = None
        if self.ai_orchestrator:
            try:
                ai_decision = self.ai_orchestrator.decide_reroute(
                    current_route=current_route,
                    new_reports=new_reports,
                    user_location=user_location,
                    eta_remaining=eta_remaining
                )
            except Exception as e:
                print(f"AI reroute decision failed: {e}")
        
        final_decision = ai_decision if ai_decision else deterministic_decision
        
        if ai_decision and deterministic_decision["should_reroute"]:
            final_decision["should_reroute"] = True
            final_decision["urgency"] = max(
                ai_decision.get("urgency", "low"),
                deterministic_decision["urgency"],
                key=lambda x: {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(x, 0)
            )
        
        return {
            **final_decision,
            "deterministic_analysis": deterministic_decision,
            "ai_analysis": ai_decision,
            "new_report_count": len(new_reports),
            "critical_report_count": len(critical_reports),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    
    def recommend_action(
        self,
        situation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recommend user action based on current situation.
        """
        risk_level = situation.get("risk_level", "moderate")
        eta = situation.get("eta_remaining_minutes", 999)
        
        actions = {
            "safe": {
                "action": "continue",
                "message": "Route is safe. Continue as planned.",
                "priority": "low"
            },
            "moderate": {
                "action": "proceed_with_caution",
                "message": "Some safety concerns detected. Stay alert and avoid isolated areas.",
                "priority": "medium"
            },
            "risky": {
                "action": "consider_alternative",
                "message": "Risky conditions ahead. Consider taking an alternative route.",
                "priority": "high"
            },
            "dangerous": {
                "action": "reroute_immediately",
                "message": "Dangerous conditions detected. Finding safer route...",
                "priority": "critical"
            }
        }
        
        recommendation = actions.get(risk_level, actions["moderate"])
        
        if eta < 5 and risk_level in ["moderate", "risky"]:
            recommendation["message"] += " You're almost there - stay vigilant."
        
        return {
            **recommendation,
            "situation": situation,
            "timestamp": datetime.utcnow().isoformat()
        }