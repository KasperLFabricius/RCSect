import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def render_elastic_results(elastic_output: dict):
    """
    Renders the tables for the elastic analysis using the 4-step ECROSS methodology.
    """
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Max Concrete Compression", 
            value=f"{elastic_output.get('max_concrete', 0.0):.0f} kPa"
        )
    with col2:
        max_tension = 0.0
        if elastic_output.get("RST_total"):
            max_tension = max(list(elastic_output["RST_total"].values()) + [0.0])
        st.metric(
            label="Max Steel Tension (TOTAL)", 
            value=f"{max_tension:.0f} kPa"
        )

    st.markdown("#### Individual Bar Stresses")
    
    table_data = []
    bar_ids = elastic_output.get("RST_total", {}).keys()
    
    for b_id in bar_ids:
        table_data.append({
            "Bar NO": b_id,
            "TOTAL (kPa)": elastic_output["RST_total"].get(b_id, 0.0),
            "LONG (kPa)": elastic_output["LONG_s1"].get(b_id, 0.0),
            "DIF (kPa)": elastic_output["DIF"].get(b_id, 0.0),
            "RST1 (kPa)": elastic_output["RST1_s3"].get(b_id, 0.0)
        })
        
    if table_data:
        df_elastic = pd.DataFrame(table_data)
        st.dataframe(df_elastic.style.format(precision=0), width="stretch")
    else:
        st.info("No reinforcement data available.")

def render_plastic_results(plastic_output: list, target_P: float):
    """
    Takes the aggregated list of results from the V_min to V_max sweep 
    and renders the biaxial interaction envelope and detailed data table.
    """
    if not plastic_output:
        st.warning("No plastic calculation data generated.")
        return

    df_plastic = pd.DataFrame(plastic_output)
    
    # Calculate the angle U and radius R (polar coordinates of the moment)
    # R = sqrt(Mx^2 + My^2) / P
    df_plastic["R (m)"] = np.sqrt(df_plastic["Mx"]**2 + df_plastic["My"]**2) / target_P
    df_plastic["U (deg)"] = np.degrees(np.arctan2(df_plastic["Mx"], df_plastic["My"]))
    
    # Format the dataframe to match the legacy PCROSS tabular output
    display_cols = ["U (deg)", "R (m)", "Mx", "My", "V", "y_na", "kappa", "pivot"]
    df_display = df_plastic[display_cols].copy()
    
    df_display.rename(columns={
        "Mx": "Mx (kNm)",
        "My": "My (kNm)",
        "V": "V (deg)",
        "y_na": "Depth y_na (m)",
        "kappa": "Curvature (1/m)",
        "pivot": "Failure Pivot"
    }, inplace=True)

    # 1. Plot the Interactive Capacity Envelope
    st.markdown("#### Biaxial Capacity Envelope ($M_x$ vs $M_y$)")
    
    fig = go.Figure()
    
    mx_vals = df_plastic["Mx"].tolist()
    my_vals = df_plastic["My"].tolist()
    
    # Close the loop for a continuous polygon visual
    if mx_vals and my_vals:
        mx_vals.append(mx_vals[0])
        my_vals.append(my_vals[0])

    
        
    fig.add_trace(go.Scatter(
        x=mx_vals, 
        y=my_vals,
        fill="toself",
        fillcolor="rgba(220, 50, 50, 0.15)",
        line=dict(color="red", width=2.5),
        name="Capacity Limit",
        hovertext=[f"Angle V = {v:.1f}°" for v in df_plastic["V"].tolist()] + [f"Angle V = {df_plastic['V'].iloc[0]:.1f}°"],
        hoverinfo="text+x+y",
        mode="lines+markers",
        marker=dict(size=4, color="darkred")
    ))
    
    fig.update_layout(
        xaxis=dict(title="Moment $M_x$ (kNm)", zeroline=True, zerolinewidth=1.5, zerolinecolor="black"),
        yaxis=dict(title="Moment $M_y$ (kNm)", zeroline=True, zerolinewidth=1.5, zerolinecolor="black"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=30, b=10),
        height=500
    )
    
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    # 2. Render the Detailed Iteration Table
    st.markdown("#### Angular Sweep Output Data")
    st.dataframe(df_display.style.format({
        "U (deg)": "{:.1f}",
        "R (m)": "{:.3f}",
        "Mx (kNm)": "{:.1f}",
        "My (kNm)": "{:.1f}",
        "V (deg)": "{:.1f}",
        "Depth y_na (m)": "{:.3f}",
        "Curvature (1/m)": "{:.6f}"
    }), width="stretch", height=400)
