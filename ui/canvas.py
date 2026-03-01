import plotly.graph_objects as go
import streamlit as st

from utils.data_io import initialize_session_state


def render_geometry_plot():
    """Renders the interactive Plotly graph for the cross section."""
    initialize_session_state()
    geom = st.session_state.data["geometry"]

    fig = go.Figure()

    # 1. Plot Concrete Outline
    concrete_outline = geom.get("concrete_outline") or []
    if not concrete_outline:
        st.info("Geometry has no concrete outline points to plot yet.")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})
        return

    x_out = [pt["x"] for pt in concrete_outline]
    y_out = [pt["y"] for pt in concrete_outline]

    # Close the polygon by repeating the first point
    x_out.append(x_out[0])
    y_out.append(y_out[0])

    fig.add_trace(
        go.Scatter(
            x=x_out,
            y=y_out,
            fill="toself",
            fillcolor="rgba(200, 200, 200, 0.5)",
            line=dict(color="black", width=2),
            name="Concrete",
            hoverinfo="x+y",
            mode="lines",
        )
    )

    # 2. Plot Concrete Voids
    for i, void in enumerate(geom.get("concrete_voids", [])):
        if void:
            x_v = [pt["x"] for pt in void]
            y_v = [pt["y"] for pt in void]

            x_v.append(x_v[0])
            y_v.append(y_v[0])

            fig.add_trace(
                go.Scatter(
                    x=x_v,
                    y=y_v,
                    fill="toself",
                    fillcolor="white",
                    line=dict(color="black", width=1, dash="dash"),
                    name=f"Void {i+1}",
                    hoverinfo="x+y",
                    mode="lines",
                )
            )

    # 3. Plot Mild Reinforcement
    if geom.get("reinforcement_mild"):
        x_m = [bar["x"] for bar in geom["reinforcement_mild"]]
        y_m = [bar["y"] for bar in geom["reinforcement_mild"]]
        text_m = [f"ID: {bar['id']}<br>Area: {bar['area']} mm²" for bar in geom["reinforcement_mild"]]

        fig.add_trace(
            go.Scatter(
                x=x_m,
                y=y_m,
                mode="markers",
                marker=dict(color="blue", size=8, symbol="circle"),
                name="Mild Steel",
                text=text_m,
                hoverinfo="text+x+y",
            )
        )

    # 4. Plot Prestressed Reinforcement
    if geom.get("reinforcement_prestressed"):
        x_p = [bar["x"] for bar in geom["reinforcement_prestressed"]]
        y_p = [bar["y"] for bar in geom["reinforcement_prestressed"]]
        text_p = [f"ID: {bar['id']}<br>Area: {bar['area']} mm²" for bar in geom["reinforcement_prestressed"]]

        fig.add_trace(
            go.Scatter(
                x=x_p,
                y=y_p,
                mode="markers",
                marker=dict(color="red", size=10, symbol="diamond"),
                name="Prestressed Steel",
                text=text_p,
                hoverinfo="text+x+y",
            )
        )

    # 5. Configure Layout for Structural Engineering
    fig.update_layout(
        xaxis=dict(
            title="Width, x (m)",
            scaleanchor="y",
            scaleratio=1,
            zeroline=True,
            zerolinewidth=1.5,
            zerolinecolor="black",
        ),
        yaxis=dict(
            title="Depth, y (m)",
            zeroline=True,
            zerolinewidth=1.5,
            zerolinecolor="black",
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.8)",
        ),
    )

    # Render in Streamlit
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})
