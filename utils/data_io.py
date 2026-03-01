import json
import os
import time
import streamlit as st
from shapely.geometry import LinearRing, Point, Polygon
from shapely.validation import explain_validity

AUTOSAVE_FILE = "rcsect_autosave.json"

def initialize_session_state():
    """Loads the autosave file if it exists, otherwise creates the default JSON schema."""
    if "data" not in st.session_state:
        if os.path.exists(AUTOSAVE_FILE):
            try:
                with open(AUTOSAVE_FILE, 'r') as f:
                    st.session_state.data = json.load(f)
            except json.JSONDecodeError:
                st.session_state.data = _get_default_schema()
        else:
            st.session_state.data = _get_default_schema()

        st.session_state.data["geometry"] = validate_winding_constraints(
            st.session_state.data["geometry"]
        )

def _get_default_schema():
    """Returns the full foundational JSON structure with default values."""
    return {
        "project_metadata": {
            "project_number": "",
            "project_name": "",
            "engineer": "",
            "date": ""
        },
        "analysis_settings": {
            "mode": "Both", 
            "autosave_interval_seconds": 60
        },
        "materials": {
            "concrete": {"f_ck": 30.0, "gamma_c": 1.45, "alpha_cc": 1.0},
            "mild_steel": {
                "f_yk": 500.0, "gamma_s": 1.20, "e_uk": 0.05, 
                "include_hardening": False, "f_uk": 550.0
            },
            "prestressed_steel": {
                "f_p01k": 1500.0, "f_pk": 1700.0, "gamma_p": 1.20, 
                "initial_strain": 0.004, "e_uk": 0.035
            }
        },
        "geometry": {
            "concrete_outline": [
                {"x": -0.60, "y": 0.35},
                {"x": 0.60, "y": 0.35},
                {"x": 0.60, "y": 0.15},
                {"x": 0.15, "y": 0.15},
                {"x": 0.15, "y": -0.65},
                {"x": -0.15, "y": -0.65},
                {"x": -0.15, "y": 0.15}
            ],
            "concrete_voids": [],
            "reinforcement_mild": [
                {"id": 1, "x": -0.55, "y": 0.30, "area": 491.0},
                {"id": 2, "x": 0.55, "y": 0.30, "area": 491.0},
                {"id": 3, "x": -0.10, "y": -0.60, "area": 314.0},
                {"id": 4, "x": 0.10, "y": -0.60, "area": 314.0}
            ],
            "reinforcement_prestressed": [
                {"id": 29, "x": 0.00, "y": -0.38, "area": 1016.0},
                {"id": 30, "x": 0.00, "y": -0.54, "area": 1016.0}
            ]
        },
        "load_cases": []
    }

def handle_autosave():
    """
    Checks the time elapsed since the last save. 
    If it exceeds the interval, dumps the session state to a local JSON file.
    """
    if "last_save_time" not in st.session_state:
        st.session_state.last_save_time = time.time()
        
    current_time = time.time()
    interval = st.session_state.data["analysis_settings"].get("autosave_interval_seconds", 60)
    
    if current_time - st.session_state.last_save_time > interval:
        st.session_state.data["geometry"] = validate_winding_constraints(
            st.session_state.data["geometry"]
        )
        with open(AUTOSAVE_FILE, 'w') as f:
            json.dump(st.session_state.data, f, indent=4)
        st.session_state.last_save_time = current_time

def export_json():
    """Returns a formatted JSON string for the user to download."""
    return json.dumps(st.session_state.data, indent=4)
    
def validate_winding_constraints(geometry_data):
    """
    Enforces the rule: concrete outline must be clockwise,
    voids must be counterclockwise.
    """
    outline = geometry_data.get("concrete_outline", [])
    if len(outline) >= 3:
        ring = LinearRing([(pt['x'], pt['y']) for pt in outline])
        if ring.is_ccw:
            # Reverse to enforce clockwise
            geometry_data["concrete_outline"].reverse()
            
    for void in geometry_data.get("concrete_voids", []):
        if len(void) >= 3:
            ring = LinearRing([(pt['x'], pt['y']) for pt in void])
            if not ring.is_ccw:
                # Reverse to enforce counterclockwise
                void.reverse()
    return geometry_data


def validate_geometry_topology(geometry_data):
    """Validates geometry topology and returns actionable errors/warnings."""
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
            result["warnings"].append(
                f"Void {idx} has fewer than 3 points; add points or remove this void."
            )
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
            result["errors"].append(
                f"Void {idx} is not fully inside the outline; move it fully inside the concrete boundary."
            )

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
                result["errors"].append(
                    f"Void {i + 1} intersects Void {j + 1}; separate them so they do not touch or overlap."
                )

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
