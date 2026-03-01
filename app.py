import streamlit as st
import numpy as np

# Import all modular components we built
from utils.data_io import initialize_session_state, handle_autosave
from ui.sidebar import render_sidebar
from ui.canvas import render_geometry_plot
from ui.results import render_elastic_results, render_plastic_results

from core.materials import Concrete, MildSteel, PrestressedSteel
from core.geometry import CrossSection
from core.solver_elastic import ElasticSolver
from core.solver_plastic import PlasticSolver

def build_computational_models(data):
    """
    Translates the JSON session state into the active Python class instances 
    required by the analytical engines.
    """
    # 1. Instantiate Materials
    mat_c = data["materials"]["concrete"]
    concrete = Concrete(
        f_ck=mat_c["f_ck"], 
        gamma_c=mat_c["gamma_c"], 
        alpha_cc=mat_c["alpha_cc"]
    )
    
    mat_s = data["materials"]["mild_steel"]
    mild_steel = MildSteel(
        f_yk=mat_s["f_yk"], 
        gamma_s=mat_s["gamma_s"], 
        e_uk=mat_s["e_uk"],
        f_uk=mat_s.get("f_uk", None),
        include_hardening=mat_s.get("include_hardening", False)
    )
    
    mat_p = data["materials"]["prestressed_steel"]
    prestressed_steel = None
    if data["geometry"].get("reinforcement_prestressed"):
        prestressed_steel = PrestressedSteel(
            f_p01k=mat_p["f_p01k"], 
            f_pk=mat_p["f_pk"], 
            initial_strain=mat_p["initial_strain"],
            e_uk=mat_p["e_uk"],
            gamma_s=mat_p["gamma_p"]
        )

    # 2. Instantiate Geometry
    cross_section = CrossSection(
        concrete_outline=data["geometry"].get("concrete_outline", []),
        concrete_voids=data["geometry"].get("concrete_voids", []),
        rebar_mild=data["geometry"].get("reinforcement_mild", []),
        rebar_prestressed=data["geometry"].get("reinforcement_prestressed", [])
    )
    
    return cross_section, concrete, mild_steel, prestressed_steel

def main():
    st.set_page_config(
        page_title="RCSect",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("RCSect: Reinforced Concrete Section Analysis")

    # 1. Initialize State and Sidebar
    initialize_session_state()
    render_sidebar()
    
    data = st.session_state.data
    mode = data["analysis_settings"]["mode"]

    # 2. Layout
    col_canvas, col_results = st.columns([5, 7])

    with col_canvas:
        st.subheader("Cross-Section Geometry")
        render_geometry_plot()
        
    with col_results:
        st.subheader("Analysis Results")
        
        # Verify geometry exists before attempting to solve
        if not data["geometry"].get("concrete_outline"):
            st.warning("Please define the concrete geometry to run the analysis.")
            return
            
        # Build core engine instances
        cs, conc, mild, pre = build_computational_models(data)

        # 3. Execution: Elastic Mode
        if mode in ["Elastic", "Both"]:
            st.write("### Elastic Analysis")
            # For demonstration, we use placeholder loads. In the final version,
            # these will be extracted from data["load_cases"]
            elastic_engine = ElasticSolver(cross_section=cs, E_c=33000.0, E_s=200000.0)
            
            try:
                # Utilizing the exact 4-step combination algorithm
                el_results = elastic_engine.solve_combined_loads(
                    P_l=408.98, Mx_l=-49.87, My_l=0.0, n_l=22.93,
                    P_s=-5.45, Mx_s=-36.12, My_s=0.0, n_s=5.733
                )
                render_elastic_results(el_results)
            except Exception as e:
                st.error(f"Elastic Solver Error: {e}")

        st.divider()

        # 4. Execution: Plastic Mode (The Angular Sweep)
        if mode in ["Plastic", "Both"]:
            st.write("### Plastic Analysis")
            plastic_engine = PlasticSolver(cs, conc, mild, pre)
            
            # Using placeholder load case parameters as defined in the documentation
            target_P = 1976.0  
            v_min = 0.0        
            v_max = 360.0      
            v_inc = 10.0       

            try:
                plastic_sweep_results = []
                # Execute the iteration sweep
                current_v = v_min
                while current_v <= v_max:
                    res = plastic_engine.solve(angle_v_deg=current_v, P_target=target_P)
                    # Append the specific angle to the result dictionary
                    res["V"] = current_v
                    plastic_sweep_results.append(res)
                    current_v += v_inc
                
                # Pass the aggregated list of dictionaries to the rendering module
                render_plastic_results(plastic_sweep_results, target_P)
                
            except Exception as e:
                st.error(f"Plastic Solver Error: {e}")

    # 5. Background Task
    handle_autosave()

if __name__ == "__main__":
    main()