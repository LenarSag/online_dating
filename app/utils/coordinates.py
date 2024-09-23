import math

from app.schemas.user_schema import LocationBase


def get_distance_between_coordinates(coord1: LocationBase, coord2: LocationBase):
    # Earth radius in kilometers
    R = 6371.0

    # Coordinates (latitude, longitude)
    lat1 = coord1.latitude
    lon1 = coord1.longitude

    lat2 = coord2.latitude
    lon2 = coord2.longitude

    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = R * c

    return round(distance, 2)
