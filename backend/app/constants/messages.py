"""
User-Facing Messages and Alerts
================================

This module contains all user-facing messages, warnings, alerts, and
notifications used throughout the Safety Route application.

Categories:
- Success messages (route found, SOS sent, etc.)
- Warning messages (low safety, night travel, etc.)
- Error messages (invalid input, service unavailable, etc.)
- Info messages (tips, recommendations, etc.)

Benefits of centralized messages:
- Consistent tone and language
- Easy to update/translate
- Better user experience
- Easier testing

Author: Safety Route Team
Date: January 2026
"""

# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

SUCCESS_ROUTE_FOUND = "Found {count} safe route(s) to your destination."
SUCCESS_ROUTE_PLANNED = "Route planned successfully. Total distance: {distance} km."
SUCCESS_SAFEST_ROUTE = "We've identified the safest route for you."
SUCCESS_ALTERNATIVE_ROUTES = "Found {count} alternative route(s) with similar safety ratings."
SUCCESS_LOCATION_UPDATED = "Your location has been updated successfully."
SUCCESS_SOS_SENT = "SOS alert sent successfully. Emergency contacts have been notified."
SUCCESS_SOS_CANCELLED = "SOS alert cancelled. Your contacts have been informed you're safe."
SUCCESS_REPORT_SUBMITTED = "Thank you! Your safety report has been submitted."
SUCCESS_CONTACT_ADDED = "Emergency contact added successfully."
SUCCESS_PREFERENCES_SAVED = "Your preferences have been saved."


# ============================================================================
# WARNING MESSAGES - SAFETY ALERTS
# ============================================================================

# General safety warnings
WARNING_LOW_SAFETY = "⚠️ This route has a low safety score ({score}/100). Consider alternatives."
WARNING_MODERATE_RISK = "This route has moderate risk. Stay alert and aware of your surroundings."
WARNING_HIGH_RISK = "⚠️ High risk detected on this route. We strongly recommend choosing an alternative."
WARNING_CRITICAL_RISK = "🚫 CRITICAL: This route is dangerous. Do NOT proceed. Select a different route."

# Time-based warnings
WARNING_NIGHT_TRAVEL = "⚠️ Traveling at night reduces safety. Consider delaying your journey until morning."
WARNING_LATE_HOURS = "It's late ({time}). Safety scores are lower during these hours. Extra caution advised."
WARNING_DAWN_DUSK = "Visibility is reduced during dawn/dusk hours. Stay on well-lit paths."

# Location-based warnings
WARNING_CRIME_ZONE = "⚠️ High crime area detected on this route. Distance from crime zone: {distance}m."
WARNING_MULTIPLE_CRIME_ZONES = "⚠️ Multiple crime zones detected along this route. Alternative routes recommended."
WARNING_ISOLATED_AREA = "This route passes through isolated areas. Consider traveling with companions."
WARNING_POOR_LIGHTING = "⚠️ Poor lighting detected on parts of this route. Bring a flashlight or use phone light."
WARNING_LOW_CROWD = "This area has low foot traffic. You may encounter few other people."

# Weather-based warnings (for future implementation)
WARNING_WEATHER_POOR = "⚠️ Poor weather conditions may affect route safety. Exercise extra caution."
WARNING_WEATHER_SEVERE = "🚫 Severe weather alert. Consider postponing your journey."


# ============================================================================
# ERROR MESSAGES
# ============================================================================

# Input validation errors
ERROR_INVALID_COORDINATES = "Invalid coordinates provided. Please check your location data."
ERROR_INVALID_MODE = "Invalid travel mode. Supported modes: walking, driving, cycling."
ERROR_MISSING_SOURCE = "Source location is required."
ERROR_MISSING_DESTINATION = "Destination location is required."
ERROR_SAME_LOCATION = "Source and destination are the same location."
ERROR_COORDINATES_OUT_OF_RANGE = "Coordinates are out of valid range. Lat: -90 to 90, Lng: -180 to 180."

# Service errors
ERROR_ROUTE_NOT_FOUND = "No route could be found between these locations."
ERROR_SERVICE_UNAVAILABLE = "Route service is temporarily unavailable. Please try again."
ERROR_MAPS_API_ERROR = "Error connecting to maps service. Please check your connection."
ERROR_SAFETY_DATA_UNAVAILABLE = "Safety data temporarily unavailable. Showing routes without safety scores."

# SOS errors
ERROR_SOS_NO_CONTACTS = "No emergency contacts configured. Please add contacts in settings."
ERROR_SOS_SEND_FAILED = "Failed to send SOS alert. Please try again or call emergency services directly."
ERROR_LOCATION_REQUIRED = "Location access required for SOS feature."

# User/Auth errors (for future implementation)
ERROR_USER_NOT_FOUND = "User not found. Please register first."
ERROR_INVALID_CONTACT = "Invalid emergency contact. Please provide a valid phone number."
ERROR_UNAUTHORIZED = "Unauthorized access. Please log in."


# ============================================================================
# INFORMATIONAL MESSAGES
# ============================================================================

INFO_CALCULATING_ROUTES = "Calculating safe routes to your destination..."
INFO_ANALYZING_SAFETY = "Analyzing safety factors along your route..."
INFO_FETCHING_DATA = "Fetching latest safety data..."
INFO_NO_ROUTES_AVAILABLE = "No routes available for these locations."
INFO_ALTERNATIVE_SUGGESTED = "Alternative route suggested with {percent}% better safety."
INFO_SAFEST_ROUTE_LONGER = "Note: The safest route is {extra_distance} km longer but {percent}% safer."
INFO_ROUTE_COMPARISON = "Comparing {count} route options based on safety..."
INFO_REAL_TIME_UPDATE = "Route safety updated based on current conditions."


# ============================================================================
# RECOMMENDATION MESSAGES
# ============================================================================

RECOMMEND_SAFER_ROUTE = "A safer route is available. Would you like to see it?"
RECOMMEND_ALTERNATIVE = "We found {count} safer alternative(s). Tap to view."
RECOMMEND_TRAVEL_COMPANION = "For this route, we recommend traveling with a companion."
RECOMMEND_DAYLIGHT = "This route is much safer during daylight hours. Consider traveling between {start} and {end}."
RECOMMEND_WELL_LIT_PATH = "Stay on main roads with better lighting for improved safety."
RECOMMEND_EMERGENCY_CONTACTS = "Add emergency contacts to use the SOS feature."
RECOMMEND_LOCATION_SHARING = "Share your live location with trusted contacts for added safety."


# ============================================================================
# SOS MESSAGES
# ============================================================================

SOS_ALERT_TRIGGERED = "🚨 SOS ALERT ACTIVE 🚨"
SOS_ALERT_MESSAGE = "Emergency alert sent to your contacts with your current location."
SOS_HELP_ON_WAY = "Help is on the way. Stay calm and in a safe location if possible."
SOS_CALL_EMERGENCY = "If in immediate danger, call emergency services: 112 (India) / 911 (US)"
SOS_CONTACT_NOTIFIED = "{contact_name} has been notified of your emergency."
SOS_LOCATION_SHARED = "Your location is being shared continuously with emergency contacts."
SOS_CANCEL_PROMPT = "Are you safe? Tap here to cancel the SOS alert."
SOS_AUTO_CANCELLED = "SOS alert auto-cancelled after arriving at safe location."


# ============================================================================
# ROUTE DETAILS MESSAGES
# ============================================================================

ROUTE_DETAILS_DISTANCE = "Distance: {distance} km"
ROUTE_DETAILS_DURATION = "Estimated time: {duration} minutes"
ROUTE_DETAILS_SAFETY_SCORE = "Safety Score: {score}/100"
ROUTE_DETAILS_CRIME_SCORE = "Crime Safety: {score}/100"
ROUTE_DETAILS_LIGHTING_SCORE = "Lighting Quality: {score}/100"
ROUTE_DETAILS_CROWD_SCORE = "Crowd Density: {score}/100"
ROUTE_DETAILS_TIME_FACTOR = "Time of Day Factor: {factor}x"
ROUTE_DETAILS_SAFEST = "✅ This is the safest route"
ROUTE_DETAILS_FASTEST = "⚡ This is the fastest route"
ROUTE_DETAILS_SHORTEST = "📏 This is the shortest route"


# ============================================================================
# TIPS AND GUIDANCE
# ============================================================================

TIP_STAY_ALERT = "💡 Tip: Stay alert and aware of your surroundings at all times."
TIP_VALUABLES = "💡 Tip: Keep valuables out of sight to avoid attracting attention."
TIP_TRUST_INSTINCT = "💡 Tip: Trust your instincts. If something feels wrong, seek help."
TIP_WELL_LIT = "💡 Tip: Stick to well-lit, populated areas whenever possible."
TIP_PHONE_CHARGED = "💡 Tip: Keep your phone charged when traveling."
TIP_SHARE_LOCATION = "💡 Tip: Share your location with trusted contacts before traveling."
TIP_AVOID_SHORTCUTS = "💡 Tip: Avoid isolated shortcuts, even if they seem faster."
TIP_NIGHT_SAFETY = "💡 Tip: Travel in groups when possible, especially at night."
TIP_EMERGENCY_NUMBERS = "💡 Tip: Keep emergency numbers saved in your phone."
TIP_ROUTE_PLANNING = "💡 Tip: Plan your route in advance, especially for unfamiliar areas."


# ============================================================================
# VALIDATION MESSAGES
# ============================================================================

VALIDATION_LOCATION_REQUIRED = "Please provide both source and destination locations."
VALIDATION_INVALID_TIME = "Invalid time format. Please use 24-hour format (0-23)."
VALIDATION_INVALID_MODE = "Please select a valid travel mode: walking, driving, or cycling."
VALIDATION_DISTANCE_TOO_LONG = "Route distance exceeds maximum limit of {max_distance} km."
VALIDATION_COORDINATES_INVALID = "Coordinates must be numbers. Latitude: -90 to 90, Longitude: -180 to 180."


# ============================================================================
# COMMUNITY FEATURES (Future)
# ============================================================================

COMMUNITY_REPORT_THANKS = "Thank you for reporting! Your input helps keep the community safe."
COMMUNITY_INCIDENT_REPORTED = "Incident reported successfully. We'll update safety data accordingly."
COMMUNITY_UPVOTE_THANKS = "Thanks for verifying this report!"
COMMUNITY_NEW_ALERT = "New safety alert in your area: {alert_message}"


# ============================================================================
# NOTIFICATION MESSAGES (Push/SMS)
# ============================================================================

NOTIFICATION_SOS_TRIGGERED = "{user_name} has triggered an SOS alert! Location: {location}"
NOTIFICATION_ARRIVED_SAFE = "{user_name} has arrived safely at their destination."
NOTIFICATION_ROUTE_DEVIATION = "{user_name} has deviated from their planned route."
NOTIFICATION_LOW_BATTERY = "{user_name}'s phone battery is low ({battery}%)"
NOTIFICATION_SAFETY_ALERT = "Safety Alert: Avoid {area_name} due to {reason}"


# ============================================================================
# HELPER FUNCTIONS FOR DYNAMIC MESSAGES
# ============================================================================

def format_message(template: str, **kwargs) -> str:
    """
    Format a message template with provided values.
    
    Replaces placeholders in message templates with actual values.
    
    Args:
        template (str): Message template with {placeholders}
        **kwargs: Values to substitute into template
    
    Returns:
        str: Formatted message
    
    Examples:
        >>> format_message(SUCCESS_ROUTE_FOUND, count=3)
        'Found 3 safe route(s) to your destination.'
        
        >>> format_message(WARNING_CRIME_ZONE, distance=150)
        '⚠️ High crime area detected on this route. Distance from crime zone: 150m.'
        
        >>> format_message(ROUTE_DETAILS_SAFETY_SCORE, score=85)
        'Safety Score: 85/100'
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        # If placeholder is missing, return template as-is
        return template


def get_safety_warning(score: float) -> str:
    """
    Get appropriate safety warning based on score.
    
    Args:
        score (float): Safety score (0-100)
    
    Returns:
        str: Warning message appropriate for the score
    
    Examples:
        >>> get_safety_warning(85)
        ''  # No warning for safe routes
        
        >>> get_safety_warning(65)
        'This route has moderate risk. Stay alert and aware of your surroundings.'
        
        >>> get_safety_warning(45)
        '⚠️ High risk detected on this route. We strongly recommend choosing an alternative.'
        
        >>> get_safety_warning(25)
        '🚫 CRITICAL: This route is dangerous. Do NOT proceed. Select a different route.'
    """
    if score >= 80:
        return ""  # No warning needed
    elif score >= 50:
        return WARNING_MODERATE_RISK
    elif score >= 40:
        return WARNING_HIGH_RISK
    else:
        return WARNING_CRITICAL_RISK


def get_time_warning(hour: int) -> str:
    """
    Get time-based safety warning.
    
    Args:
        hour (int): Hour of day (0-23)
    
    Returns:
        str: Time-based warning message
    
    Examples:
        >>> get_time_warning(2)  # 2 AM
        "It's late (02:00). Safety scores are lower during these hours. Extra caution advised."
        
        >>> get_time_warning(14)  # 2 PM
        ''  # No warning during day
        
        >>> get_time_warning(19)  # 7 PM (dusk)
        'Visibility is reduced during dawn/dusk hours. Stay on well-lit paths.'
    """
    if 22 <= hour or hour < 5:  # Night (10 PM - 5 AM)
        return format_message(WARNING_LATE_HOURS, time=f"{hour:02d}:00")
    elif 5 <= hour < 7 or 18 <= hour < 20:  # Dawn/Dusk
        return WARNING_DAWN_DUSK
    else:
        return ""  # No warning during day


def get_route_tip() -> str:
    """
    Get a random safety tip for users.
    
    Returns:
        str: A random safety tip
    
    Example:
        >>> tip = get_route_tip()
        >>> print(tip)
        '💡 Tip: Stay alert and aware of your surroundings at all times.'
    """
    import random
    
    tips = [
        TIP_STAY_ALERT,
        TIP_VALUABLES,
        TIP_TRUST_INSTINCT,
        TIP_WELL_LIT,
        TIP_PHONE_CHARGED,
        TIP_SHARE_LOCATION,
        TIP_AVOID_SHORTCUTS,
        TIP_NIGHT_SAFETY,
        TIP_EMERGENCY_NUMBERS,
        TIP_ROUTE_PLANNING
    ]
    
    return random.choice(tips)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Demonstration of message formatting and usage.
    """
    print("=== Safety Route Messages Demo ===\n")
    
    # Example 1: Success message
    print("1. Route found:")
    print(format_message(SUCCESS_ROUTE_FOUND, count=3))
    print()
    
    # Example 2: Safety warnings
    print("2. Safety warnings for different scores:")
    for score in [85, 65, 45, 25]:
        warning = get_safety_warning(score)
        if warning:
            print(f"Score {score}: {warning}")
    print()
    
    # Example 3: Time warnings
    print("3. Time-based warnings:")
    for hour in [2, 7, 14, 19, 23]:
        warning = get_time_warning(hour)
        if warning:
            print(f"{hour:02d}:00 - {warning}")
    print()
    
    # Example 4: Route details
    print("4. Route details:")
    print(format_message(ROUTE_DETAILS_DISTANCE, distance=3.5))
    print(format_message(ROUTE_DETAILS_DURATION, duration=25))
    print(format_message(ROUTE_DETAILS_SAFETY_SCORE, score=85))
    print()
    
    # Example 5: Random tip
    print("5. Safety tip:")
    print(get_route_tip())