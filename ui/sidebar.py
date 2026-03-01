import streamlit as st
import pandas as pd
import uuid
from utils.data_io import (
    initialize_session_state,
    validate_winding_constraints,
    validate_geometry_topology,
)

def render_sidebar():
    """Renders the sidebar interface for global settings, materials, and geometry."""
    initialize_session_state()
    
    st.sidebar.header("Global Settings")
    
    # Analysis Mode Selection
    st.session_state.data["analysis_settings"]["mode"] = st.sidebar.radio(
        "Analysis Mode",
        options=["Elastic", "Plastic", "Both"],
        index=["Elastic", "Plastic", "Both"].index(st.session_state.data["analysis_settings"]["mode"]),
        help="Select the type of analysis to perform."
    )
    
    st.sidebar.divider()
    
    # Create Tabs for Organization
    tab_mat, tab_geom, tab_load = st.sidebar.tabs(
        ["Materials", "Geometry Input", "Load Cases"]
    )
    
    with tab_mat:
        _render_material_inputs()
        
    with tab_geom:
        _render_geometry_inputs()

    with tab_load:
        _render_load_case_inputs()

    st.sidebar.divider()
    
    # File I/O Placeholders
    st.sidebar.header("Data Management")
    st.sidebar.button("Load JSON File", use_container_width=True)
    st.sidebar.button("Save JSON File", use_container_width=True)
    st.sidebar.button("Export Results to PDF", type="primary", use_container_width=True)


def _render_material_inputs():
    """Helper function to render the material expanders."""
    mats = st.session_state.data["materials"]
    
    with st.expander("Concrete", expanded=True):
        mats["concrete"]["f_ck"] = st.number_input("f_ck (MPa)", min_value=10.0, max_value=150.0, value=mats["concrete"]["f_ck"])
        mats["concrete"]["gamma_c"] = st.number_input("gamma_c", min_value=1.0, value=mats["concrete"]["gamma_c"])
        mats["concrete"]["alpha_cc"] = st.number_input("alpha_cc", min_value=0.8, max_value=1.0, value=mats["concrete"]["alpha_cc"])

    with st.expander("Mild Reinforcement", expanded=False):
        mats["mild_steel"]["f_yk"] = st.number_input("f_yk (MPa)", min_value=200.0, value=mats["mild_steel"]["f_yk"])
        mats["mild_steel"]["gamma_s"] = st.number_input("gamma_s", min_value=1.0, value=mats["mild_steel"]["gamma_s"])
        mats["mild_steel"]["e_uk"] = st.number_input("e_uk (-)", min_value=0.01, value=mats["mild_steel"]["e_uk"], format="%.3f")
        mats["mild_steel"]["include_hardening"] = st.checkbox("Include Strain Hardening", value=mats["mild_steel"]["include_hardening"])
        if mats["mild_steel"]["include_hardening"]:
            mats["mild_steel"]["f_uk"] = st.number_input("f_uk (MPa)", min_value=mats["mild_steel"]["f_yk"], value=mats["mild_steel"]["f_uk"])

    with st.expander("Prestressing Steel", expanded=False):
        mats["prestressed_steel"]["f_p01k"] = st.number_input("f_p01k (MPa)", min_value=1000.0, value=mats["prestressed_steel"]["f_p01k"])
        mats["prestressed_steel"]["f_pk"] = st.number_input("f_pk (MPa)", min_value=1000.0, value=mats["prestressed_steel"]["f_pk"])
        mats["prestressed_steel"]["gamma_p"] = st.number_input("gamma_p", min_value=1.0, value=mats["prestressed_steel"]["gamma_p"])
        mats["prestressed_steel"]["initial_strain"] = st.number_input("Initial Prestrain (-)", min_value=0.0, value=mats["prestressed_steel"]["initial_strain"], format="%.4f")
        mats["prestressed_steel"]["e_uk"] = st.number_input("e_uk (-)", min_value=0.01, value=mats["prestressed_steel"]["e_uk"], format="%.3f")


def _render_geometry_inputs():
    """Helper function to render the interactive data editors for coordinates."""
    geom = st.session_state.data["geometry"]
    if "concrete_voids" not in geom:
        geom["concrete_voids"] = []

    if "void_editor_keys" not in st.session_state:
        st.session_state.void_editor_keys = []

    void_editor_keys = st.session_state.void_editor_keys
    void_count = len(geom["concrete_voids"])
    if len(void_editor_keys) < void_count:
        void_editor_keys.extend(
            str(uuid.uuid4()) for _ in range(void_count - len(void_editor_keys))
        )
    elif len(void_editor_keys) > void_count:
        del void_editor_keys[void_count:]
    
    st.write("**Concrete Outline (Clockwise)**")
    df_outline = pd.DataFrame(geom.get("concrete_outline", [{"x": 0.0, "y": 0.0}]))
    edited_outline = st.data_editor(
        df_outline, 
        num_rows="dynamic", 
        use_container_width=True,
        key="editor_outline"
    )
    geom["concrete_outline"] = edited_outline.to_dict('records')
    st.session_state.data["geometry"] = validate_winding_constraints(
        st.session_state.data["geometry"]
    )

    st.write("**Concrete voids (Counterclockwise)**")
    st.caption("Orientation will be auto-normalized.")

    if st.button("Add void", key="add_void", use_container_width=True):
        geom["concrete_voids"].append(
            [
                {"x": -0.10, "y": -0.10},
                {"x": 0.10, "y": -0.10},
                {"x": 0.10, "y": 0.10},
                {"x": -0.10, "y": 0.10},
            ]
        )
        void_editor_keys.append(str(uuid.uuid4()))
        st.session_state.data["geometry"] = validate_winding_constraints(
            st.session_state.data["geometry"]
        )

    for i, void in enumerate(geom["concrete_voids"]):
        with st.expander(f"Void {i+1}", expanded=False):
            if st.button(
                "Remove this void",
                key=f"remove_void_{i}",
                use_container_width=True,
            ):
                geom["concrete_voids"].pop(i)
                void_editor_keys.pop(i)
                st.session_state.data["geometry"] = validate_winding_constraints(
                    st.session_state.data["geometry"]
                )
                st.rerun()

            df_void = pd.DataFrame(void if void else [{"x": 0.0, "y": 0.0}])
            edited_void = st.data_editor(
                df_void,
                num_rows="dynamic",
                use_container_width=True,
                key=f"editor_void_{void_editor_keys[i]}",
            )
            geom["concrete_voids"][i] = edited_void.to_dict("records")
            st.session_state.data["geometry"] = validate_winding_constraints(
                st.session_state.data["geometry"]
            )

    st.write("**Mild Steel (x, y, area mm²)**")
    df_mild = pd.DataFrame(geom.get("reinforcement_mild", [{"id": 1, "x": 0.0, "y": 0.0, "area": 0.0}]))
    edited_mild = st.data_editor(
        df_mild, 
        num_rows="dynamic", 
        use_container_width=True,
        key="editor_mild"
    )
    geom["reinforcement_mild"] = edited_mild.to_dict('records')

    st.write("**Prestressed Steel (x, y, area mm²)**")
    df_pre = pd.DataFrame(geom.get("reinforcement_prestressed", [{"id": 1, "x": 0.0, "y": 0.0, "area": 0.0}]))
    edited_pre = st.data_editor(
        df_pre, 
        num_rows="dynamic", 
        use_container_width=True,
        key="editor_pre"
    )
    geom["reinforcement_prestressed"] = edited_pre.to_dict('records')

    with st.expander("Geometry validation", expanded=True):
        topo = validate_geometry_topology(st.session_state.data["geometry"])
        if not topo["errors"] and not topo["warnings"]:
            st.success("No topology issues detected.")
        for error in topo["errors"]:
            st.error(error)
        for warning in topo["warnings"]:
            st.warning(warning)


def _get_next_load_case_id(load_cases):
    """Returns max valid integer id + 1; falls back to 1 when none exist."""
    valid_ids = []
    for case in load_cases:
        try:
            case_id = int(case.get("id"))
            valid_ids.append(case_id)
        except (TypeError, ValueError):
            continue

    return (max(valid_ids) + 1) if valid_ids else 1


def _render_load_case_inputs():
    """Renders editable elastic/plastic load case tables."""
    data = st.session_state.data
    mode = data["analysis_settings"]["mode"]

    if "load_cases" not in data or not isinstance(data["load_cases"], dict):
        data["load_cases"] = {"elastic": [], "plastic": []}

    data["load_cases"].setdefault("elastic", [])
    data["load_cases"].setdefault("plastic", [])

    elastic_columns = ["id", "name", "P_l", "Mx_l", "My_l", "n_l", "P_s", "Mx_s", "My_s", "n_s"]
    plastic_columns = ["id", "name", "P_target", "v_min", "v_max", "v_inc"]

    if mode in ["Elastic", "Both"]:
        st.write("**Elastic load cases**")
        elastic_cases = data["load_cases"]["elastic"]
        df_elastic = (
            pd.DataFrame(elastic_cases)
            if elastic_cases
            else pd.DataFrame(columns=elastic_columns)
        )
        edited_elastic = st.data_editor(
            df_elastic,
            num_rows="dynamic",
            use_container_width=True,
            key="editor_load_cases_elastic",
        )
        data["load_cases"]["elastic"] = edited_elastic.to_dict("records")

        add_elastic_col, remove_elastic_col = st.columns(2)
        with add_elastic_col:
            if st.button("Add elastic load case", key="add_elastic_case", use_container_width=True):
                elastic_cases = data["load_cases"]["elastic"]
                next_id = _get_next_load_case_id(elastic_cases)
                elastic_cases.append(
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
                st.rerun()
        with remove_elastic_col:
            if st.button("Remove last elastic load case", key="remove_elastic_case", use_container_width=True):
                elastic_cases = data["load_cases"]["elastic"]
                if elastic_cases:
                    elastic_cases.pop()
                    st.rerun()

    if mode in ["Plastic", "Both"]:
        st.write("**Plastic load cases**")
        plastic_cases = data["load_cases"]["plastic"]
        df_plastic = (
            pd.DataFrame(plastic_cases)
            if plastic_cases
            else pd.DataFrame(columns=plastic_columns)
        )
        edited_plastic = st.data_editor(
            df_plastic,
            num_rows="dynamic",
            use_container_width=True,
            key="editor_load_cases_plastic",
        )
        data["load_cases"]["plastic"] = edited_plastic.to_dict("records")

        add_plastic_col, remove_plastic_col = st.columns(2)
        with add_plastic_col:
            if st.button("Add plastic load case", key="add_plastic_case", use_container_width=True):
                plastic_cases = data["load_cases"]["plastic"]
                next_id = _get_next_load_case_id(plastic_cases)
                plastic_cases.append(
                    {
                        "id": next_id,
                        "name": f"Load case {next_id}",
                        "P_target": 0.0,
                        "v_min": 0.0,
                        "v_max": 360.0,
                        "v_inc": 10.0,
                    }
                )
                st.rerun()
        with remove_plastic_col:
            if st.button("Remove last plastic load case", key="remove_plastic_case", use_container_width=True):
                plastic_cases = data["load_cases"]["plastic"]
                if plastic_cases:
                    plastic_cases.pop()
                    st.rerun()
