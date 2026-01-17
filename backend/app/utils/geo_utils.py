"""
Geospatial Utility Functions
=============================
This module provides geographic calculation utilities for the Safety Route system.
It includes distance calculations, proximity checks, and point interpolation.

Key Functions:
- calculate_distance: Calculate distance between two GPS coordinates
- is_point_in_radius: Check if a point falls within a danger zone
- get_proximity_factor: Calculate how close a point is to a zone (0-1 scale)
- interpolate_points: Generate waypoints between two locations
"""

import math
from typing import List, Dict, Tuple, Optional


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the distance between two GPS coordinates using the Haversine formula.
    
    The Haversine formula calculates the great-circle distance between two points
    on a sphere given their longitudes and latitudes. This is the shortest distance
    over the earth's surface.
    
    Args:
        lat1 (float): Latitude of first point in decimal degrees
        lng1 (float): Longitude of first point in decimal degrees
        lat2 (float): Latitude of second point in decimal degrees
        lng2 (float): Longitude of second point in decimal degrees
    
    Returns:
        float: Distance between the two points in kilometers
    
    Example:
        >>> distance = calculate_distance(20.2961, 85.8245, 20.3021, 85.8350)
        >>> print(f"Distance: {distance:.2f} km")
        Distance: 1.23 km
    """
    R = 6371
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def is_point_in_radius(point_lat: float, point_lng: float, 
                       center_lat: float, center_lng: float, 
                       radius_meters: float) -> bool:
    """
    Check if a point falls within a circular zone (e.g., crime zone, danger zone).
    
    This is used to determine if a route passes through unsafe areas.
    For example, if a crime zone has a radius of 500 meters, this function
    checks if any point on the route is within that 500-meter circle.
    
    Args:
        point_lat (float): Latitude of the point to check
        point_lng (float): Longitude of the point to check
        center_lat (float): Latitude of the zone center
        center_lng (float): Longitude of the zone center
        radius_meters (float): Radius of the zone in meters
    
    Returns:
        bool: True if point is inside the zone, False otherwise
    
    Example:
        >>> is_unsafe = is_point_in_radius(20.2961, 85.8245, 20.2970, 85.8250, 500)
        >>> if is_unsafe:
        ...     print("Warning: Route passes through crime zone!")
    """
    distance_km = calculate_distance(point_lat, point_lng, center_lat, center_lng)
    distance_m = distance_km * 1000
    return distance_m <= radius_meters


def get_proximity_factor(point_lat: float, point_lng: float,
                         center_lat: float, center_lng: float,
                         radius_meters: float) -> float:
    """
    Calculate how close a point is to a zone center (normalized 0-1 scale).
    
    Returns a proximity factor where:
    - 1.0 = point is exactly at the center (most dangerous)
    - 0.5 = point is halfway between center and edge
    - 0.0 = point is outside the radius (safe)
    
    This is used for weighted safety scoring - routes passing through the
    center of a crime zone are more dangerous than routes passing through
    the edge.
    
    Args:
        point_lat (float): Latitude of the point
        point_lng (float): Longitude of the point
        center_lat (float): Latitude of zone center
        center_lng (float): Longitude of zone center
        radius_meters (float): Radius of the zone in meters
    
    Returns:
        float: Proximity factor between 0.0 (far/safe) and 1.0 (close/dangerous)
    
    Example:
        >>> factor = get_proximity_factor(20.2961, 85.8245, 20.2970, 85.8250, 500)
        >>> danger_score = factor * 50
        >>> print(f"Danger contribution: {danger_score:.1f} points")
    """
    distance_km = calculate_distance(point_lat, point_lng, center_lat, center_lng)
    distance_m = distance_km * 1000
    
    if distance_m >= radius_meters:
        return 0.0
    
    return 1.0 - (distance_m / radius_meters)


def get_midpoint(lat1: float, lng1: float, lat2: float, lng2: float) -> Dict[str, float]:
    """
    Calculate the midpoint between two GPS coordinates.
    
    This is useful for finding the center of a route segment or
    dividing a route into smaller sections for analysis.
    
    Args:
        lat1 (float): Latitude of first point
        lng1 (float): Longitude of first point
        lat2 (float): Latitude of second point
        lng2 (float): Longitude of second point
    
    Returns:
        Dict[str, float]: Dictionary with 'lat' and 'lng' keys containing midpoint coordinates
    
    Example:
        >>> start = (20.2961, 85.8245)
        >>> end = (20.3021, 85.8350)
        >>> midpoint = get_midpoint(*start, *end)
        >>> print(f"Midpoint: {midpoint['lat']:.4f}, {midpoint['lng']:.4f}")
    """
    mid_lat = (lat1 + lat2) / 2
    mid_lng = (lng1 + lng2) / 2
    return {"lat": mid_lat, "lng": mid_lng}


def interpolate_points(start_lat: float, start_lng: float,
                       end_lat: float, end_lng: float,
                       num_points: int = 10) -> List[Dict[str, float]]:
    """
    Generate intermediate waypoints between two locations.
    
    This creates a series of GPS points along a straight line between
    start and end points. Used to:
    1. Check if a route passes through unsafe zones
    2. Visualize routes on a map
    3. Sample safety conditions along the entire route
    
    Args:
        start_lat (float): Starting latitude
        start_lng (float): Starting longitude
        end_lat (float): Ending latitude
        end_lng (float): Ending longitude
        num_points (int): Number of intermediate points to generate (default: 10)
    
    Returns:
        List[Dict[str, float]]: List of waypoint dictionaries with 'lat' and 'lng' keys
                                Includes start point, intermediate points, and end point
    
    Example:
        >>> waypoints = interpolate_points(20.2961, 85.8245, 20.3021, 85.8350, num_points=5)
        >>> print(f"Generated {len(waypoints)} waypoints")
    """
    points = []
    
    for i in range(num_points + 1):
        t = i / num_points
        lat = start_lat + (end_lat - start_lat) * t
        lng = start_lng + (end_lng - start_lng) * t
        points.append({"lat": lat, "lng": lng})
    
    return points


def get_bounding_box(points: List[Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """
    Calculate the bounding box (rectangular area) that contains all given points.
    
    A bounding box is defined by its northeast (top-right) and southwest
    (bottom-left) corners. This is useful for:
    1. Map visualization (zoom to fit all points)
    2. Spatial queries (find all zones within route area)
    3. Route comparison (which route covers more area)
    
    Args:
        points (List[Dict[str, float]]): List of GPS points with 'lat' and 'lng' keys
    
    Returns:
        Dict: Dictionary with 'northeast' and 'southwest' keys, each containing
              'lat' and 'lng' coordinates
    
    Example:
        >>> route_points = [
        ...     {"lat": 20.2961, "lng": 85.8245},
        ...     {"lat": 20.3021, "lng": 85.8350}
        ... ]
        >>> bbox = get_bounding_box(route_points)
    """
    if not points:
        return {
            "northeast": {"lat": 0, "lng": 0},
            "southwest": {"lat": 0, "lng": 0}
        }
    
    lats = [p["lat"] for p in points]
    lngs = [p["lng"] for p in points]
    
    return {
        "northeast": {"lat": max(lats), "lng": max(lngs)},
        "southwest": {"lat": min(lats), "lng": min(lngs)}
    }