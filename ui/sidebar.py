import uuid

import pandas as pd
import streamlit as st

from ui.aggrid_points import edit_ordered_points
from utils.data_io import (
    coerce_rebar_rows,
    initialize_session_state,
    load_example_geometry,
    normalize_geometry_for_use,
    validate_geometry_topology,
)


GEOMETRY_EDITOR_BASE_KEYS = ["editor_outline", "editor_mild", "editor_pre"]


def _seed_widget(key, value):
    if key.startswith("editor_"):
        return
    if key not in st.session_state:
        st.session_state[key] = value


def _reset_widget_keys(keys: list[str]) -> None:
    for key in keys:
        st.session_state.pop(key, None)


def reset_geometry_editor_widgets(clear_void_keys: bool = True) -> None:
    keys_to_clear = list(GEOMETRY_EDITOR_BASE_KEYS)
    void_keys = list(st.session_state.get("void_editor_keys", []))
    keys_to_clear.extend([f"editor_void_{k}" for k in void_keys])

    # hygiene: clear orphaned void editor keys too
    for key in list(st.session_state.keys()):
        if key.startswith("editor_void_") and key not in keys_to_clear:
            keys_to_clear.append(key)

    _reset_widget_keys(keys_to_clear)

    if clear_void_keys:
        st.session_state.pop("void_editor_keys", None)


def reset_load_case_editor_widgets() -> None:
    _reset_widget_keys(["editor_load_cases_elastic", "editor_load_cases_plastic"])


def _rebuild_void_editor_keys_from_geometry() -> None:
    st.session_state.void_editor_keys = [
        str(uuid.uuid4()) for _ in st.session_state.data["geometry"].get("concrete_voids", [])
    ]


def _ensure_grid_versions() -> None:
    versions = st.session_state.setdefault("grid_versions", {})
    versions.setdefault("outline", 0)
    for void_uuid in st.session_state.get("void_editor_keys", []):
        versions.setdefault(f"void_{void_uuid}", 0)


def _bump_grid_version(grid_key: str) -> None:
    _ensure_grid_versions()
    st.session_state.grid_versions[grid_key] = st.session_state.grid_versions.get(grid_key, 0) + 1


def _is_reversed(lhs: list[dict], rhs: list[dict]) -> bool:
    lhs_xy = [(pt.get("x"), pt.get("y")) for pt in lhs]
    rhs_xy = [(pt.get("x"), pt.get("y")) for pt in rhs]
    return len(lhs_xy) >= 3 and lhs_xy == list(reversed(rhs_xy))



def render_sidebar():
    initialize_session_state()
    data = st.session_state.data

    st.sidebar.header("Global Settings")
    settings = data["analysis_settings"]

    _seed_widget("analysis_mode", settings.get("mode", "Both"))
    st.sidebar.radio("Analysis Mode", ["Elastic", "Plastic", "Both"], key="analysis_mode")
    settings["mode"] = st.session_state.analysis_mode

    _seed_widget("autosave_enabled", settings.get("autosave_enabled", True))
    st.sidebar.checkbox("Enable autosave", key="autosave_enabled")
    settings["autosave_enabled"] = bool(st.session_state.autosave_enabled)

    _seed_widget("autosave_interval_seconds", int(settings.get("autosave_interval_seconds", 60)))
    st.sidebar.number_input(
        "Autosave interval (seconds)", min_value=5, max_value=600, step=5, key="autosave_interval_seconds"
    )
    settings["autosave_interval_seconds"] = int(st.session_state.autosave_interval_seconds)

    if st.session_state.get("last_autosave_timestamp"):
        st.sidebar.caption(f"Last autosave: {st.session_state['last_autosave_timestamp']}")

    st.sidebar.divider()
    tab_mat, tab_geom, tab_load = st.sidebar.tabs(["Materials", "Geometry Input", "Load Cases"])

    with tab_mat:
        _render_material_inputs()
    with tab_geom:
        _render_geometry_inputs()
    with tab_load:
        _render_load_case_inputs()

    st.sidebar.divider()
    st.sidebar.header("Data Management")
    st.sidebar.button("Load JSON File", width="stretch")
    st.sidebar.button("Save JSON File", width="stretch")
    st.sidebar.button("Export Results to PDF", type="primary", width="stretch")


def _render_material_inputs():
    mats = st.session_state.data["materials"]

    with st.expander("Concrete", expanded=True):
        _seed_widget("mat_fck", mats["concrete"]["f_ck"])
        _seed_widget("mat_gamma_c", mats["concrete"]["gamma_c"])
        _seed_widget("mat_alpha_cc", mats["concrete"]["alpha_cc"])
        st.number_input("f_ck (MPa)", min_value=10.0, max_value=150.0, key="mat_fck")
        st.number_input("gamma_c", min_value=1.0, key="mat_gamma_c")
        st.number_input("alpha_cc", min_value=0.8, max_value=1.0, key="mat_alpha_cc")
        mats["concrete"]["f_ck"] = float(st.session_state.mat_fck)
        mats["concrete"]["gamma_c"] = float(st.session_state.mat_gamma_c)
        mats["concrete"]["alpha_cc"] = float(st.session_state.mat_alpha_cc)

    with st.expander("Mild Reinforcement", expanded=False):
        _seed_widget("mat_fyk", mats["mild_steel"]["f_yk"])
        _seed_widget("mat_gamma_s", mats["mild_steel"]["gamma_s"])
        _seed_widget("mat_euk", mats["mild_steel"]["e_uk"])
        _seed_widget("mat_hard", mats["mild_steel"]["include_hardening"])
        _seed_widget("mat_fuk", mats["mild_steel"].get("f_uk", mats["mild_steel"]["f_yk"]))
        st.number_input("f_yk (MPa)", min_value=200.0, key="mat_fyk")
        st.number_input("gamma_s", min_value=1.0, key="mat_gamma_s")
        st.number_input("e_uk (-)", min_value=0.01, format="%.3f", key="mat_euk")
        st.checkbox("Include Strain Hardening", key="mat_hard")
        if st.session_state.mat_hard:
            st.number_input("f_uk (MPa)", min_value=float(st.session_state.mat_fyk), key="mat_fuk")
        mats["mild_steel"]["f_yk"] = float(st.session_state.mat_fyk)
        mats["mild_steel"]["gamma_s"] = float(st.session_state.mat_gamma_s)
        mats["mild_steel"]["e_uk"] = float(st.session_state.mat_euk)
        mats["mild_steel"]["include_hardening"] = bool(st.session_state.mat_hard)
        mats["mild_steel"]["f_uk"] = float(st.session_state.mat_fuk)

    with st.expander("Prestressing Steel", expanded=False):
        _seed_widget("mat_fp01k", mats["prestressed_steel"]["f_p01k"])
        _seed_widget("mat_fpk", mats["prestressed_steel"]["f_pk"])
        _seed_widget("mat_gamma_p", mats["prestressed_steel"]["gamma_p"])
        _seed_widget("mat_initial_strain", mats["prestressed_steel"]["initial_strain"])
        _seed_widget("mat_pre_euk", mats["prestressed_steel"]["e_uk"])
        st.number_input("f_p01k (MPa)", min_value=1000.0, key="mat_fp01k")
        st.number_input("f_pk (MPa)", min_value=1000.0, key="mat_fpk")
        st.number_input("gamma_p", min_value=1.0, key="mat_gamma_p")
        st.number_input("Initial Prestrain (-)", min_value=0.0, format="%.4f", key="mat_initial_strain")
        st.number_input("e_uk (-)", min_value=0.01, format="%.3f", key="mat_pre_euk")
        mats["prestressed_steel"]["f_p01k"] = float(st.session_state.mat_fp01k)
        mats["prestressed_steel"]["f_pk"] = float(st.session_state.mat_fpk)
        mats["prestressed_steel"]["gamma_p"] = float(st.session_state.mat_gamma_p)
        mats["prestressed_steel"]["initial_strain"] = float(st.session_state.mat_initial_strain)
        mats["prestressed_steel"]["e_uk"] = float(st.session_state.mat_pre_euk)


def _render_geometry_inputs():
    data = st.session_state.data
    geom = data["geometry"]

    if "void_editor_keys" not in st.session_state:
        _rebuild_void_editor_keys_from_geometry()

    while len(st.session_state.void_editor_keys) < len(geom.get("concrete_voids", [])):
        st.session_state.void_editor_keys.append(str(uuid.uuid4()))
    if len(st.session_state.void_editor_keys) > len(geom.get("concrete_voids", [])):
        st.session_state.void_editor_keys = st.session_state.void_editor_keys[: len(geom.get("concrete_voids", []))]
    _ensure_grid_versions()

    st.write("**Concrete Outline (Clockwise)**")
    outline_grid_key = f"outline_v{st.session_state.grid_versions.get('outline', 0)}"
    geom["concrete_outline"] = edit_ordered_points(geom.get("concrete_outline", []), outline_grid_key)

    st.write("**Concrete voids (Counterclockwise)**")
    left_col, right_col = st.columns(2)

    with left_col:
        if st.button("Load example section", width="stretch"):
            data["geometry"] = load_example_geometry()
            data["geometry"] = normalize_geometry_for_use(data["geometry"])
            _rebuild_void_editor_keys_from_geometry()
            st.session_state.grid_versions = {"outline": st.session_state.get("grid_versions", {}).get("outline", 0) + 1}
            _ensure_grid_versions()
            st.rerun()

    with right_col:
        if st.button("Reset geometry", width="stretch"):
            data["geometry"] = {
                "concrete_outline": [],
                "concrete_voids": [],
                "reinforcement_mild": [],
                "reinforcement_prestressed": [],
            }
            _rebuild_void_editor_keys_from_geometry()
            st.session_state.grid_versions = {"outline": st.session_state.get("grid_versions", {}).get("outline", 0) + 1}
            st.rerun()

    if st.button("Add void", key="add_void", width="stretch"):
        geom.setdefault("concrete_voids", []).append(
            [
                {"id": 1, "x": -0.10, "y": -0.10},
                {"id": 2, "x": 0.10, "y": -0.10},
                {"id": 3, "x": 0.10, "y": 0.10},
                {"id": 4, "x": -0.10, "y": 0.10},
            ]
        )
        new_void_uuid = str(uuid.uuid4())
        st.session_state.void_editor_keys.append(new_void_uuid)
        _bump_grid_version("outline")
        _bump_grid_version(f"void_{new_void_uuid}")
        data["geometry"] = normalize_geometry_for_use(geom)
        st.rerun()

    for i, void in enumerate(geom.get("concrete_voids", [])):
        void_uuid = st.session_state.void_editor_keys[i]
        void_version = st.session_state.grid_versions.get(f"void_{void_uuid}", 0)
        void_key = f"void_{void_uuid}_v{void_version}"
        with st.expander(f"Void {i + 1}", expanded=False):
            if st.button("Remove this void", key=f"remove_void_{i}", width="stretch"):
                geom["concrete_voids"].pop(i)
                removed_uuid = st.session_state.void_editor_keys.pop(i)
                st.session_state.grid_versions.pop(f"void_{removed_uuid}", None)
                _bump_grid_version("outline")
                data["geometry"] = normalize_geometry_for_use(geom)
                st.rerun()

            geom["concrete_voids"][i] = edit_ordered_points(void, void_key)

    st.write("**Mild Steel (x, y, area mm²)**")
    df_mild = pd.DataFrame(geom.get("reinforcement_mild", []), columns=["id", "x", "y", "area"])
    edited_mild = st.data_editor(
        df_mild, num_rows="dynamic", width="stretch", key="editor_mild"
    )
    geom["reinforcement_mild"] = coerce_rebar_rows(edited_mild.to_dict("records"))

    st.write("**Prestressed Steel (x, y, area mm²)**")
    df_pre = pd.DataFrame(
        geom.get("reinforcement_prestressed", []), columns=["id", "x", "y", "area", "eps0"]
    )
    edited_pre = st.data_editor(
        df_pre, num_rows="dynamic", width="stretch", key="editor_pre"
    )
    geom["reinforcement_prestressed"] = coerce_rebar_rows(
        edited_pre.to_dict("records"), include_eps0=True
    )

    edited_geom = {
        "concrete_outline": list(geom.get("concrete_outline", [])),
        "concrete_voids": [list(v) for v in geom.get("concrete_voids", [])],
    }
    canonical_geom = normalize_geometry_for_use(geom)
    data["geometry"] = canonical_geom
    if _is_reversed(edited_geom.get("concrete_outline", []), canonical_geom.get("concrete_outline", [])):
        _bump_grid_version("outline")
        st.rerun()

    for i, void_points in enumerate(edited_geom.get("concrete_voids", [])):
        if i >= len(canonical_geom.get("concrete_voids", [])):
            continue
        if _is_reversed(void_points, canonical_geom["concrete_voids"][i]):
            void_uuid = st.session_state.void_editor_keys[i]
            _bump_grid_version(f"void_{void_uuid}")
            st.rerun()

    if canonical_geom != geom:
        reset_geometry_editor_widgets(clear_void_keys=False)
        st.rerun()

    plot_options = data["plot_options"]
    with st.expander("Plot options", expanded=False):
        for key, label in [
            ("show_concrete_point_ids", "Show concrete point IDs"),
            ("show_void_point_ids", "Show void point IDs"),
            ("show_mild_bar_ids", "Show mild bar IDs"),
            ("show_prestressed_bar_ids", "Show prestressed bar IDs"),
        ]:
            _seed_widget(key, plot_options.get(key, False))
            st.checkbox(label, key=key)
            plot_options[key] = bool(st.session_state[key])

    with st.expander("Geometry validation", expanded=True):
        topo = validate_geometry_topology(data["geometry"])
        if not topo["errors"] and not topo["warnings"]:
            st.success("No topology issues detected.")
        for error in topo["errors"]:
            st.error(error)
        for warning in topo["warnings"]:
            st.warning(warning)


def _get_next_load_case_id(load_cases):
    valid_ids = []
    for case in load_cases:
        try:
            valid_ids.append(int(case.get("id")))
        except (TypeError, ValueError):
            continue
    return (max(valid_ids) + 1) if valid_ids else 1


def _render_load_case_inputs():
    data = st.session_state.data
    mode = data["analysis_settings"]["mode"]
    data.setdefault("load_cases", {"elastic": [], "plastic": []})
    data["load_cases"].setdefault("elastic", [])
    data["load_cases"].setdefault("plastic", [])

    elastic_columns = ["id", "name", "P_l", "Mx_l", "My_l", "n_l", "P_s", "Mx_s", "My_s", "n_s"]
    plastic_columns = ["id", "name", "P_target", "v_min", "v_max", "v_inc"]

    if mode in ["Elastic", "Both"]:
        st.write("**Elastic load cases**")
        df_elastic = pd.DataFrame(data["load_cases"].get("elastic", []), columns=elastic_columns)
        edited_elastic = st.data_editor(
            df_elastic,
            num_rows="dynamic",
            width="stretch",
            key="editor_load_cases_elastic",
        )
        data["load_cases"]["elastic"] = edited_elastic.to_dict("records")

        add_col, rm_col = st.columns(2)
        with add_col:
            if st.button("Add elastic load case", key="add_elastic_case", width="stretch"):
                next_id = _get_next_load_case_id(data["load_cases"]["elastic"])
                data["load_cases"]["elastic"].append(
                    {
                        "id": next_id,
                        "name": f"Load case {next_id}",
                        "P_l": 0.0,
                        "Mx_l": 0.0,
                        "My_l": 0.0,
                        "n_l": 1.0,
                        "P_s": 0.0,
                        "Mx_s": 0.0,
                        "My_s": 0.0,
                        "n_s": 1.0,
                    }
                )
                reset_load_case_editor_widgets()
                st.rerun()
        with rm_col:
            if st.button("Remove last elastic load case", key="remove_elastic_case", width="stretch"):
                if data["load_cases"]["elastic"]:
                    data["load_cases"]["elastic"].pop()
                    reset_load_case_editor_widgets()
                    st.rerun()

    if mode in ["Plastic", "Both"]:
        st.write("**Plastic load cases**")
        df_plastic = pd.DataFrame(data["load_cases"].get("plastic", []), columns=plastic_columns)
        edited_plastic = st.data_editor(
            df_plastic,
            num_rows="dynamic",
            width="stretch",
            key="editor_load_cases_plastic",
        )
        data["load_cases"]["plastic"] = edited_plastic.to_dict("records")

        add_col, rm_col = st.columns(2)
        with add_col:
            if st.button("Add plastic load case", key="add_plastic_case", width="stretch"):
                next_id = _get_next_load_case_id(data["load_cases"]["plastic"])
                data["load_cases"]["plastic"].append(
                    {
                        "id": next_id,
                        "name": f"Load case {next_id}",
                        "P_target": 0.0,
                        "v_min": 0.0,
                        "v_max": 360.0,
                        "v_inc": 10.0,
                    }
                )
                reset_load_case_editor_widgets()
                st.rerun()
        with rm_col:
            if st.button("Remove last plastic load case", key="remove_plastic_case", width="stretch"):
                if data["load_cases"]["plastic"]:
                    data["load_cases"]["plastic"].pop()
                    reset_load_case_editor_widgets()
                    st.rerun()
