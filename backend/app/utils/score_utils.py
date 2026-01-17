"""
Score Calculation Utilities
===========================
This module provides helper functions for calculating, normalizing, and
interpreting safety scores throughout the Safety Route system.

Key Functions:
- normalize_score: Ensure scores stay within 0-100 range
- calculate_weighted_score: Combine multiple scores with weights
- get_risk_level: Convert numeric score to risk category
- interpolate_score: Calculate score between two values
- aggregate_scores: Combine multiple route scores
"""

from typing import List, Dict, Tuple
from app.constants.safety_thresholds import (
    CRIME_WEIGHT,
    LIGHTING_WEIGHT,
    CROWD_WEIGHT,
    MINIMUM_SAFE_SCORE,
    RECOMMENDED_SAFE_SCORE,
    CRITICAL_RISK_THRESHOLD
)


def normalize_score(score: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """
    Normalize a score to ensure it stays within the valid range.
    
    Safety scores must always be between 0-100 for consistency.
    This function clamps any score that goes out of bounds.
    
    Why normalize?
    - Calculations might produce negative values (penalties)
    - Calculations might exceed 100 (bonuses)
    - We need consistent 0-100 scale for user display
    
    Args:
        score (float): The score to normalize
        min_val (float): Minimum allowed value (default: 0.0)
        max_val (float): Maximum allowed value (default: 100.0)
    
    Returns:
        float: Normalized score within [min_val, max_val] range
    
    Example:
        >>> normalize_score(120)  # Too high
        100.0
        >>> normalize_score(-15)  # Negative (from penalties)
        0.0
        >>> normalize_score(75.5)  # Already valid
        75.5
        
        >>> # In safety calculation
        >>> base_score = 80
        >>> penalty = 30  # Heavy crime penalty
        >>> result = normalize_score(base_score - penalty)  # 50
    """
    return max(min_val, min(max_val, score))


def calculate_weighted_score(crime_score: float, 
                            lighting_score: float, 
                            crowd_score: float) -> float:
    """
    Calculate overall safety score using weighted combination of factors.
    
    The overall safety score is not a simple average - different factors
    have different importance levels:
    - Crime: 40% (most important - directly affects personal safety)
    - Lighting: 30% (visibility and deterrent for crime)
    - Crowd: 30% (safety in numbers, but not overcrowding)
    
    Formula:
    Overall = (Crime × 0.4) + (Lighting × 0.3) + (Crowd × 0.3)
    
    Why weighted?
    A route through a high-crime area with good lighting is still dangerous.
    Crime factor gets highest weight because it's the primary safety concern.
    
    Args:
        crime_score (float): Crime safety score (0-100, higher = safer)
        lighting_score (float): Lighting quality score (0-100, higher = better lit)
        crowd_score (float): Crowd density score (0-100, optimal around 70-80)
    
    Returns:
        float: Weighted overall safety score (0-100)
    
    Example:
        >>> # Safe route: low crime, well lit, good crowd
        >>> calculate_weighted_score(90, 85, 75)
        83.5
        
        >>> # Dangerous route: high crime, poor lighting, isolated
        >>> calculate_weighted_score(30, 40, 35)
        35.0
        
        >>> # Mixed: safe from crime but poor lighting at night
        >>> calculate_weighted_score(85, 35, 70)
        66.5  # Crime weight keeps it moderate despite poor lighting
    """
    # Apply weights from constants
    weighted = (
        crime_score * CRIME_WEIGHT +      # 40% weight
        lighting_score * LIGHTING_WEIGHT +  # 30% weight
        crowd_score * CROWD_WEIGHT          # 30% weight
    )
    
    # Ensure result is within valid range
    return normalize_score(weighted)


def get_risk_level(score: float) -> str:
    """
    Convert a numeric safety score to a human-readable risk level category.
    
    Risk Levels:
    - "safe" (70-100): Recommended for travel, minimal concerns
    - "moderate" (50-69): Acceptable with caution, some risk factors present
    - "risky" (40-49): Not recommended, significant safety concerns
    - "dangerous" (0-39): Avoid, critical safety issues
    
    These categories help users quickly understand route safety without
    needing to interpret numeric scores.
    
    Args:
        score (float): Safety score (0-100)
    
    Returns:
        str: Risk level category ("safe", "moderate", "risky", or "dangerous")
    
    Example:
        >>> get_risk_level(85)
        'safe'
        >>> get_risk_level(55)
        'moderate'
        >>> get_risk_level(45)
        'risky'
        >>> get_risk_level(25)
        'dangerous'
        
        >>> # Usage in UI
        >>> score = 65
        >>> level = get_risk_level(score)
        >>> color = {"safe": "green", "moderate": "yellow", "risky": "orange", "dangerous": "red"}
        >>> print(f"Route safety: {level} ({color[level]})")
        Route safety: moderate (yellow)
    """
    if score >= RECOMMENDED_SAFE_SCORE:  # 70+
        return "safe"
    elif score >= MINIMUM_SAFE_SCORE:    # 50-69
        return "moderate"
    elif score >= CRITICAL_RISK_THRESHOLD:  # 40-49
        return "risky"
    else:  # Below 40
        return "dangerous"


def get_risk_color(score: float) -> str:
    """
    Get the color code for visualizing a safety score.
    
    Colors provide instant visual feedback about route safety:
    - Green: Safe routes
    - Yellow: Moderate risk
    - Orange: High risk
    - Red: Dangerous
    
    Args:
        score (float): Safety score (0-100)
    
    Returns:
        str: Hex color code
    
    Example:
        >>> get_risk_color(85)
        '#00C851'  # Green
        >>> get_risk_color(55)
        '#FFB700'  # Yellow
        >>> get_risk_color(45)
        '#FF8800'  # Orange
        >>> get_risk_color(25)
        '#FF4444'  # Red
    """
    risk_level = get_risk_level(score)
    color_map = {
        "safe": "#00C851",      # Green
        "moderate": "#FFB700",  # Yellow
        "risky": "#FF8800",     # Orange
        "dangerous": "#FF4444"  # Red
    }
    return color_map.get(risk_level, "#999999")  # Gray as fallback


def interpolate_score(start_score: float, end_score: float, factor: float) -> float:
    """
    Calculate an intermediate score between two values.
    
    Used for:
    - Gradual score transitions along a route
    - Estimating scores for points between sampled locations
    - Smooth score animations in UI
    
    Args:
        start_score (float): Starting score
        end_score (float): Ending score
        factor (float): Interpolation factor (0.0 to 1.0)
                       0.0 = start_score, 1.0 = end_score, 0.5 = midpoint
    
    Returns:
        float: Interpolated score
    
    Example:
        >>> interpolate_score(80, 40, 0.0)  # At start
        80.0
        >>> interpolate_score(80, 40, 0.5)  # Halfway
        60.0
        >>> interpolate_score(80, 40, 1.0)  # At end
        40.0
        
        >>> # Gradual transition along route
        >>> start = 85
        >>> end = 55
        >>> for i in range(5):
        ...     t = i / 4  # 0.0, 0.25, 0.5, 0.75, 1.0
        ...     score = interpolate_score(start, end, t)
        ...     print(f"Position {i}: {score:.1f}")
    """
    # Linear interpolation: start + (end - start) * factor
    return start_score + (end_score - start_score) * factor


def aggregate_scores(scores: List[float], method: str = "average") -> float:
    """
    Combine multiple safety scores into a single aggregate score.
    
    Used when:
    - Comparing multiple routes
    - Combining segment scores for total route score
    - Analyzing safety across multiple time periods
    
    Methods:
    - "average": Simple mean of all scores
    - "min": Most pessimistic (lowest score) - conservative approach
    - "weighted_avg": Use lowest scores more heavily (safety-first approach)
    
    Args:
        scores (List[float]): List of safety scores to aggregate
        method (str): Aggregation method ("average", "min", or "weighted_avg")
    
    Returns:
        float: Aggregated score (0-100)
    
    Example:
        >>> route_segments = [85, 70, 60, 75]
        
        >>> aggregate_scores(route_segments, "average")
        72.5  # Simple average
        
        >>> aggregate_scores(route_segments, "min")
        60.0  # Conservative: route is only as safe as weakest segment
        
        >>> aggregate_scores(route_segments, "weighted_avg")
        67.5  # Emphasizes lower scores for safety
    """
    if not scores:
        return 0.0
    
    if method == "average":
        return sum(scores) / len(scores)
    
    elif method == "min":
        # Conservative: route is only as safe as its least safe segment
        return min(scores)
    
    elif method == "weighted_avg":
        # Weight lower scores more heavily (safety-first approach)
        # Sort scores and give more weight to lower ones
        sorted_scores = sorted(scores)
        weights = [1.5 if i < len(scores) / 2 else 1.0 for i in range(len(scores))]
        weighted_sum = sum(s * w for s, w in zip(sorted_scores, weights))
        total_weight = sum(weights)
        return weighted_sum / total_weight
    
    else:
        # Default to average
        return sum(scores) / len(scores)


def score_to_percentage(score: float) -> str:
    """
    Convert safety score to percentage string for display.
    
    Args:
        score (float): Safety score (0-100)
    
    Returns:
        str: Formatted percentage string
    
    Example:
        >>> score_to_percentage(85.7)
        '86%'
        >>> score_to_percentage(42.3)
        '42%'
    """
    return f"{round(score)}%"


def get_score_description(score: float) -> str:
    """
    Get a detailed text description of what a safety score means.
    
    Provides user-friendly explanation of the numeric score.
    
    Args:
        score (float): Safety score (0-100)
    
    Returns:
        str: Human-readable description
    
    Example:
        >>> get_score_description(85)
        'Excellent safety rating. This route is highly recommended.'
        
        >>> get_score_description(55)
        'Moderate safety. Exercise normal caution and be aware of surroundings.'
        
        >>> get_score_description(35)
        'Poor safety rating. This route is not recommended. Consider alternatives.'
    """
    if score >= 80:
        return "Excellent safety rating. This route is highly recommended."
    elif score >= 70:
        return "Good safety rating. This route is generally safe."
    elif score >= 60:
        return "Fair safety rating. Exercise caution and stay alert."
    elif score >= 50:
        return "Moderate safety. Exercise normal caution and be aware of surroundings."
    elif score >= 40:
        return "Below average safety. Consider alternative routes if possible."
    else:
        return "Poor safety rating. This route is not recommended. Consider alternatives."