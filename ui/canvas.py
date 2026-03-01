import copy
import math

import plotly.graph_objects as go
import streamlit as st

from utils.data_io import (
    geometry_to_polygon,
    initialize_session_state,
    normalize_geometry_for_use,
    normalize_rebar_ids,
    validate_geometry_topology,
)


def _marker_size(area):
    return max(6.0, min(18.0, math.sqrt(max(area, 1.0)) / 2.0))


def _add_id_labels(fig, records, x_key, y_key, show, name):
    if not show or not records:
        return
    fig.add_trace(
        go.Scatter(
            x=[row[x_key] + 0.01 for row in records],
            y=[row[y_key] + 0.01 for row in records],
            mode="text",
            text=[str(row.get("id", "")) for row in records],
            textfont=dict(size=10, color="#333"),
            name=name,
            showlegend=False,
            hoverinfo="skip",
        )
    )


def render_geometry_plot():
    initialize_session_state()
    data = st.session_state.data
    geom = copy.deepcopy(data["geometry"])
    geom = normalize_geometry_for_use(geom)
    geom = normalize_rebar_ids(geom)
    options = data.get("plot_options", {})

    fig = go.Figure()
    poly = geometry_to_polygon(geom)
    topo = validate_geometry_topology(geom)

    outline = sorted(geom.get("concrete_outline", []), key=lambda pt: pt["id"])
    if not outline:
        st.info("Geometry has no concrete outline points to plot yet.")
    else:
        x_out = [pt["x"] for pt in outline] + [outline[0]["x"]]
        y_out = [pt["y"] for pt in outline] + [outline[0]["y"]]
        can_fill = bool(poly and not poly.is_empty and poly.is_valid)

        fig.add_trace(
            go.Scatter(
                x=x_out,
                y=y_out,
                mode="lines+markers",
                line=dict(color="black", width=3),
                marker=dict(color="black", size=6, symbol="circle"),
                fill="toself" if can_fill else None,
                fillcolor="rgba(180, 180, 180, 0.45)",
                name="Concrete outline",
            )
        )
        _add_id_labels(fig, outline, "x", "y", options.get("show_concrete_point_ids", False), "Concrete IDs")

        if not can_fill and topo["errors"]:
            st.warning(f"Concrete polygon is invalid: {topo['errors'][0]}")

    for idx, void in enumerate(geom.get("concrete_voids", []), start=1):
        ordered_void = sorted(void, key=lambda pt: pt["id"])
        if not ordered_void:
            continue
        xv = [pt["x"] for pt in ordered_void] + [ordered_void[0]["x"]]
        yv = [pt["y"] for pt in ordered_void] + [ordered_void[0]["y"]]
        fig.add_trace(
            go.Scatter(
                x=xv,
                y=yv,
                mode="lines+markers",
                line=dict(color="#666", width=1.4, dash="dash"),
                marker=dict(color="#666", size=5, symbol="diamond-open"),
                fill="toself" if (poly and poly.is_valid and not poly.is_empty) else None,
                fillcolor="rgba(255,255,255,0.95)",
                name=f"Void {idx}",
            )
        )
        _add_id_labels(fig, ordered_void, "x", "y", options.get("show_void_point_ids", False), f"Void {idx} IDs")

    mild = geom.get("reinforcement_mild", [])
    if mild:
        fig.add_trace(
            go.Scatter(
                x=[bar["x"] for bar in mild],
                y=[bar["y"] for bar in mild],
                mode="markers",
                marker=dict(color="#1f77b4", size=[_marker_size(bar["area"]) for bar in mild], symbol="circle"),
                name="Mild steel",
                text=[f"ID: {bar['id']}<br>Area: {bar['area']:.2f} mm²" for bar in mild],
                hoverinfo="text+x+y",
            )
        )
        _add_id_labels(fig, mild, "x", "y", options.get("show_mild_bar_ids", False), "Mild IDs")

    prestressed = geom.get("reinforcement_prestressed", [])
    if prestressed:
        fig.add_trace(
            go.Scatter(
                x=[bar["x"] for bar in prestressed],
                y=[bar["y"] for bar in prestressed],
                mode="markers",
                marker=dict(color="#d62728", size=[_marker_size(bar["area"]) for bar in prestressed], symbol="diamond"),
                name="Prestressed steel",
                text=[f"ID: {bar['id']}<br>Area: {bar['area']:.2f} mm²" for bar in prestressed],
                hoverinfo="text+x+y",
            )
        )
        _add_id_labels(fig, prestressed, "x", "y", options.get("show_prestressed_bar_ids", False), "Prestressed IDs")

    fig.update_layout(
        xaxis=dict(
            title="Width, x (m)",
            scaleanchor="y",
            scaleratio=1,
            zeroline=True,
            zerolinecolor="#B0B0B0",
            zerolinewidth=1,
            showgrid=False,
        ),
        yaxis=dict(
            title="Depth, y (m)",
            zeroline=True,
            zerolinecolor="#B0B0B0",
            zerolinewidth=1,
            showgrid=False,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=90, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        shapes=[
            dict(type="line", x0=-1e3, x1=1e3, y0=0, y1=0, line=dict(color="#B0B0B0", width=1, dash="dash")),
            dict(type="line", x0=0, x1=0, y0=-1e3, y1=1e3, line=dict(color="#B0B0B0", width=1, dash="dash")),
        ],
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": True})
