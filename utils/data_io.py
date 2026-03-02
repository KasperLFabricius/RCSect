import copy
import json
import os
import time

import streamlit as st
from shapely.geometry import LinearRing, Point, Polygon
from shapely.validation import explain_validity

AUTOSAVE_FILE = "rcsect_autosave.json"


def _coerce_float(value):
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_int(value):
    try:
        if value in (None, ""):
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def coerce_point_rows(rows):
    cleaned = []
    for row in rows or []:
        x_val = _coerce_float(row.get("x"))
        y_val = _coerce_float(row.get("y"))
        if x_val is None or y_val is None:
            continue
        point_id = _coerce_int(row.get("id"))
        cleaned.append({"id": point_id, "x": x_val, "y": y_val})
    return cleaned


def coerce_rebar_rows(rows, include_eps0=False):
    cleaned = []
    for row in rows or []:
        x_val = _coerce_float(row.get("x"))
        y_val = _coerce_float(row.get("y"))
        area_val = _coerce_float(row.get("area"))
        if x_val is None or y_val is None or area_val is None:
            continue

        bar = {
            "id": _coerce_int(row.get("id")),
            "x": x_val,
            "y": y_val,
            "area": area_val,
        }
        if include_eps0 and "eps0" in row:
            eps0_val = _coerce_float(row.get("eps0"))
            if eps0_val is not None:
                bar["eps0"] = eps0_val
        cleaned.append(bar)
    return cleaned


def _get_example_geometry():
    return {
        "concrete_outline": [
            {"id": 1, "x": -0.60, "y": 0.35},
            {"id": 2, "x": 0.60, "y": 0.35},
            {"id": 3, "x": 0.60, "y": 0.15},
            {"id": 4, "x": 0.15, "y": 0.15},
            {"id": 5, "x": 0.15, "y": -0.65},
            {"id": 6, "x": -0.15, "y": -0.65},
            {"id": 7, "x": -0.15, "y": 0.15},
            {"id": 8, "x": 0.60, "y": 0.15},
        ],
        "concrete_voids": [],
        "reinforcement_mild": [
            {"id": 1, "x": -0.55, "y": 0.30, "area": 491.0},
            {"id": 2, "x": 0.55, "y": 0.30, "area": 491.0},
            {"id": 3, "x": -0.10, "y": -0.60, "area": 314.0},
            {"id": 4, "x": 0.10, "y": -0.60, "area": 314.0},
        ],
        "reinforcement_prestressed": [
            {"id": 5, "x": 0.00, "y": -0.38, "area": 1016.0},
            {"id": 6, "x": 0.00, "y": -0.54, "area": 1016.0},
        ],
    }


def _get_default_schema():
    """Returns the full foundational JSON structure with default values."""
    return {
        "project_metadata": {
            "project_number": "",
            "project_name": "",
            "engineer": "",
            "date": "",
        },
        "analysis_settings": {
            "mode": "Both",
            "autosave_enabled": True,
            "autosave_interval_seconds": 60,
        },
        "materials": {
            "concrete": {"f_ck": 30.0, "gamma_c": 1.45, "alpha_cc": 1.0},
            "mild_steel": {
                "f_yk": 500.0,
                "gamma_s": 1.20,
                "e_uk": 0.05,
                "include_hardening": False,
                "f_uk": 550.0,
            },
            "prestressed_steel": {
                "f_p01k": 1500.0,
                "f_pk": 1700.0,
                "gamma_p": 1.20,
                "initial_strain": 0.004,
                "e_uk": 0.035,
            },
        },
        "geometry": {
            "concrete_outline": [],
            "concrete_voids": [],
            "reinforcement_mild": [],
            "reinforcement_prestressed": [],
        },
        "plot_options": {
            "show_concrete_point_ids": False,
            "show_void_point_ids": False,
            "show_mild_bar_ids": False,
            "show_prestressed_bar_ids": False,
            "scale_bar_markers_by_area": False,
        },
        "load_cases": {
            "elastic": [
                {
                    "id": 1,
                    "name": "Default elastic case",
                    "P_l": 408.98,
                    "Mx_l": -49.87,
                    "My_l": 0.0,
                    "n_l": 22.93,
                    "P_s": -5.45,
                    "Mx_s": -36.12,
                    "My_s": 0.0,
                    "n_s": 5.733,
                }
            ],
            "plastic": [
                {
                    "id": 1,
                    "name": "Default plastic case",
                    "P_target": 1976.0,
                    "v_min": 0.0,
                    "v_max": 360.0,
                    "v_inc": 10.0,
                }
            ],
        },
    }


def _normalize_load_cases(load_cases):
    defaults = _get_default_schema()["load_cases"]
    if not isinstance(load_cases, dict):
        return defaults
    elastic = load_cases.get("elastic")
    plastic = load_cases.get("plastic")
    if not isinstance(elastic, list):
        elastic = defaults["elastic"]
    if not isinstance(plastic, list):
        plastic = defaults["plastic"]
    return {"elastic": elastic, "plastic": plastic}


def normalize_point_ids(geometry):
    normalized = copy.deepcopy(geometry or {})

    outline = coerce_point_rows(normalized.get("concrete_outline", []))
    outline.sort(key=lambda pt: pt["id"] if pt["id"] is not None else 10**9)
    normalized_outline = []
    for idx, pt in enumerate(outline, start=1):
        normalized_outline.append({"id": idx, "x": float(pt["x"]), "y": float(pt["y"])})
    normalized["concrete_outline"] = normalized_outline

    normalized_voids = []
    for void in normalized.get("concrete_voids", []):
        void_points = coerce_point_rows(void)
        void_points.sort(key=lambda pt: pt["id"] if pt["id"] is not None else 10**9)
        normalized_void = []
        for idx, pt in enumerate(void_points, start=1):
            normalized_void.append({"id": idx, "x": float(pt["x"]), "y": float(pt["y"])})
        normalized_voids.append(normalized_void)
    normalized["concrete_voids"] = normalized_voids

    normalized["reinforcement_mild"] = coerce_rebar_rows(normalized.get("reinforcement_mild", []))
    normalized["reinforcement_prestressed"] = coerce_rebar_rows(
        normalized.get("reinforcement_prestressed", []), include_eps0=True
    )
    return normalized


def normalize_rebar_ids(geometry):
    normalized = copy.deepcopy(geometry or {})
    mild = coerce_rebar_rows(normalized.get("reinforcement_mild", []))
    prestressed = coerce_rebar_rows(normalized.get("reinforcement_prestressed", []), include_eps0=True)
    all_ids = [bar.get("id") for bar in mild + prestressed]
    valid_ids = [bar_id for bar_id in all_ids if isinstance(bar_id, int) and bar_id > 0]
    has_all_ids = len(valid_ids) == len(all_ids)
    has_unique_ids = len(set(valid_ids)) == len(valid_ids)

    if has_all_ids and has_unique_ids:
        normalized["reinforcement_mild"] = mild
        normalized["reinforcement_prestressed"] = prestressed
        return normalized

    next_id = 1
    for bar in mild:
        bar["id"] = next_id
        next_id += 1
    for bar in prestressed:
        bar["id"] = next_id
        next_id += 1

    normalized["reinforcement_mild"] = mild
    normalized["reinforcement_prestressed"] = prestressed
    return normalized


def validate_winding_constraints(geometry_data):
    geometry_data = copy.deepcopy(geometry_data or {})
    outline = geometry_data.get("concrete_outline", [])
    if len(outline) >= 3:
        ring = LinearRing([(pt["x"], pt["y"]) for pt in outline])
        if ring.is_ccw:
            geometry_data["concrete_outline"] = list(reversed(outline))

    normalized_voids = []
    for void in geometry_data.get("concrete_voids", []):
        if len(void) >= 3:
            ring = LinearRing([(pt["x"], pt["y"]) for pt in void])
            if not ring.is_ccw:
                void = list(reversed(void))
        normalized_voids.append(void)
    geometry_data["concrete_voids"] = normalized_voids
    return geometry_data


def normalize_geometry_for_use(geometry):
    normalized = normalize_point_ids(geometry)
    normalized = normalize_rebar_ids(normalized)
    normalized = validate_winding_constraints(normalized)
    return normalized


def geometry_to_polygon(geometry_data):
    outline = sorted(geometry_data.get("concrete_outline", []), key=lambda pt: pt["id"])
    if len(outline) < 3:
        return None
    shell = [(pt["x"], pt["y"]) for pt in outline]
    holes = []
    for void in geometry_data.get("concrete_voids", []):
        ordered = sorted(void, key=lambda pt: pt["id"])
        if len(ordered) < 3:
            continue
        holes.append([(pt["x"], pt["y"]) for pt in ordered])
    try:
        return Polygon(shell, holes)
    except Exception:
        return None


def initialize_session_state():
    if "data" not in st.session_state:
        if os.path.exists(AUTOSAVE_FILE):
            try:
                with open(AUTOSAVE_FILE, "r", encoding="utf-8") as f:
                    st.session_state.data = json.load(f)
            except (json.JSONDecodeError, OSError):
                st.session_state.data = _get_default_schema()
        else:
            st.session_state.data = _get_default_schema()

    data = st.session_state.data
    defaults = _get_default_schema()
    data.setdefault("analysis_settings", {})
    data["analysis_settings"].setdefault("mode", defaults["analysis_settings"]["mode"])
    data["analysis_settings"].setdefault("autosave_enabled", True)
    data["analysis_settings"].setdefault("autosave_interval_seconds", 60)
    data["load_cases"] = _normalize_load_cases(data.get("load_cases"))
    data.setdefault("plot_options", defaults["plot_options"])
    data.setdefault("geometry", defaults["geometry"])
    data["geometry"] = normalize_geometry_for_use(data["geometry"])


def handle_autosave():
    data = st.session_state.data
    settings = data["analysis_settings"]
    if not settings.get("autosave_enabled", True):
        return

    if "last_save_time" not in st.session_state:
        st.session_state.last_save_time = 0.0

    current_time = time.time()
    interval = int(settings.get("autosave_interval_seconds", 60))
    if current_time - st.session_state.last_save_time <= interval:
        return

    data["geometry"] = normalize_geometry_for_use(data["geometry"])
    with open(AUTOSAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    st.session_state.last_save_time = current_time
    st.session_state.last_autosave_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")


def export_json():
    return json.dumps(st.session_state.data, indent=4)


def validate_geometry_topology(geometry_data):
    result = {"errors": [], "warnings": []}

    outline_pts = geometry_data.get("concrete_outline", [])
    if len(outline_pts) < 3:
        result["warnings"].append(
            "Outline has fewer than 3 points; add at least 3 points to define a valid polygon."
        )
        return result

    outer = Polygon([(pt["x"], pt["y"]) for pt in outline_pts])
    if not outer.is_valid or outer.area <= 0:
        validity = explain_validity(outer)
        result["errors"].append(
            f"Outline is invalid ({validity}); fix self-intersections/duplicate points and ensure non-zero area."
        )

    void_polys = []
    for idx, void_pts in enumerate(geometry_data.get("concrete_voids", []), start=1):
        if len(void_pts) < 3:
            result["warnings"].append(f"Void {idx} has fewer than 3 points; add points or remove this void.")
            void_polys.append(None)
            continue

        void_poly = Polygon([(pt["x"], pt["y"]) for pt in void_pts])
        void_polys.append(void_poly)

        if not void_poly.is_valid or void_poly.area <= 0:
            validity = explain_validity(void_poly)
            result["errors"].append(
                f"Void {idx} is invalid ({validity}); fix self-intersections/duplicate points and ensure non-zero area."
            )

        if not outer.contains(void_poly):
            result["errors"].append(f"Void {idx} is not fully inside the outline; move it fully inside the concrete boundary.")

        if outer.touches(void_poly):
            result["errors"].append(
                f"Void {idx} intersects outer boundary; move it fully inside the outline with clear offset."
            )

    for i in range(len(void_polys)):
        if void_polys[i] is None:
            continue
        for j in range(i + 1, len(void_polys)):
            if void_polys[j] is None:
                continue
            if void_polys[i].intersects(void_polys[j]):
                result["errors"].append(f"Void {i + 1} intersects Void {j + 1}; separate them so they do not touch or overlap.")

    for idx, bar in enumerate(geometry_data.get("reinforcement_mild", []), start=1):
        point = Point(bar["x"], bar["y"])
        if not outer.contains(point):
            result["warnings"].append(
                f"Mild reinforcement bar {idx} is outside the outline; move it inside the concrete polygon."
            )
            continue
        for void_idx, void_poly in enumerate(void_polys, start=1):
            if void_poly is not None and (void_poly.contains(point) or void_poly.touches(point)):
                result["warnings"].append(
                    f"Mild reinforcement bar {idx} lies in Void {void_idx}; relocate it to solid concrete."
                )
                break

    for idx, bar in enumerate(geometry_data.get("reinforcement_prestressed", []), start=1):
        point = Point(bar["x"], bar["y"])
        if not outer.contains(point):
            result["warnings"].append(
                f"Prestressed reinforcement bar {idx} is outside the outline; move it inside the concrete polygon."
            )
            continue
        for void_idx, void_poly in enumerate(void_polys, start=1):
            if void_poly is not None and (void_poly.contains(point) or void_poly.touches(point)):
                result["warnings"].append(
                    f"Prestressed reinforcement bar {idx} lies in Void {void_idx}; relocate it to solid concrete."
                )
                break

    return result


def load_example_geometry():
    return normalize_geometry_for_use(_get_example_geometry())
