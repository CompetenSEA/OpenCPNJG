from pathlib import Path

import sys

import pytest
from shapely.geometry import Point


BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from lights import build_light_sectors, build_light_character


def test_sector_geometry_snapshot():
    pt = Point(0, 0)
    geom = build_light_sectors(pt, {"SECTR1": 0, "SECTR2": 90, "VALNMR": 6})
    expected = (
        "MULTIPOLYGON (((0 0, 0 0.1, 0.017364817766693 0.0984807753012208, "
        "0.0342020143325669 0.0939692620785908, 0.05 0.0866025403784439, "
        "0.0642787609686539 0.0766044443118978, 0.0766044443118978 "
        "0.0642787609686539, 0.0866025403784439 0.05, 0.0939692620785908 "
        "0.0342020143325669, 0.0984807753012208 0.017364817766693, 0.1 "
        "6.123233995736766e-18, 0 0)))"
    )
    assert geom.wkt == expected


def test_light_character_deterministic():
    attrs = {
        "LITCHR": "Fl",
        "SIGGRP": "(3)",
        "COLOUR": "red",
        "SIGPER": "5s",
        "VALNMR": 10,
        "SECTR1": 0,
        "SECTR2": 90,
    }
    code = build_light_character(attrs)
    assert code == 2112210742
    # Call again to ensure deterministic
    assert build_light_character(attrs) == code

