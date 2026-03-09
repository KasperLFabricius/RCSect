"""Centralized plastic solver conventions.

This module is the single source of truth for production sign, units, and
rotation/orientation behavior used by the plastic solver.
"""

from __future__ import annotations

import math


UNITS = {
    "geometry_coordinates": "m",
    "rebar_area": "mm2",
    "stress": "MPa",
    "force": "kN",
    "moment": "kNm",
    "internal_strain": "fraction",
    "reported_strain": "permille",
}


AXIAL_SIGN_CONVENTION = "compression_positive"
INTERNAL_STRAIN_SIGN_CONVENTION = "tension_positive"
REPORTED_STRAIN_SIGN_CONVENTION = "compression_positive"
ANGLE_CONVENTION = "V is angle between NA and global +Y"


def to_compression_positive(force_internal_signed: float) -> float:
    """Convert internal solver force sign (tension-positive) to compression-positive."""
    return -float(force_internal_signed)


def format_reported_strain(internal_permille: float | None) -> float | None:
    """Convert internal strain sign (tension-positive) to reported sign (compression-positive)."""
    if internal_permille is None:
        return None
    return -float(internal_permille)


def classify_zone_from_total_strain(total_strain: float) -> str:
    """Classify strain field zone from solved total strain."""
    return "compression" if float(total_strain) < 0.0 else "tension"


def rotate_vector_local_to_global(vx_local: float, vy_local: float, angle_rad: float) -> tuple[float, float]:
    """Rotate a local vector to global coordinates using one shared transform."""
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    return (vx_local * c - vy_local * s, vx_local * s + vy_local * c)


def rotate_point_global_to_local(x_global: float, y_global: float, angle_rad: float) -> tuple[float, float]:
    """Rotate global point into local coordinates (inverse of local->global)."""
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    return (x_global * c + y_global * s, -x_global * s + y_global * c)


def rotate_moment_local_to_global(mx_local: float, my_local: float, angle_rad: float) -> tuple[float, float]:
    """Transform local plastic resultants to reported global Mx/My convention."""
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    mx = -float(mx_local) * c + float(my_local) * s
    my = float(mx_local) * s + float(my_local) * c
    return mx, my


def build_internal_arm_vector(
    comp_centroid_x: float | None,
    comp_centroid_y: float | None,
    tens_centroid_x: float | None,
    tens_centroid_y: float | None,
) -> tuple[float, float]:
    """Build compression->tension local arm vector from zone centroids."""
    if None in (comp_centroid_x, comp_centroid_y, tens_centroid_x, tens_centroid_y):
        return (0.0, 0.0)
    return (
        float(tens_centroid_x) - float(comp_centroid_x),
        float(tens_centroid_y) - float(comp_centroid_y),
    )
