import hashlib
import json

import streamlit as st

from utils.data_io import handle_autosave, initialize_session_state
from ui.canvas import render_geometry_plot
from ui.results import (
    render_elastic_export,
    render_elastic_results,
    render_geometry_exports,
    render_plastic_export,
    render_plastic_results,
)
from ui.sidebar import RUN_BUTTON_PRESSED_KEY, render_sidebar

from core.geometry import CrossSection
from core.materials import Concrete, MildSteel, PrestressedSteel
from core.solver_elastic import ElasticSolver
from core.solver_plastic import PlasticSolver
from utils.units import gpa_to_mpa


def build_computational_models(data):
    mat_c = data["materials"]["concrete"]
    concrete = Concrete(f_ck=mat_c["f_ck"], gamma_c=mat_c["gamma_c"], alpha_cc=mat_c["alpha_cc"])

    mat_s = data["materials"]["mild_steel"]
    mild_steel = MildSteel(
        f_yk=mat_s["f_yk"],
        gamma_s=mat_s["gamma_s"],
        E_s=gpa_to_mpa(mat_s.get("E_s_GPa", 200.0)),
        e_uk=mat_s["e_uk"],
        f_uk=mat_s.get("f_uk", None),
        include_hardening=mat_s.get("include_hardening", False),
    )

    mat_p = data["materials"]["prestressed_steel"]
    prestressed_steel = None
    if data["geometry"].get("reinforcement_prestressed"):
        prestressed_steel = PrestressedSteel(
            f_p01k=mat_p["f_p01k"],
            f_pk=mat_p["f_pk"],
            initial_strain=mat_p["initial_strain"],
            e_uk=mat_p["e_uk"],
            gamma_s=mat_p["gamma_p"],
            E_p=gpa_to_mpa(mat_p.get("E_p_GPa", 195.0)),
        )

    cross_section = CrossSection(
        concrete_outline=data["geometry"].get("concrete_outline", []),
        concrete_voids=data["geometry"].get("concrete_voids", []),
        rebar_mild=data["geometry"].get("reinforcement_mild", []),
        rebar_prestressed=data["geometry"].get("reinforcement_prestressed", []),
    )

    return cross_section, concrete, mild_steel, prestressed_steel


def _compute_results(data: dict):
    mode = data["analysis_settings"]["mode"]
    can_run_analysis = bool(data["geometry"].get("concrete_outline"))
    if not can_run_analysis:
        return {"can_run": False, "elastic": [], "plastic": []}

    cs, conc, mild, pre = build_computational_models(data)
    computed = {"can_run": True, "elastic": [], "plastic": []}

    if mode in ["Elastic", "Both"]:
        mat_c = data["materials"]["concrete"]
        mat_s = data["materials"]["mild_steel"]
        elastic_engine = ElasticSolver(
            cross_section=cs,
            E_c=gpa_to_mpa(mat_c.get("E_c_GPa", 33.0)),
            E_s=gpa_to_mpa(mat_s.get("E_s_GPa", 200.0)),
        )
        for case in data.get("load_cases", {}).get("elastic", []):
            case_name = case.get("name", "Unnamed")
            try:
                el_results = elastic_engine.solve_combined_loads(
                    P_l=case.get("P_l", 0.0),
                    Mx_l=case.get("Mx_l", 0.0),
                    My_l=case.get("My_l", 0.0),
                    n_l=case.get("n_l", 1.0),
                    P_s=case.get("P_s", 0.0),
                    Mx_s=case.get("Mx_s", 0.0),
                    My_s=case.get("My_s", 0.0),
                    n_s=case.get("n_s", 1.0),
                )
                computed["elastic"].append({"case": case, "case_name": case_name, "result": el_results})
            except Exception as exc:
                computed["elastic"].append({"case": case, "case_name": case_name, "error": str(exc)})

    if mode in ["Plastic", "Both"]:
        plastic_engine = PlasticSolver(cs, conc, mild, pre)
        for case in data.get("load_cases", {}).get("plastic", []):
            case_name = case.get("name", "Unnamed")
            v_inc = case.get("v_inc", 0.0)
            v_min = case.get("v_min", 0.0)
            v_max = case.get("v_max", 0.0)
            target_p = case.get("P_target", 0.0)
            if v_inc <= 0:
                computed["plastic"].append({"case": case, "case_name": case_name, "error": "Invalid load case: v_inc must be greater than 0."})
                continue
            if v_max < v_min:
                computed["plastic"].append({"case": case, "case_name": case_name, "error": "Invalid load case: v_max must be greater than or equal to v_min."})
                continue

            try:
                plastic_sweep_results = []
                current_v = v_min
                while current_v <= v_max:
                    res = plastic_engine.solve(angle_v_deg=current_v, P_target=target_p)
                    res["V"] = current_v
                    plastic_sweep_results.append(res)
                    current_v += v_inc
                computed["plastic"].append({"case": case, "case_name": case_name, "result": plastic_sweep_results, "target_P": target_p})
            except Exception as exc:
                computed["plastic"].append({"case": case, "case_name": case_name, "error": str(exc)})

    return computed


def _input_hash(data: dict) -> str:
    analysis_settings = dict(data.get("analysis_settings", {}))
    analysis_settings.pop("auto_run", None)
    payload = {
        "analysis_settings": analysis_settings,
        "materials": data.get("materials", {}),
        "geometry": data.get("geometry", {}),
        "load_cases": data.get("load_cases", {}),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def main():
    st.set_page_config(page_title="RCSect", page_icon="🏗", layout="wide", initial_sidebar_state="expanded")
    st.title("RCSect: Reinforced Concrete Section Analysis")

    initialize_session_state()
    render_sidebar()

    data = st.session_state.data
    current_hash = _input_hash(data)
    st.session_state["current_input_hash"] = current_hash
    mode = data["analysis_settings"]["mode"]
    auto_run = bool(data["analysis_settings"].get("auto_run", True))

    col_canvas, col_results = st.columns([5, 7])

    with col_canvas:
        st.subheader("Cross-Section Geometry")
        canvas_container = st.container()

    with col_results:
        st.subheader("Analysis Results")
        render_geometry_exports(data.get("geometry", {}))

        can_run_analysis = bool(data["geometry"].get("concrete_outline"))
        if not can_run_analysis:
            st.warning("Please define the concrete geometry to run the analysis.")

        cached = st.session_state.get("last_results_cache", {})

        should_compute = auto_run and can_run_analysis
        if not auto_run and can_run_analysis:
            should_compute = st.button("Run analysis", key=RUN_BUTTON_PRESSED_KEY)

        if should_compute:
            computed = _compute_results(data)
            st.session_state["last_results_cache"] = {"hash": current_hash, "results": computed}
            cached = st.session_state["last_results_cache"]

        results = cached.get("results") if cached.get("hash") == current_hash else None

        if results and mode in ["Elastic", "Both"]:
            st.write("### Elastic Analysis")
            if not results["elastic"]:
                st.info("No elastic load cases configured.")
            for item in results["elastic"]:
                case = item["case"]
                case_id = case.get("id", "?")
                with st.expander(f"Elastic load case {case_id}: {item['case_name']}", expanded=False):
                    if item.get("error"):
                        st.error(f"Elastic Solver Error: {item['error']}")
                    else:
                        render_elastic_results(item["result"])
                        render_elastic_export(item["case_name"], item["result"])

        st.divider()

        if results and mode in ["Plastic", "Both"]:
            st.write("### Plastic Analysis")
            if not results["plastic"]:
                st.info("No plastic load cases configured.")
            for item in results["plastic"]:
                case = item["case"]
                case_id = case.get("id", "?")
                with st.expander(f"Plastic load case {case_id}: {item['case_name']}", expanded=False):
                    if item.get("error"):
                        st.error(f"Plastic Solver Error: {item['error']}")
                    else:
                        render_plastic_results(item["result"], item["target_P"])
                        render_plastic_export(item["case_name"], item["result"])
        elif not auto_run and can_run_analysis and cached.get("hash") != current_hash:
            st.info("Analysis inputs changed. Click 'Run analysis' to refresh results.")


    with canvas_container:
        render_geometry_plot()

    handle_autosave()


if __name__ == "__main__":
    main()
