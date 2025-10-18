"""
Location validation utilities.
Handles geolocation calculations and validation.
"""
import logging
from typing import Tuple
from geopy.distance import geodesic

from config import Config

logger = logging.getLogger(__name__)


def calculate_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate distance between two points using geodesic formula.

    Uses geopy's geodesic calculation which is more accurate than
    haversine as it accounts for Earth's ellipsoidal shape.

    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point

    Returns:
        float: Distance in meters

    Example:
        >>> distance = calculate_distance(35.69, 139.83, 35.69, 139.84)
        >>> print(f"{distance:.2f}m")
    """
    try:
        point1 = (lat1, lon1)
        point2 = (lat2, lon2)

        distance = geodesic(point1, point2).meters
        logger.debug(f"Distance calculated: {distance:.2f}m between {point1} and {point2}")

        return distance

    except Exception as e:
        logger.error(f"Error calculating distance: {e}")
        raise


def is_within_radius(
    user_latitude: float,
    user_longitude: float,
    school_latitude: float = Config.SCHOOL_LATITUDE,
    school_longitude: float = Config.SCHOOL_LONGITUDE,
    radius_meters: int = Config.RADIUS_METERS
) -> Tuple[bool, float]:
    """
    Check if user is within allowed radius of school.

    Args:
        user_latitude: User's current latitude
        user_longitude: User's current longitude
        school_latitude: School's latitude (default: from config)
        school_longitude: School's longitude (default: from config)
        radius_meters: Allowed radius in meters (default: from config)

    Returns:
        Tuple[bool, float]: (is_within_radius, actual_distance)

    Example:
        >>> within, distance = is_within_radius(35.69, 139.83)
        >>> if within:
        ...     print(f"Within radius: {distance:.2f}m")
        ... else:
        ...     print(f"Too far: {distance:.2f}m away")
    """
    try:
        distance = calculate_distance(
            user_latitude,
            user_longitude,
            school_latitude,
            school_longitude
        )

        is_within = distance <= radius_meters

        logger.info(
            f"Location check: {distance:.2f}m from school "
            f"({'WITHIN' if is_within else 'OUTSIDE'} {radius_meters}m radius)"
        )

        return is_within, distance

    except Exception as e:
        logger.error(f"Error checking radius: {e}")
        raise


def format_coordinates(latitude: float, longitude: float) -> str:
    """
    Format coordinates for display.

    Args:
        latitude: Latitude value
        longitude: Longitude value

    Returns:
        str: Formatted coordinate string

    Example:
        >>> format_coordinates(35.69176, 139.83941)
        '35.6918°N, 139.8394°E'
    """
    lat_dir = 'N' if latitude >= 0 else 'S'
    lon_dir = 'E' if longitude >= 0 else 'W'

    return f"{abs(latitude):.4f}°{lat_dir}, {abs(longitude):.4f}°{lon_dir}"


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate coordinate values are within valid ranges.

    Args:
        latitude: Latitude value (-90 to 90)
        longitude: Longitude value (-180 to 180)

    Returns:
        bool: True if coordinates are valid

    Example:
        >>> validate_coordinates(35.69, 139.83)
        True
        >>> validate_coordinates(91.0, 200.0)
        False
    """
    if not (-90 <= latitude <= 90):
        logger.warning(f"Invalid latitude: {latitude}")
        return False

    if not (-180 <= longitude <= 180):
        logger.warning(f"Invalid longitude: {longitude}")
        return False

    return True
