import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import numpy as np


def _to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def render_geometry_exports(geometry: dict):
    st.markdown("#### Exports")
    outline_df = pd.DataFrame(geometry.get("concrete_outline", []), columns=["id", "x", "y"])
    st.download_button(
        "Download outline points CSV",
        data=_to_csv_bytes(outline_df),
        file_name="geometry_outline_points.csv",
        mime="text/csv",
    )

    void_rows = []
    for i, void in enumerate(geometry.get("concrete_voids", []), start=1):
        for pt in void:
            void_rows.append({"void_index": i, "id": pt.get("id"), "x": pt.get("x"), "y": pt.get("y")})
    void_df = pd.DataFrame(void_rows, columns=["void_index", "id", "x", "y"])
    st.download_button(
        "Download void points CSV",
        data=_to_csv_bytes(void_df),
        file_name="geometry_void_points.csv",
        mime="text/csv",
    )

    mild_rows = [{"type": "mild", **bar} for bar in geometry.get("reinforcement_mild", [])]
    pre_rows = [{"type": "prestress", **bar} for bar in geometry.get("reinforcement_prestressed", [])]
    rebar_df = pd.DataFrame(mild_rows + pre_rows)
    st.download_button(
        "Download reinforcement CSV",
        data=_to_csv_bytes(rebar_df),
        file_name="geometry_rebar.csv",
        mime="text/csv",
    )


def render_elastic_results(elastic_output: dict):
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Max Concrete Compression", value=f"{elastic_output.get('max_concrete', 0.0):.0f} kPa")
    with col2:
        max_tension = 0.0
        if elastic_output.get("RST_total"):
            max_tension = max(list(elastic_output["RST_total"].values()) + [0.0])
        st.metric(label="Max Steel Tension (TOTAL)", value=f"{max_tension:.0f} kPa")

    st.markdown("#### Individual Bar Stresses")

    table_data = []
    bar_ids = elastic_output.get("RST_total", {}).keys()

    for b_id in bar_ids:
        table_data.append(
            {
                "Bar NO": b_id,
                "TOTAL (kPa)": elastic_output["RST_total"].get(b_id, 0.0),
                "LONG (kPa)": elastic_output["LONG_s1"].get(b_id, 0.0),
                "DIF (kPa)": elastic_output["DIF"].get(b_id, 0.0),
                "RST1 (kPa)": elastic_output["RST1_s3"].get(b_id, 0.0),
            }
        )

    if table_data:
        df_elastic = pd.DataFrame(table_data)
        st.dataframe(df_elastic.style.format(precision=0), width="stretch")
    else:
        st.info("No reinforcement data available.")


def render_elastic_export(case_name: str, elastic_output: dict):
    rows = []
    for key, value in elastic_output.items():
        if isinstance(value, dict):
            for sub_key, sub_val in value.items():
                rows.append({"metric": key, "item": sub_key, "value": sub_val})
        elif isinstance(value, (list, tuple)):
            for idx, item in enumerate(value):
                rows.append({"metric": key, "item": idx, "value": item})
        else:
            rows.append({"metric": key, "item": "", "value": value})
    df = pd.DataFrame(rows, columns=["metric", "item", "value"])
    st.download_button(
        f"Download elastic CSV: {case_name}",
        data=_to_csv_bytes(df),
        file_name=f"elastic_{case_name.replace(' ', '_')}.csv",
        mime="text/csv",
    )


def render_plastic_results(plastic_output: list, target_P: float):
    if not plastic_output:
        st.warning("No plastic calculation data generated.")
        return

    df_plastic = pd.DataFrame(plastic_output)
    df_plastic["R (m)"] = np.sqrt(df_plastic["Mx"] ** 2 + df_plastic["My"] ** 2) / target_P
    df_plastic["U (deg)"] = np.degrees(np.arctan2(df_plastic["Mx"], df_plastic["My"]))

    display_cols = ["U (deg)", "R (m)", "Mx", "My", "V", "y_na", "kappa", "pivot"]
    df_display = df_plastic[display_cols].copy()

    df_display.rename(
        columns={
            "Mx": "Mx (kNm)",
            "My": "My (kNm)",
            "V": "V (deg)",
            "y_na": "Depth y_na (m)",
            "kappa": "Curvature (1/m)",
            "pivot": "Failure Pivot",
        },
        inplace=True,
    )

    st.markdown("#### Biaxial Capacity Envelope ($M_x$ vs $M_y$)")

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
            name="Capacity Limit",
            hovertext=[f"Angle V = {v:.1f}°" for v in df_plastic["V"].tolist()] + [f"Angle V = {df_plastic['V'].iloc[0]:.1f}°"],
            hoverinfo="text+x+y",
            mode="lines+markers",
            marker=dict(size=4, color="darkred"),
        )
    )

    fig.update_layout(
        xaxis=dict(title="Moment $M_x$ (kNm)", zeroline=True, zerolinewidth=1.5, zerolinecolor="black"),
        yaxis=dict(title="Moment $M_y$ (kNm)", zeroline=True, zerolinewidth=1.5, zerolinecolor="black"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=30, b=10),
        height=500,
    )

    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    st.markdown("#### Angular Sweep Output Data")
    st.dataframe(
        df_display.style.format(
            {
                "U (deg)": "{:.1f}",
                "R (m)": "{:.3f}",
                "Mx (kNm)": "{:.1f}",
                "My (kNm)": "{:.1f}",
                "V (deg)": "{:.1f}",
                "Depth y_na (m)": "{:.3f}",
                "Curvature (1/m)": "{:.6f}",
            }
        ),
        width="stretch",
        height=400,
    )


def render_plastic_export(case_name: str, plastic_output: list):
    df_plastic = pd.DataFrame(plastic_output)
    st.download_button(
        f"Download plastic CSV: {case_name}",
        data=_to_csv_bytes(df_plastic),
        file_name=f"plastic_{case_name.replace(' ', '_')}.csv",
        mime="text/csv",
    )
