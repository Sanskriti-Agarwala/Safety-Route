"""
Time-Based Utility Functions
============================
This module provides time-related helper functions for the Safety Route system.
It determines whether current time is day or night and calculates appropriate
safety multipliers based on the hour.

Key Functions:
- is_night_time: Check if a given time falls within night hours
- get_time_period: Get the time period (morning/afternoon/evening/night)
- get_safety_multiplier: Get safety adjustment factor based on time
"""

from datetime import datetime
from app.constants.safety_thresholds import NIGHT_START_HOUR, NIGHT_END_HOUR


def is_night_time(current_time: datetime = None) -> bool:
    """
    Determine if the given time is considered "night time" for safety purposes.
    
    Night time is defined in safety_thresholds.py (typically 21:00 - 06:00).
    During night hours, routes receive stricter safety evaluation since:
    - Visibility is lower (poor lighting becomes critical)
    - Fewer people around (isolation risk increases)
    - Crime rates are typically higher
    
    Args:
        current_time (datetime, optional): The time to check. If None, uses current system time.
    
    Returns:
        bool: True if the time falls within night hours, False otherwise
    
    Example:
        >>> # Check if current time is night
        >>> if is_night_time():
        ...     print("Warning: Night travel requires extra caution")
        
        >>> # Check a specific time
        >>> from datetime import datetime
        >>> late_night = datetime(2025, 1, 17, 23, 30)  # 11:30 PM
        >>> is_night_time(late_night)  # Returns True
        
        >>> afternoon = datetime(2025, 1, 17, 14, 0)  # 2:00 PM
        >>> is_night_time(afternoon)  # Returns False
    """
    # If no time provided, use current system time
    if current_time is None:
        current_time = datetime.now()
    
    # Extract the hour (0-23)
    hour = current_time.hour
    
    # Handle night time that spans across midnight (e.g., 21:00-06:00)
    # If NIGHT_START_HOUR (21) > NIGHT_END_HOUR (6), night spans midnight
    if NIGHT_START_HOUR > NIGHT_END_HOUR:
        # Night time wraps around midnight
        # True if hour >= 21 OR hour < 6
        return hour >= NIGHT_START_HOUR or hour < NIGHT_END_HOUR
    else:
        # Night time doesn't wrap (e.g., if it were 1:00-5:00)
        # True if hour is between start and end
        return NIGHT_START_HOUR <= hour < NIGHT_END_HOUR


def get_time_period(hour: int) -> str:
    """
    Get the descriptive time period for a given hour.
    
    This categorizes the 24-hour day into four periods, which is useful for:
    - Displaying user-friendly time descriptions
    - Analyzing crowd patterns (different for morning vs evening)
    - Customizing safety warnings based on time period
    
    Time Periods:
    - Morning: 6:00 AM - 11:59 AM (06:00 - 11:59)
    - Afternoon: 12:00 PM - 5:59 PM (12:00 - 17:59)
    - Evening: 6:00 PM - 9:59 PM (18:00 - 21:59)
    - Night: 10:00 PM - 5:59 AM (22:00 - 05:59)
    
    Args:
        hour (int): Hour in 24-hour format (0-23)
    
    Returns:
        str: One of "morning", "afternoon", "evening", or "night"
    
    Example:
        >>> get_time_period(8)   # 8 AM
        'morning'
        >>> get_time_period(14)  # 2 PM
        'afternoon'
        >>> get_time_period(19)  # 7 PM
        'evening'
        >>> get_time_period(23)  # 11 PM
        'night'
        
        >>> # Use with crowd data
        >>> hour = 14
        >>> period = get_time_period(hour)
        >>> crowd_level = crowd_data[period]  # Get afternoon crowd level
    """
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 22:
        return "evening"
    else:
        return "night"


def get_safety_multiplier(hour: int) -> float:
    """
    Calculate the time-based safety multiplier for a given hour.
    
    The safety multiplier adjusts the overall safety score based on time of day.
    This reflects the reality that the same route can be safe during the day
    but risky at night due to reduced visibility, fewer people, etc.
    
    Multiplier Scale:
    - 1.0 = Daytime (6 AM - 6 PM) - Full safety score applies
    - 0.85 = Evening (6 PM - 10 PM) - Slight reduction (dusk/early evening)
    - 0.6 = Night (10 PM - 2 AM) - Significant reduction (late night)
    - 0.5 = Late Night (2 AM - 6 AM) - Maximum reduction (most dangerous hours)
    
    How it works:
    If a route has a base safety score of 80:
    - At 2 PM (day): 80 × 1.0 = 80 (no change)
    - At 8 PM (evening): 80 × 0.85 = 68 (slightly less safe)
    - At 11 PM (night): 80 × 0.6 = 48 (much less safe)
    - At 3 AM (late night): 80 × 0.5 = 40 (least safe)
    
    Args:
        hour (int): Hour in 24-hour format (0-23)
    
    Returns:
        float: Safety multiplier between 0.5 and 1.0
    
    Example:
        >>> base_score = 85.0
        >>> hour = 23  # 11 PM
        >>> multiplier = get_safety_multiplier(hour)
        >>> final_score = base_score * multiplier
        >>> print(f"Safety at {hour}:00 = {final_score:.1f}/100")
        Safety at 23:00 = 51.0/100
        
        >>> # Compare day vs night
        >>> day_score = 85 * get_safety_multiplier(14)    # 2 PM
        >>> night_score = 85 * get_safety_multiplier(23)  # 11 PM
        >>> print(f"Day: {day_score:.0f}, Night: {night_score:.0f}")
        Day: 85, Night: 51
    """
    from app.constants.safety_thresholds import (
        DAY_SAFETY_MULTIPLIER,
        EVENING_SAFETY_MULTIPLIER,
        NIGHT_SAFETY_MULTIPLIER,
        LATE_NIGHT_SAFETY_MULTIPLIER
    )
    
    # Daytime: 6 AM to 6 PM (full safety)
    if 6 <= hour < 18:
        return DAY_SAFETY_MULTIPLIER
    
    # Evening: 6 PM to 10 PM (slight reduction)
    elif 18 <= hour < 22:
        return EVENING_SAFETY_MULTIPLIER
    
    # Night: 10 PM to 2 AM (significant reduction)
    elif 22 <= hour <= 23 or 0 <= hour < 2:
        return NIGHT_SAFETY_MULTIPLIER
    
    # Late Night: 2 AM to 6 AM (maximum reduction - most dangerous)
    else:
        return LATE_NIGHT_SAFETY_MULTIPLIER