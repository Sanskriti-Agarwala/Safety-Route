"""
Risk Level Labels and Categorization Constants
==============================================

This module defines the risk level categories, labels, colors, and icons
used throughout the Safety Route application for consistent user experience.

Categories:
- SAFE: High safety score (80-100)
- MODERATE: Acceptable safety (50-79)
- RISKY: Below recommended (40-49)
- DANGEROUS: Critical safety concerns (0-39)

Author: Safety Route Team
Date: January 2026
"""

from typing import Dict, List

# ============================================================================
# RISK LEVEL CATEGORIES
# ============================================================================

# Primary risk categories used throughout the application
RISK_LEVEL_SAFE = "safe"
RISK_LEVEL_MODERATE = "moderate"
RISK_LEVEL_RISKY = "risky"
RISK_LEVEL_DANGEROUS = "dangerous"

# All valid risk levels in order from safest to most dangerous
ALL_RISK_LEVELS = [
    RISK_LEVEL_SAFE,
    RISK_LEVEL_MODERATE,
    RISK_LEVEL_RISKY,
    RISK_LEVEL_DANGEROUS
]


# ============================================================================
# RISK LEVEL DISPLAY LABELS
# ============================================================================

RISK_LABELS = {
    "safe": "Safe Route",
    "moderate": "Moderate Risk",
    "risky": "High Risk",
    "dangerous": "Dangerous Route"
}

# Short labels for compact UI displays (mobile, map markers)
RISK_LABELS_SHORT = {
    "safe": "Safe",
    "moderate": "Caution",
    "risky": "Risky",
    "dangerous": "Danger"
}

# Detailed labels with additional context
RISK_LABELS_DETAILED = {
    "safe": "Safe - Recommended Route",
    "moderate": "Moderate Risk - Exercise Caution",
    "risky": "High Risk - Not Recommended",
    "dangerous": "Dangerous - Avoid This Route"
}


# ============================================================================
# RISK LEVEL COLOR CODES
# ============================================================================

# Standard colors for UI display (hex codes)
RISK_COLORS = {
    "safe": "#00C851",      # Green - Go ahead
    "moderate": "#FFB700",  # Yellow/Amber - Proceed with caution
    "risky": "#FF8800",     # Orange - Warning
    "dangerous": "#FF4444"  # Red - Stop/Danger
}

# Alternative color scheme for dark mode
RISK_COLORS_DARK_MODE = {
    "safe": "#00E676",      # Brighter green
    "moderate": "#FFC107",  # Brighter yellow
    "risky": "#FF9800",     # Brighter orange
    "dangerous": "#F44336"  # Brighter red
}

# RGB values for map rendering or custom graphics
RISK_COLORS_RGB = {
    "safe": (0, 200, 81),
    "moderate": (255, 183, 0),
    "risky": (255, 136, 0),
    "dangerous": (255, 68, 68)
}


# ============================================================================
# RISK LEVEL ICONS
# ============================================================================

# Unicode emoji icons for quick visual identification
RISK_ICONS = {
    "safe": "✅",           # Check mark - approved
    "moderate": "⚠️",       # Warning sign - caution
    "risky": "❗",          # Exclamation - alert
    "dangerous": "🚫"       # Prohibited - stop
}

# Alternative text-based icons (for environments without emoji support)
RISK_ICONS_TEXT = {
    "safe": "[OK]",
    "moderate": "[!]",
    "risky": "[!!]",
    "dangerous": "[X]"
}

# Font Awesome icon classes (if using Font Awesome in frontend)
RISK_ICONS_FA = {
    "safe": "fa-check-circle",
    "moderate": "fa-exclamation-triangle",
    "risky": "fa-exclamation-circle",
    "dangerous": "fa-times-circle"
}


# ============================================================================
# RISK DESCRIPTIONS
# ============================================================================

# User-friendly descriptions explaining what each risk level means
RISK_DESCRIPTIONS = {
    "safe": (
        "This route has excellent safety ratings across all factors. "
        "Crime rates are low, lighting is good, and crowd density is optimal. "
        "We recommend this route for your journey."
    ),
    "moderate": (
        "This route has acceptable safety but with some concerns. "
        "You should remain alert and aware of your surroundings. "
        "Consider traveling during daylight hours if possible."
    ),
    "risky": (
        "This route has significant safety concerns and is not recommended. "
        "High crime rates, poor lighting, or other risk factors are present. "
        "We strongly suggest choosing an alternative route."
    ),
    "dangerous": (
        "This route poses serious safety risks and should be avoided. "
        "Critical safety factors such as high crime, no lighting, or isolated areas detected. "
        "Please select a different route immediately."
    )
}

# Short descriptions for tooltips or mobile UI
RISK_DESCRIPTIONS_SHORT = {
    "safe": "Low risk. Safe to proceed.",
    "moderate": "Some risk. Stay alert.",
    "risky": "High risk. Not recommended.",
    "dangerous": "Critical risk. Avoid this route."
}


# ============================================================================
# RISK RECOMMENDATIONS
# ============================================================================

# Action recommendations for users based on risk level
RISK_RECOMMENDATIONS = {
    "safe": [
        "Enjoy your journey",
        "Maintain normal awareness",
        "Follow standard safety practices"
    ],
    "moderate": [
        "Stay on well-lit paths",
        "Keep valuables secure",
        "Travel with others if possible",
        "Share your location with trusted contacts",
        "Stay alert to your surroundings"
    ],
    "risky": [
        "Consider an alternative route",
        "Do not travel alone",
        "Avoid traveling after dark",
        "Keep emergency contacts ready",
        "Share live location with trusted contacts",
        "Stay in well-populated areas"
    ],
    "dangerous": [
        "Choose a different route immediately",
        "Do not proceed with this route",
        "Contact local authorities if necessary",
        "Use our SOS feature if you feel unsafe",
        "Share your location with emergency contacts"
    ]
}


# ============================================================================
# RISK SCORE RANGES
# ============================================================================

# Score thresholds for each risk category
# These map safety scores (0-100) to risk levels
RISK_SCORE_RANGES = {
    "safe": {
        "min": 80,
        "max": 100,
        "label": "80-100"
    },
    "moderate": {
        "min": 50,
        "max": 79,
        "label": "50-79"
    },
    "risky": {
        "min": 40,
        "max": 49,
        "label": "40-49"
    },
    "dangerous": {
        "min": 0,
        "max": 39,
        "label": "0-39"
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_risk_level_from_score(score: float) -> str:
    """
    Convert a numeric safety score to a risk level category.
    
    This is the primary function for categorizing routes based on their
    calculated safety scores.
    
    Args:
        score (float): Safety score (0-100)
    
    Returns:
        str: Risk level category ('safe', 'moderate', 'risky', or 'dangerous')
    
    Examples:
        >>> get_risk_level_from_score(85)
        'safe'
        >>> get_risk_level_from_score(65)
        'moderate'
        >>> get_risk_level_from_score(45)
        'risky'
        >>> get_risk_level_from_score(25)
        'dangerous'
    
    Usage in routes:
        >>> route_score = 72
        >>> risk = get_risk_level_from_score(route_score)
        >>> color = RISK_COLORS[risk]
        >>> label = RISK_LABELS[risk]
        >>> print(f"{label}: {color}")
        Moderate Risk: #FFB700
    """
    if score >= 80:
        return RISK_LEVEL_SAFE
    elif score >= 50:
        return RISK_LEVEL_MODERATE
    elif score >= 40:
        return RISK_LEVEL_RISKY
    else:
        return RISK_LEVEL_DANGEROUS


def get_risk_display_info(score: float) -> Dict[str, str]:
    """
    Get complete display information for a safety score.
    
    Returns all the visual and textual elements needed to display
    a risk level in the UI (label, color, icon, description).
    
    Args:
        score (float): Safety score (0-100)
    
    Returns:
        Dict containing:
            - level: Risk category
            - label: Display label
            - color: Hex color code
            - icon: Unicode emoji
            - description: Full description
            - short_description: Brief description
    
    Example:
        >>> info = get_risk_display_info(85)
        >>> info['label']
        'Safe Route'
        >>> info['color']
        '#00C851'
        >>> info['icon']
        '✅'
    
    Usage in API response:
        >>> route = {
        ...     "safety_score": 72,
        ...     "display": get_risk_display_info(72)
        ... }
        >>> # Returns complete UI info for frontend
    """
    risk_level = get_risk_level_from_score(score)
    
    return {
        "level": risk_level,
        "label": RISK_LABELS[risk_level],
        "label_short": RISK_LABELS_SHORT[risk_level],
        "color": RISK_COLORS[risk_level],
        "icon": RISK_ICONS[risk_level],
        "description": RISK_DESCRIPTIONS[risk_level],
        "short_description": RISK_DESCRIPTIONS_SHORT[risk_level],
        "recommendations": RISK_RECOMMENDATIONS[risk_level],
        "score_range": RISK_SCORE_RANGES[risk_level]["label"]
    }


def get_all_risk_levels_info() -> List[Dict]:
    """
    Get information about all risk levels.
    
    Useful for:
    - Generating legend/key for maps
    - Documentation
    - Help/tutorial screens
    
    Returns:
        List[Dict]: Information for each risk level
    
    Example:
        >>> levels = get_all_risk_levels_info()
        >>> for level in levels:
        ...     print(f"{level['label']}: {level['score_range']}")
        Safe Route: 80-100
        Moderate Risk: 50-79
        High Risk: 40-49
        Dangerous Route: 0-39
    """
    return [
        {
            "level": level,
            "label": RISK_LABELS[level],
            "color": RISK_COLORS[level],
            "icon": RISK_ICONS[level],
            "score_range": RISK_SCORE_RANGES[level],
            "description": RISK_DESCRIPTIONS_SHORT[level]
        }
        for level in ALL_RISK_LEVELS
    ]


def is_safe_route(score: float) -> bool:
    """
    Quick check if a route is considered safe (score >= 80).
    
    Args:
        score (float): Safety score
    
    Returns:
        bool: True if route is in 'safe' category
    
    Example:
        >>> is_safe_route(85)
        True
        >>> is_safe_route(65)
        False
    """
    return score >= 80


def is_dangerous_route(score: float) -> bool:
    """
    Quick check if a route is dangerous (score < 40).
    
    Args:
        score (float): Safety score
    
    Returns:
        bool: True if route is in 'dangerous' category
    
    Example:
        >>> is_dangerous_route(25)
        True
        >>> is_dangerous_route(65)
        False
    """
    return score < 40


def requires_warning(score: float) -> bool:
    """
    Check if a route requires a safety warning (score < 50).
    
    Routes with moderate risk or worse should display warnings.
    
    Args:
        score (float): Safety score
    
    Returns:
        bool: True if warning should be shown
    
    Example:
        >>> requires_warning(45)
        True
        >>> requires_warning(75)
        False
    """
    return score < 50


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Demonstration of risk label functionality.
    Run this file directly to see sample outputs.
    """
    print("=== Risk Labels Demo ===\n")
    
    # Test different safety scores
    test_scores = [95, 65, 45, 25]
    
    for score in test_scores:
        info = get_risk_display_info(score)
        print(f"Score {score}:")
        print(f"  Level: {info['level']}")
        print(f"  Label: {info['label']} {info['icon']}")
        print(f"  Color: {info['color']}")
        print(f"  Description: {info['short_description']}")
        print(f"  Recommendations: {', '.join(info['recommendations'][:2])}")
        print()
    
    # Show all risk levels
    print("\n=== All Risk Levels ===")
    for level_info in get_all_risk_levels_info():
        print(f"{level_info['icon']} {level_info['label']}: {level_info['score_range']['label']}")