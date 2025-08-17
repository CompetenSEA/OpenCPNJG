import math


def xyz_to_bbox(z: int, x: int, y: int) -> tuple[float, float, float, float]:
    """Convert slippy-map tile z/x/y to WGS84 bbox.

    Returns (west, south, east, north) in degrees.
    """
    n = 2 ** z
    west = x / n * 360.0 - 180.0
    east = (x + 1) / n * 360.0 - 180.0
    lat_rad_n = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_rad_s = math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n)))
    north = math.degrees(lat_rad_n)
    south = math.degrees(lat_rad_s)
    return west, south, east, north


def bbox_to_xyz(z: int, west: float, south: float, east: float, north: float) -> tuple[int, int]:
    """Convert WGS84 bbox to slippy-map tile coordinates.

    The bbox is expected to align to tile boundaries produced by
    :func:`xyz_to_bbox`.
    """
    n = 2 ** z
    x = int((west + 180.0) / 360.0 * n)
    lat_rad = math.radians(north)
    value = (1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2 * n
    y = int(round(value))
    return x, y
