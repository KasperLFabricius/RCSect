import streamlit as st
import pandas as pd
import uuid
from utils.data_io import (
    initialize_session_state,
    validate_geometry_topology,
    validate_winding_constraints,
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
    tab_mat, tab_geom = st.sidebar.tabs(["Materials", "Geometry Input"])
    
    with tab_mat:
        _render_material_inputs()
        
    with tab_geom:
        _render_geometry_inputs()

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

    with st.expander("Geometry validation", expanded=True):
        topo = validate_geometry_topology(st.session_state.data["geometry"])
        if not topo["errors"] and not topo["warnings"]:
            st.success("No topology issues detected.")
        for error in topo["errors"]:
            st.error(error)
        for warning in topo["warnings"]:
            st.warning(warning)

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
