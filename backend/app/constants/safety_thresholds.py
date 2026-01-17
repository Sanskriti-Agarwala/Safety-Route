"""
Safety Thresholds and Constants
================================
This module defines all safety-related constants and thresholds used throughout
the Safety Route system. These values determine how routes are scored and what
constitutes safe vs unsafe conditions.

Categories:
- Time definitions (when is "night")
- Safety score thresholds (what score is "safe")
- Time-based multipliers (how time affects safety)
- Crime zone penalties (how dangerous is each severity level)
- Lighting thresholds (what's considered well-lit)
- Crowd density preferences (optimal crowd levels)
- Scoring weights (importance of each factor)
"""

# ============================================================================
# TIME DEFINITIONS (24-hour format)
# ============================================================================
# These define when "night time" begins and ends for safety calculations

NIGHT_START_HOUR = 21  # 9:00 PM - Night begins (reduced visibility, fewer people)
NIGHT_END_HOUR = 6     # 6:00 AM - Night ends (daylight returns)
DAY_START_HOUR = 6     # 6:00 AM - Day begins
DAY_END_HOUR = 21      # 9:00 PM - Day ends


# ============================================================================
# SAFETY SCORE THRESHOLDS (0-100 scale)
# ============================================================================
# These thresholds determine what safety scores mean for users

# Minimum acceptable safety score for daytime travel
# Routes below this should show warnings
DAY_RISK_THRESHOLD = 60

# Stricter threshold for nighttime travel
# Night routes need higher scores to be considered safe
NIGHT_RISK_THRESHOLD = 70

# Critical threshold - routes below this should be avoided entirely
# Regardless of time of day
CRITICAL_RISK_THRESHOLD = 40


# ============================================================================
# TIME-BASED SAFETY MULTIPLIERS
# ============================================================================
# These multipliers adjust safety scores based on time of day
# Lower multiplier = route becomes less safe at that time

DAY_SAFETY_MULTIPLIER = 1.0        # 6 AM - 6 PM: Full safety (no reduction)
EVENING_SAFETY_MULTIPLIER = 0.85   # 6 PM - 10 PM: Slight reduction (dusk)
NIGHT_SAFETY_MULTIPLIER = 0.6      # 10 PM - 2 AM: Significant reduction
LATE_NIGHT_SAFETY_MULTIPLIER = 0.5 # 2 AM - 6 AM: Maximum reduction (most dangerous)


# ============================================================================
# CRIME ZONE SEVERITY WEIGHTS
# ============================================================================
# Penalty points applied when route passes through crime zones
# Higher penalty = more dangerous zone

HIGH_CRIME_PENALTY = 50    # High crime area: Major safety concern
MEDIUM_CRIME_PENALTY = 25  # Medium crime area: Moderate concern
LOW_CRIME_PENALTY = 10     # Low crime area: Minor concern


# ============================================================================
# LIGHTING SCORE THRESHOLDS
# ============================================================================
# What constitutes good/poor lighting (0-100 scale)

WELL_LIT_THRESHOLD = 80      # Score >= 80: Well-lit, safe for night travel
MODERATE_LIT_THRESHOLD = 60  # Score 60-79: Moderate lighting, caution advised
POORLY_LIT_THRESHOLD = 40    # Score < 40: Poorly lit, avoid at night


# ============================================================================
# CROWD DENSITY PREFERENCES (0-100 scale)
# ============================================================================
# Optimal crowd levels for safety
# Too few people = isolation risk
# Too many people = overcrowding, potential targets

OPTIMAL_CROWD_MIN = 60       # Minimum for optimal safety (good foot traffic)
OPTIMAL_CROWD_MAX = 85       # Maximum for optimal safety (busy but not crowded)
ISOLATED_THRESHOLD = 40      # Below this = too isolated (risk of no help)
OVERCROWDED_THRESHOLD = 90   # Above this = too crowded (different risks)


# ============================================================================
# DISTANCE THRESHOLDS FOR ZONE PROXIMITY (meters)
# ============================================================================
# How close to a danger zone triggers warnings

DANGER_ZONE_RADIUS = 500   # High-risk zones affect routes within 500m
WARNING_ZONE_RADIUS = 300  # Medium-risk zones affect routes within 300m
SAFE_ZONE_RADIUS = 100     # Safe zones (police, hospitals) within 100m


# ============================================================================
# SCORING WEIGHTS
# ============================================================================
# How much each factor contributes to overall safety score
# These weights must sum to 1.0 for proper calculation

CRIME_WEIGHT = 0.4      # 40% - Crime is most important factor
LIGHTING_WEIGHT = 0.3   # 30% - Lighting is second most important
CROWD_WEIGHT = 0.3      # 30% - Crowd density completes the score

# Example calculation:
# Overall Score = (Crime Score × 0.4) + (Lighting Score × 0.3) + (Crowd Score × 0.3)
# If Crime=80, Lighting=70, Crowd=60:
# Overall = (80×0.4) + (70×0.3) + (60×0.3) = 32 + 21 + 18 = 71


# ============================================================================
# MINIMUM ACCEPTABLE SAFETY SCORES
# ============================================================================
# Used for filtering and recommendations

MINIMUM_SAFE_SCORE = 50      # Absolute minimum - below this shows strong warning
RECOMMENDED_SAFE_SCORE = 70  # Recommended minimum for comfortable travel