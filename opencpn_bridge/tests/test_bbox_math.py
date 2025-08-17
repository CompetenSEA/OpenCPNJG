from opencpn_bridge.py.util_bbox import xyz_to_bbox, bbox_to_xyz


def test_round_trip_xyz_bbox():
    cases = [
        (0, 0, 0),
        (1, 1, 1),
        (2, 2, 3),
        (5, 11, 22),
        (10, 345, 678),
    ]
    for z, x, y in cases:
        bbox = xyz_to_bbox(z, x, y)
        x2, y2 = bbox_to_xyz(z, *bbox)
        assert (x2, y2) == (x, y)
        west, south, east, north = bbox
        assert west < east
        assert south < north
