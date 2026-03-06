import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import numpy as np

from utils.units import kn_m2_to_mpa


def _to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")



def _normalize_case_name(case_name) -> tuple[str, str]:
    if isinstance(case_name, str):
        display_name = case_name.strip()
    elif case_name is None:
        display_name = ""
    else:
        display_name = str(case_name).strip()

    if not display_name:
        display_name = "Unnamed case"

    slug = "".join(ch.lower() if ch.isalnum() else "_" for ch in display_name)
    slug = "_".join(part for part in slug.split("_") if part)
    if not slug:
        slug = "unnamed_case"

    return display_name, slug

def prepare_plastic_results_dataframe(plastic_output: list, target_P: float | None = None) -> pd.DataFrame:
    """Normalize plastic solver output for display/export tables."""
    df_plastic = pd.DataFrame(plastic_output or [])
    if df_plastic.empty:
        return df_plastic

    for col in [
        "Mx",
        "My",
        "V",
        "y_na",
        "kappa",
        "na_intersect_x",
        "na_intersect_y",
        "strain_concrete",
        "strain_mild",
        "strain_prestressed",
        "compress_force",
        "lever_L",
        "lever_DX",
        "lever_DY",
        "warning",
        "pivot",
    ]:
        if col not in df_plastic.columns:
            df_plastic[col] = None

    denom = target_P if target_P not in (None, 0) else np.nan
    df_plastic["R (m)"] = np.sqrt(df_plastic["Mx"] ** 2 + df_plastic["My"] ** 2) / denom
    df_plastic["U (deg)"] = np.degrees(np.arctan2(df_plastic["Mx"], df_plastic["My"]))

    export_rename = {
        "Mx": "Mx_kNm",
        "My": "My_kNm",
        "V": "V_deg",
        "y_na": "y_na_m",
        "kappa": "kappa_1_per_m",
        "na_intersect_x": "na_intersect_x_m",
        "na_intersect_y": "na_intersect_y_m",
        "strain_concrete": "strain_concrete_permille",
        "strain_mild": "strain_mild_permille",
        "strain_prestressed": "strain_prestressed_permille",
        "compress_force": "compress_force_kN",
        "lever_L": "lever_L_m",
        "lever_DX": "lever_DX_m",
        "lever_DY": "lever_DY_m",
    }
    df_export = df_plastic.rename(columns=export_rename)
    ordered_cols = [
        "Mx_kNm",
        "My_kNm",
        "V_deg",
        "y_na_m",
        "kappa_1_per_m",
        "na_intersect_x_m",
        "na_intersect_y_m",
        "strain_concrete_permille",
        "strain_mild_permille",
        "strain_prestressed_permille",
        "compress_force_kN",
        "lever_L_m",
        "lever_DX_m",
        "lever_DY_m",
        "warning",
        "pivot",
    ]
    for col in ordered_cols:
        if col not in df_export.columns:
            df_export[col] = None
    df_plastic.attrs["export_df"] = df_export[ordered_cols].copy()
    return df_plastic


def render_geometry_exports(geometry: dict):
    st.markdown("#### Exports")
    outline_df = pd.DataFrame(geometry.get("concrete_outline", []), columns=["id", "x_m", "y_m"])
    st.download_button(
        "Download outline points CSV",
        data=_to_csv_bytes(outline_df),
        file_name="geometry_outline_points.csv",
        mime="text/csv",
    )

    void_rows = []
    for i, void in enumerate(geometry.get("concrete_voids", []), start=1):
        for pt in void:
            void_rows.append({"void_index": i, "id": pt.get("id"), "x_m": pt.get("x"), "y_m": pt.get("y")})
    void_df = pd.DataFrame(void_rows, columns=["void_index", "id", "x_m", "y_m"])
    st.download_button(
        "Download void points CSV",
        data=_to_csv_bytes(void_df),
        file_name="geometry_void_points.csv",
        mime="text/csv",
    )

    mild_rows = [{"type": "mild", **bar} for bar in geometry.get("reinforcement_mild", [])]
    pre_rows = []
    for bar in geometry.get("reinforcement_prestressed", []):
        row = {"type": "prestress", **bar}
        eps0_strain = row.get("eps0")
        if eps0_strain is not None:
            row["eps0_strain"] = eps0_strain
            row["eps0_permille"] = 1000.0 * eps0_strain
        pre_rows.append(row)

    rebar_df = pd.DataFrame(mild_rows + pre_rows)
    if "x" in rebar_df.columns:
        rebar_df = rebar_df.rename(columns={"x": "x_m", "y": "y_m", "area": "A_mm2"})
    st.download_button(
        "Download reinforcement CSV",
        data=_to_csv_bytes(rebar_df),
        file_name="geometry_rebar.csv",
        mime="text/csv",
    )


def render_elastic_results(elastic_output: dict):
    def _fmt_na_intercept(value):
        if value is None:
            return "N/A"
        try:
            value = float(value)
        except (TypeError, ValueError):
            return "N/A"
        if not np.isfinite(value):
            return "N/A"
        return f"{value:.4f}"

    max_c_mpa = kn_m2_to_mpa(elastic_output.get("max_concrete", 0.0))
    max_tension = 0.0
    if elastic_output.get("RST_total"):
        max_tension = max(list(elastic_output["RST_total"].values()) + [0.0])
    max_tension_mpa = kn_m2_to_mpa(max_tension)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(r"$\sigma_{c,\max}\ [\mathrm{MPa}]$")
        st.metric(label="sigma_c_max", value=f"{max_c_mpa:.3f}", label_visibility="collapsed")
    with col2:
        st.markdown(r"$\sigma_{s,\max,\mathrm{TOTAL}}\ [\mathrm{MPa}]$")
        st.metric(label="sigma_s_max_total", value=f"{max_tension_mpa:.3f}", label_visibility="collapsed")

    st.markdown("#### Individual bar stresses")
    table_data = []
    bar_ids = elastic_output.get("RST_total", {}).keys()

    for b_id in bar_ids:
        table_data.append(
            {
                "Bar": b_id,
                "σ_s,total [MPa]": kn_m2_to_mpa(elastic_output["RST_total"].get(b_id, 0.0)),
                "σ_s,long [MPa]": kn_m2_to_mpa(elastic_output["LONG_s1"].get(b_id, 0.0)),
                "σ_s,dif [MPa]": kn_m2_to_mpa(elastic_output["DIF"].get(b_id, 0.0)),
                "σ_s,rst1 [MPa]": kn_m2_to_mpa(elastic_output["RST1_s3"].get(b_id, 0.0)),
            }
        )

    if table_data:
        df_elastic = pd.DataFrame(table_data)
        st.dataframe(df_elastic.style.format(precision=3), width="stretch")
    else:
        st.info("No reinforcement data available.")

    st.markdown("#### Neutral-axis intersections [m]")
    na_rows = []
    for state_key, label in (("na_LONG", "LONG"), ("na_RST1", "RST1")):
        na_data = elastic_output.get(state_key, {}) or {}
        na_rows.append(
            {
                "State": label,
                "x-intercept [m]": _fmt_na_intercept(na_data.get("x_intercept")),
                "y-intercept [m]": _fmt_na_intercept(na_data.get("y_intercept")),
            }
        )
    st.dataframe(pd.DataFrame(na_rows), width="stretch", hide_index=True)


def render_elastic_export(case_name: str, elastic_output: dict, data: dict | None = None):
    safe_label, safe_slug = _normalize_case_name(case_name)
    rows = []
    settings = (data or {}).get("analysis_settings", {})
    mild = ((data or {}).get("materials", {})).get("mild_steel", {})
    rows.extend(
        [
            {"metric": "meta", "item": "gamma_E", "value": settings.get("gamma_E", 1.0)},
            {"metric": "meta", "item": "gamma_u", "value": settings.get("gamma_u", 1.0)},
            {"metric": "meta", "item": "f_yk_t_MPa", "value": mild.get("f_yk_t_MPa", mild.get("f_yk", 500.0))},
            {"metric": "meta", "item": "f_yk_c_MPa", "value": mild.get("f_yk_c_MPa", mild.get("f_yk", 500.0))},
        ]
    )
    max_c = kn_m2_to_mpa(elastic_output.get("max_concrete", 0.0))
    rows.append({"metric": "sigma_c_max_MPa", "item": "", "value": max_c})

    na_long = elastic_output.get("na_LONG", {}) or {}
    na_rst1 = elastic_output.get("na_RST1", {}) or {}
    rows.extend(
        [
            {"metric": "na_intersection", "item": "long_x_intercept_m", "value": na_long.get("x_intercept")},
            {"metric": "na_intersection", "item": "long_y_intercept_m", "value": na_long.get("y_intercept")},
            {"metric": "na_intersection", "item": "rst1_x_intercept_m", "value": na_rst1.get("x_intercept")},
            {"metric": "na_intersection", "item": "rst1_y_intercept_m", "value": na_rst1.get("y_intercept")},
        ]
    )

    for key, value in elastic_output.items():
        if key in {"max_concrete", "na_LONG", "na_RST1"}:
            continue
        if isinstance(value, dict):
            for sub_key, sub_val in value.items():
                metric = key
                if key in {"RST_total", "LONG_s1", "DIF", "RST1_s3"}:
                    metric = f"{key}_MPa"
                    sub_val = kn_m2_to_mpa(sub_val)
                rows.append({"metric": metric, "item": sub_key, "value": sub_val})
        elif isinstance(value, (list, tuple)):
            for idx, item in enumerate(value):
                rows.append({"metric": key, "item": idx, "value": item})
        else:
            rows.append({"metric": key, "item": "", "value": value})
    df = pd.DataFrame(rows, columns=["metric", "item", "value"])
    st.download_button(
        f"Download elastic CSV: {safe_label}",
        data=_to_csv_bytes(df),
        file_name=f"elastic_{safe_slug}.csv",
        mime="text/csv",
    )


def render_plastic_results(plastic_output: list, target_P: float):
    if not plastic_output:
        st.warning("No plastic calculation data generated.")
        return

    df_plastic = prepare_plastic_results_dataframe(plastic_output, target_P=target_P)
    display_cols = [
        c
        for c in [
            "U (deg)",
            "R (m)",
            "Mx",
            "My",
            "V",
            "y_na",
            "kappa",
            "na_intersect_x",
            "na_intersect_y",
            "strain_concrete",
            "strain_mild",
            "strain_prestressed",
            "compress_force",
            "lever_L",
            "lever_DX",
            "lever_DY",
            "warning",
            "pivot",
        ]
        if c in df_plastic.columns
    ]
    df_display = df_plastic[display_cols].copy()

    df_display.rename(
        columns={
            "Mx": "Mx [kNm]",
            "My": "My [kNm]",
            "V": "V [deg]",
            "y_na": "Depth y_na [m]",
            "kappa": "Curvature [1/m]",
            "na_intersect_x": "NA x-intercept [m]",
            "na_intersect_y": "NA y-intercept [m]",
            "strain_concrete": "ε_c [‰]",
            "strain_mild": "ε_s [‰]",
            "strain_prestressed": "ε_p [‰]",
            "compress_force": "Compression force [kN]",
            "lever_L": "Lever arm L [m]",
            "lever_DX": "Lever arm DX [m]",
            "lever_DY": "Lever arm DY [m]",
            "warning": "Warning",
            "pivot": "Failure pivot",
        },
        inplace=True,
    )

    st.markdown("#### Biaxial capacity envelope ($M_x$ vs $M_y$)")

    fig = go.Figure()

    mx_vals = df_plastic["Mx"].tolist()
    my_vals = df_plastic["My"].tolist()

    if mx_vals and my_vals:
        mx_vals.append(mx_vals[0])
        my_vals.append(my_vals[0])

    fig.add_trace(
        go.Scatter(
            x=mx_vals,
            y=my_vals,
            fill="toself",
            fillcolor="rgba(220, 50, 50, 0.15)",
            line=dict(color="red", width=2.5),
            name="Capacity limit",
            hovertext=[f"Angle V = {v:.1f}°" for v in df_plastic["V"].tolist()] + [f"Angle V = {df_plastic['V'].iloc[0]:.1f}°"],
            hoverinfo="text+x+y",
            mode="lines+markers",
            marker=dict(size=4, color="darkred"),
        )
    )

    fig.update_layout(
        xaxis=dict(title="Moment $M_x$ [kNm]", zeroline=True, zerolinewidth=1.5, zerolinecolor="black"),
        yaxis=dict(title="Moment $M_y$ [kNm]", zeroline=True, zerolinewidth=1.5, zerolinecolor="black"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=30, b=10),
        height=500,
    )

    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    st.markdown("#### Angular sweep output data")
    st.dataframe(
        df_display.style.format(
            {
                "U (deg)": "{:.1f}",
                "R (m)": "{:.3f}",
                "Mx [kNm]": "{:.1f}",
                "My [kNm]": "{:.1f}",
                "V [deg]": "{:.1f}",
                "Depth y_na [m]": "{:.3f}",
                "Curvature [1/m]": "{:.6f}",
                "NA x-intercept [m]": "{:.4f}",
                "NA y-intercept [m]": "{:.4f}",
                "ε_c [‰]": "{:.2f}",
                "ε_s [‰]": "{:.2f}",
                "ε_p [‰]": "{:.2f}",
                "Compression force [kN]": "{:.2f}",
                "Lever arm L [m]": "{:.4f}",
                "Lever arm DX [m]": "{:.4f}",
                "Lever arm DY [m]": "{:.4f}",
            },
            na_rep="N/A",
        ),
        width="stretch",
        height=400,
    )

def render_plastic_export(case_name: str, plastic_output: list, data: dict | None = None):
    safe_label, safe_slug = _normalize_case_name(case_name)
    df_plastic = prepare_plastic_results_dataframe(plastic_output).attrs.get("export_df", pd.DataFrame())
    settings = (data or {}).get("analysis_settings", {})
    mild = ((data or {}).get("materials", {})).get("mild_steel", {})
    meta_df = pd.DataFrame(
        [
            {"meta": "gamma_E", "value": settings.get("gamma_E", 1.0)},
            {"meta": "gamma_u", "value": settings.get("gamma_u", 1.0)},
            {"meta": "f_yk_t_MPa", "value": mild.get("f_yk_t_MPa", mild.get("f_yk", 500.0))},
            {"meta": "f_yk_c_MPa", "value": mild.get("f_yk_c_MPa", mild.get("f_yk", 500.0))},
        ]
    )
    df_export = pd.concat([meta_df, pd.DataFrame([{}]), df_plastic], ignore_index=True, sort=False)
    st.download_button(
        f"Download plastic CSV: {safe_label}",
        data=_to_csv_bytes(df_export),
        file_name=f"plastic_{safe_slug}.csv",
        mime="text/csv",
    )
