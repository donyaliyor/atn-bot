"""
Location validation utilities.
Handles geolocation calculations and validation.


"""
import logging
from typing import Tuple, Optional
from geopy.distance import geodesic
from geopy.exc import GeopyError

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

    COMMIT 3: Enhanced error handling with input validation and detailed logging.

    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point

    Returns:
        float: Distance in meters

    Raises:
        ValueError: If coordinates are invalid
        Exception: If geodesic calculation fails

    Example:
        >>> distance = calculate_distance(35.69, 139.83, 35.69, 139.84)
        >>> print(f"{distance:.2f}m")
    """
    logger.debug("=" * 40)
    logger.debug("CALCULATE_DISTANCE called")
    logger.debug(f"Point 1: ({lat1}, {lon1})")
    logger.debug(f"Point 2: ({lat2}, {lon2})")

    try:
        # Step 1: Validate input types
        try:
            lat1 = float(lat1)
            lon1 = float(lon1)
            lat2 = float(lat2)
            lon2 = float(lon2)
            logger.debug("✓ Coordinates converted to float")
        except (TypeError, ValueError) as type_error:
            logger.error(f"Invalid coordinate types: {type_error}")
            raise ValueError(f"Coordinates must be numeric: {type_error}")

        # Step 2: Validate coordinate ranges
        if not validate_coordinates(lat1, lon1):
            error_msg = f"Point 1 has invalid coordinates: ({lat1}, {lon1})"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if not validate_coordinates(lat2, lon2):
            error_msg = f"Point 2 has invalid coordinates: ({lat2}, {lon2})"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.debug("✓ Coordinate validation passed")

        # Step 3: Calculate distance using geodesic
        try:
            point1 = (lat1, lon1)
            point2 = (lat2, lon2)

            logger.debug(f"Calculating geodesic distance...")
            distance = geodesic(point1, point2).meters

            logger.debug(f"✓ Distance calculated: {distance:.2f}m")
            logger.debug("=" * 40)

            return distance

        except GeopyError as geopy_error:
            logger.error(f"Geopy calculation error: {geopy_error}")
            raise Exception(f"Geodesic calculation failed: {geopy_error}")
        except Exception as calc_error:
            logger.error(f"Unexpected error during distance calculation: {calc_error}")
            raise Exception(f"Distance calculation failed: {calc_error}")

    except ValueError as val_error:
        # Re-raise ValueError for invalid inputs
        logger.error(f"ValueError in calculate_distance: {val_error}")
        raise
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"CRITICAL ERROR in calculate_distance: {e}", exc_info=True)
        logger.error("=" * 40)
        raise Exception(f"Failed to calculate distance: {e}")


def is_within_radius(
    user_latitude: float,
    user_longitude: float,
    school_latitude: Optional[float] = None,
    school_longitude: Optional[float] = None,
    radius_meters: Optional[int] = None
) -> Tuple[bool, float]:
    """
    Check if user is within allowed radius of school.

    COMMIT 3: Enhanced with comprehensive error handling and defensive defaults.

    Args:
        user_latitude: User's current latitude
        user_longitude: User's current longitude
        school_latitude: School's latitude (default: from config)
        school_longitude: School's longitude (default: from config)
        radius_meters: Allowed radius in meters (default: from config)

    Returns:
        Tuple[bool, float]: (is_within_radius, actual_distance)

    Raises:
        ValueError: If coordinates are invalid
        Exception: If distance calculation fails

    Example:
        >>> within, distance = is_within_radius(35.69, 139.83)
        >>> if within:
        ...     print(f"Within radius: {distance:.2f}m")
        ... else:
        ...     print(f"Too far: {distance:.2f}m away")
    """
    logger.info("=" * 60)
    logger.info("IS_WITHIN_RADIUS check started")

    try:
        # Step 1: Use defaults from Config if not provided
        if school_latitude is None:
            school_latitude = Config.SCHOOL_LATITUDE
            logger.debug(f"Using default school latitude: {school_latitude}")

        if school_longitude is None:
            school_longitude = Config.SCHOOL_LONGITUDE
            logger.debug(f"Using default school longitude: {school_longitude}")

        if radius_meters is None:
            radius_meters = Config.RADIUS_METERS
            logger.debug(f"Using default radius: {radius_meters}m")

        logger.info(f"User location: ({user_latitude:.6f}, {user_longitude:.6f})")
        logger.info(f"School location: ({school_latitude:.6f}, {school_longitude:.6f})")
        logger.info(f"Required radius: {radius_meters}m")

        # Step 2: Validate radius value
        try:
            radius_meters = int(radius_meters)
            if radius_meters <= 0:
                raise ValueError(f"Radius must be positive, got: {radius_meters}")
            logger.debug(f"✓ Radius validated: {radius_meters}m")
        except (TypeError, ValueError) as radius_error:
            logger.error(f"Invalid radius value: {radius_error}")
            raise ValueError(f"Invalid radius: {radius_error}")

        # Step 3: Calculate distance
        try:
            logger.debug("Calculating distance from user to school...")
            distance = calculate_distance(
                user_latitude,
                user_longitude,
                school_latitude,
                school_longitude
            )
            logger.info(f"✓ Distance calculated: {distance:.2f}m")
        except ValueError as dist_error:
            logger.error(f"Invalid coordinates for distance calculation: {dist_error}")
            raise
        except Exception as calc_error:
            logger.error(f"Error calculating distance: {calc_error}")
            raise Exception(f"Distance calculation failed: {calc_error}")

        # Step 4: Check if within radius
        is_within = distance <= radius_meters

        status = "WITHIN" if is_within else "OUTSIDE"
        logger.info(f"✓ Result: {status} radius")
        logger.info(f"  Distance: {distance:.2f}m")
        logger.info(f"  Allowed: {radius_meters}m")

        if not is_within:
            diff = distance - radius_meters
            logger.info(f"  Too far by: {diff:.2f}m")

        logger.info("IS_WITHIN_RADIUS check completed")
        logger.info("=" * 60)

        return is_within, distance

    except ValueError as val_error:
        logger.error(f"ValueError in is_within_radius: {val_error}")
        logger.error("=" * 60)
        raise
    except Exception as e:
        logger.error(f"CRITICAL ERROR in is_within_radius: {e}", exc_info=True)
        logger.error("=" * 60)
        raise Exception(f"Radius check failed: {e}")


def format_coordinates(latitude: float, longitude: float) -> str:
    """
    Format coordinates for display.

    COMMIT 3: Enhanced with error handling for invalid inputs.

    Args:
        latitude: Latitude value
        longitude: Longitude value

    Returns:
        str: Formatted coordinate string

    Raises:
        ValueError: If coordinates cannot be formatted

    Example:
        >>> format_coordinates(35.69176, 139.83941)
        '35.6918°N, 139.8394°E'
    """
    try:
        # Convert to float if not already
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError) as type_error:
            logger.error(f"Cannot convert coordinates to float: {type_error}")
            raise ValueError(f"Invalid coordinate types: {type_error}")

        # Validate coordinates
        if not validate_coordinates(latitude, longitude):
            logger.error(f"Invalid coordinates for formatting: ({latitude}, {longitude})")
            raise ValueError(f"Coordinates out of valid range: ({latitude}, {longitude})")

        # Format with direction indicators
        lat_dir = 'N' if latitude >= 0 else 'S'
        lon_dir = 'E' if longitude >= 0 else 'W'

        formatted = f"{abs(latitude):.4f}°{lat_dir}, {abs(longitude):.4f}°{lon_dir}"
        logger.debug(f"Formatted coordinates: {formatted}")

        return formatted

    except ValueError as val_error:
        logger.error(f"ValueError in format_coordinates: {val_error}")
        raise
    except Exception as e:
        logger.error(f"Error formatting coordinates: {e}", exc_info=True)
        # Return a safe fallback
        return f"({latitude}, {longitude})"


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate coordinate values are within valid ranges.

    COMMIT 3: Enhanced with detailed logging and robust type handling.

    Args:
        latitude: Latitude value (-90 to 90)
        longitude: Longitude value (-180 to 180)

    Returns:
        bool: True if coordinates are valid, False otherwise

    Example:
        >>> validate_coordinates(35.69, 139.83)
        True
        >>> validate_coordinates(91.0, 200.0)
        False
    """
    try:
        # Try to convert to float
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError) as type_error:
            logger.warning(f"Cannot convert coordinates to float: {type_error}")
            return False

        # Check for NaN or infinity
        import math
        if math.isnan(latitude) or math.isnan(longitude):
            logger.warning(f"Coordinates contain NaN: lat={latitude}, lon={longitude}")
            return False

        if math.isinf(latitude) or math.isinf(longitude):
            logger.warning(f"Coordinates contain infinity: lat={latitude}, lon={longitude}")
            return False

        # Validate latitude range (-90 to 90)
        if not (-90 <= latitude <= 90):
            logger.warning(f"Invalid latitude (must be -90 to 90): {latitude}")
            return False

        # Validate longitude range (-180 to 180)
        if not (-180 <= longitude <= 180):
            logger.warning(f"Invalid longitude (must be -180 to 180): {longitude}")
            return False

        logger.debug(f"✓ Coordinates valid: ({latitude:.6f}, {longitude:.6f})")
        return True

    except Exception as e:
        logger.error(f"Unexpected error in validate_coordinates: {e}", exc_info=True)
        # Return False on any unexpected error (defensive)
        return False


def get_distance_description(distance: float) -> str:
    """
    Get a human-readable description of distance.

    COMMIT 3: New helper function for better user feedback.

    Args:
        distance: Distance in meters

    Returns:
        str: Human-readable description

    Example:
        >>> get_distance_description(150.5)
        '150m away'
        >>> get_distance_description(1250)
        '1.2km away'
    """
    try:
        distance = float(distance)

        if distance < 0:
            return "invalid distance"
        elif distance < 1000:
            return f"{distance:.0f}m away"
        else:
            km = distance / 1000
            return f"{km:.1f}km away"

    except Exception as e:
        logger.error(f"Error formatting distance description: {e}")
        return f"{distance}m away"


def is_location_reasonable(latitude: float, longitude: float) -> bool:
    """
    Check if coordinates represent a reasonable real-world location.

    COMMIT 3: New validation function for additional safety.
    Checks for obviously fake coordinates like (0, 0) or extreme values.

    Args:
        latitude: Latitude value
        longitude: Longitude value

    Returns:
        bool: True if location seems reasonable

    Example:
        >>> is_location_reasonable(0, 0)  # Middle of ocean
        False
        >>> is_location_reasonable(41.2995, 69.2401)  # Tashkent
        True
    """
    try:
        # First check basic validity
        if not validate_coordinates(latitude, longitude):
            return False

        # Check for (0, 0) - often indicates GPS failure
        if latitude == 0 and longitude == 0:
            logger.warning("Coordinates are (0, 0) - likely GPS error")
            return False

        # Check for values that are too precise (fake data)
        # Real GPS usually has some variance in decimal places
        lat_str = str(latitude)
        lon_str = str(longitude)

        # If both coordinates end with many zeros, might be fake
        if lat_str.endswith('00000') and lon_str.endswith('00000'):
            logger.warning("Coordinates suspiciously precise - may be fake")
            return False

        return True

    except Exception as e:
        logger.error(f"Error in is_location_reasonable: {e}")
        # Default to True to not block valid locations
        return True
