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
from utils.section_properties import centroid_and_principal_axes


def _marker_size(area):
    return max(6.0, min(18.0, math.sqrt(max(area, 1.0)) / 2.0))


def _add_id_labels(fig, records, x_key, y_key, show, name, color="#333", xshift_px=10, yshift_px=10):
    if not show or not records:
        return
    for row in records:
        fig.add_annotation(
            x=row[x_key],
            y=row[y_key],
            text=str(row.get("id", "")),
            showarrow=False,
            xshift=xshift_px,
            yshift=yshift_px,
            font=dict(size=11, color=color),
            bgcolor="rgba(255,255,255,0.6)",
            bordercolor="rgba(0,0,0,0.15)",
            borderwidth=1,
        )


def _clip_line_abc_to_bounds(a, b, c, x_range, y_range):
    xmin, xmax = x_range
    ymin, ymax = y_range
    points = []

    if abs(b) > 1e-12:
        for x in (xmin, xmax):
            y = -(a * x + c) / b
            if ymin - 1e-12 <= y <= ymax + 1e-12:
                points.append((float(x), float(y)))

    if abs(a) > 1e-12:
        for y in (ymin, ymax):
            x = -(b * y + c) / a
            if xmin - 1e-12 <= x <= xmax + 1e-12:
                points.append((float(x), float(y)))

    unique = []
    for p in points:
        if not any(abs(p[0] - q[0]) < 1e-9 and abs(p[1] - q[1]) < 1e-9 for q in unique):
            unique.append(p)

    if len(unique) < 2:
        return None

    best_pair = None
    best_dist2 = -1.0
    for i in range(len(unique)):
        for j in range(i + 1, len(unique)):
            dx = unique[i][0] - unique[j][0]
            dy = unique[i][1] - unique[j][1]
            d2 = dx * dx + dy * dy
            if d2 > best_dist2:
                best_dist2 = d2
                best_pair = (unique[i], unique[j])

    return best_pair


def render_geometry_plot():
    initialize_session_state()
    data = st.session_state.data
    geom = copy.deepcopy(data["geometry"])
    geom = normalize_geometry_for_use(geom)
    geom = normalize_rebar_ids(geom)
    options = data.get("plot_options", {})

    def _compute_axis_bounds():
        points = []
        points.extend((pt["x"], pt["y"]) for pt in geom.get("concrete_outline", []))
        for void in geom.get("concrete_voids", []):
            points.extend((pt["x"], pt["y"]) for pt in void)
        points.extend((bar["x"], bar["y"]) for bar in geom.get("reinforcement_mild", []))
        points.extend((bar["x"], bar["y"]) for bar in geom.get("reinforcement_prestressed", []))

        if not points:
            return [-1.0, 1.0], [-1.0, 1.0]

        xs, ys = zip(*points)
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        span = max(xmax - xmin, ymax - ymin, 1.0)
        pad = max(0.10 * span, 0.1)
        return [xmin - pad, xmax + pad], [ymin - pad, ymax + pad]

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
        _add_id_labels(
            fig,
            outline,
            "x",
            "y",
            options.get("show_concrete_point_ids", False),
            "Concrete IDs",
            color="#222",
        )

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
        _add_id_labels(
            fig,
            ordered_void,
            "x",
            "y",
            options.get("show_void_point_ids", False),
            f"Void {idx} IDs",
            color="#666",
        )

    scale_bar_markers_by_area = bool(options.get("scale_bar_markers_by_area", False))
    mild = geom.get("reinforcement_mild", [])
    if mild:
        mild_marker_size = [_marker_size(bar["area"]) if scale_bar_markers_by_area else 10 for bar in mild]
        fig.add_trace(
            go.Scatter(
                x=[bar["x"] for bar in mild],
                y=[bar["y"] for bar in mild],
                mode="markers",
                marker=dict(color="#1f77b4", size=mild_marker_size, symbol="circle"),
                name="Mild steel",
                text=[f"ID: {bar['id']}<br>Area: {bar['area']:.2f} mm²" for bar in mild],
                hoverinfo="text+x+y",
            )
        )
        _add_id_labels(fig, mild, "x", "y", options.get("show_mild_bar_ids", False), "Mild IDs", color="#1f77b4")

    prestressed = geom.get("reinforcement_prestressed", [])
    if prestressed:
        prestressed_marker_size = [_marker_size(bar["area"]) if scale_bar_markers_by_area else 10 for bar in prestressed]
        fig.add_trace(
            go.Scatter(
                x=[bar["x"] for bar in prestressed],
                y=[bar["y"] for bar in prestressed],
                mode="markers",
                marker=dict(color="#d62728", size=prestressed_marker_size, symbol="diamond"),
                name="Prestressed steel",
                text=[f"ID: {bar['id']}<br>Area: {bar['area']:.2f} mm²" for bar in prestressed],
                hoverinfo="text+x+y",
            )
        )
        _add_id_labels(
            fig,
            prestressed,
            "x",
            "y",
            options.get("show_prestressed_bar_ids", False),
            "Prestressed IDs",
            color="#d62728",
        )

    x_range, y_range = _compute_axis_bounds()
    line_width = float(options.get("overlay_line_width", 2.0))

    section_props = None
    if poly and poly.is_valid and not poly.is_empty:
        try:
            section_props = centroid_and_principal_axes(poly)
        except Exception:
            section_props = None

    if options.get("show_centroid", True) and section_props is not None:
        cx = section_props["cx"]
        cy = section_props["cy"]
        fig.add_trace(
            go.Scatter(
                x=[cx],
                y=[cy],
                mode="markers+text",
                marker=dict(color="#2ca02c", size=11, symbol="x"),
                text=["C"],
                textposition="top right",
                name="Centroid",
                hovertemplate="Centroid<br>x=%{x:.4f}<br>y=%{y:.4f}<extra></extra>",
            )
        )

    if options.get("show_principal_axes", False) and section_props is not None:
        cx = section_props["cx"]
        cy = section_props["cy"]
        x_span = x_range[1] - x_range[0]
        y_span = y_range[1] - y_range[0]
        L = 0.35 * max(x_span, y_span)
        for (vx, vy), name, color in [
            (section_props["v1"], "Principal axis 1", "#9467bd"),
            (section_props["v2"], "Principal axis 2", "#8c564b"),
        ]:
            a = vy
            b = -vx
            c = -(a * cx + b * cy)
            clipped = _clip_line_abc_to_bounds(a, b, c, x_range, y_range)
            if clipped is None:
                p1 = (cx - L * vx, cy - L * vy)
                p2 = (cx + L * vx, cy + L * vy)
            else:
                p1, p2 = clipped
            fig.add_trace(
                go.Scatter(
                    x=[p1[0], p2[0]],
                    y=[p1[1], p2[1]],
                    mode="lines",
                    line=dict(color=color, width=line_width),
                    name=name,
                )
            )

    cache = st.session_state.get("last_results_cache")
    current_hash = st.session_state.get("current_input_hash")
    cache_current = bool(cache and cache.get("hash") == current_hash)

    if options.get("show_elastic_na", True):
        if cache_current:
            case_id = options.get("elastic_na_case_id")
            state = options.get("elastic_na_state", "RST1")
            elastic_items = cache.get("results", {}).get("elastic", [])
            selected = next((item for item in elastic_items if item.get("case", {}).get("id") == case_id), None)
            if selected and selected.get("result"):
                key = "na_LONG" if state == "LONG" else "na_RST1"
                na = selected["result"].get(key)
                if na is not None:
                    a = float(na.get("ky", 0.0))
                    b = float(na.get("kx", 0.0))
                    c = float(na.get("eps0", 0.0))
                    clipped = _clip_line_abc_to_bounds(a, b, c, x_range, y_range)
                    if clipped is not None:
                        (x1, y1), (x2, y2) = clipped
                        fig.add_trace(
                            go.Scatter(
                                x=[x1, x2],
                                y=[y1, y2],
                                mode="lines",
                                line=dict(color="#ff7f0e", width=line_width, dash="dash"),
                                name=f"Elastic NA ({state})",
                            )
                        )
        else:
            st.info("Run analysis to display neutral axis")

    if options.get("show_plastic_na", False):
        if cache_current:
            case_id = options.get("plastic_na_case_id")
            angle_target = float(options.get("plastic_na_angle_deg", 0.0))
            plastic_items = cache.get("results", {}).get("plastic", [])
            selected = next((item for item in plastic_items if item.get("case", {}).get("id") == case_id), None)
            if selected and selected.get("result"):
                entries = [entry for entry in selected["result"] if entry.get("V") is not None and entry.get("y_na") is not None]
                if entries:
                    closest = min(entries, key=lambda item: abs(float(item.get("V", 0.0)) - angle_target))
                    V = float(closest.get("V", 0.0))
                    y_na = float(closest.get("y_na", 0.0))
                    rad = math.radians(V)
                    a = -math.sin(rad)
                    b = math.cos(rad)
                    c = -y_na
                    clipped = _clip_line_abc_to_bounds(a, b, c, x_range, y_range)
                    if clipped is not None:
                        (x1, y1), (x2, y2) = clipped
                        fig.add_trace(
                            go.Scatter(
                                x=[x1, x2],
                                y=[y1, y2],
                                mode="lines",
                                line=dict(color="#17becf", width=line_width, dash="dot"),
                                name=f"Plastic NA (V≈{V:.1f}°)",
                            )
                        )
        else:
            st.info("Run analysis to display neutral axis")

    fig.update_layout(
        xaxis=dict(
            title="Width, x (m)",
            scaleanchor="y",
            scaleratio=1,
            zeroline=True,
            zerolinecolor="#B0B0B0",
            zerolinewidth=1,
            showgrid=False,
            range=x_range,
        ),
        yaxis=dict(
            title="Depth, y (m)",
            zeroline=True,
            zerolinecolor="#B0B0B0",
            zerolinewidth=1,
            showgrid=False,
            range=y_range,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=90, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        uirevision="geometry",
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": True})
