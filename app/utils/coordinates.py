import math

from app.schemas.user_schema import LocationBase


def get_distance_between_coordinates(
    coordinates1: LocationBase, coordinates2: LocationBase
):
    # Earth radius in kilometers
    R = 6371.0

    # Coordinates (latitude, longitude)
    latitude1 = coordinates1.latitude
    longitude1 = coordinates1.longitude

    latitude2 = coordinates2.latitude
    longitude2 = coordinates2.longitude

    # Convert latitude and longitude from degrees to radians
    latitude1 = math.radians(latitude1)
    longitude1 = math.radians(longitude1)
    latitude2 = math.radians(latitude2)
    longitude2 = math.radians(longitude2)

    # Differences in coordinates
    dlat = latitude2 - latitude1
    dlon = longitude2 - longitude1

    # Haversine formula
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(latitude1) * math.cos(latitude2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = R * c

    return round(distance, 2)
