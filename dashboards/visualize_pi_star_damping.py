"""
π*-Damped Feedback Recovery Visualization
------------------------------------------
Part of Feedback Processor Theory (FPT)
© 2025 Two Mile Solutions LLC / John Carroll

Description:
Interactive Dash visualization that models how the π* damping mechanism 
controls recovery stability after a feedback anomaly. 
Used within Synara’s adaptive scheduler system to visualize recovery curves 
and demonstrate feedback harmony over time.
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "π*-Damped Recovery Curve"

# App Layout
app.layout = html.Div(
    style={"backgroundColor": "#0f0f0f", "color": "#e0e0e0", "padding": "2rem"},
    children=[
        html.H1("Feedback Processor Theory: π*-Damped Recovery Curve",
                style={"textAlign": "center", "color": "#ffcc00"}),
        html.P("Visualizing adaptive recovery dynamics using the π* damping mechanism.",
               style={"textAlign": "center"}),

        # Slider for pi-star adjustment
        html.Div([
            html.Label("Adjust π* (Feedback Damping Coefficient):", style={"fontWeight": "bold"}),
            dcc.Slider(
                id='pi-slider',
                min=1.0, max=5.0, step=0.01, value=np.pi,
                marks={1: '1.0', 3.14: 'π', 5: '5.0'},
                tooltip={"always_visible": True, "placement": "bottom"}
            ),
        ], style={"margin": "2rem"}),

        # Main graph
        dcc.Graph(id='pi-damping-graph', style={"height": "70vh"}),

        html.P(id='timestamp', style={"textAlign": "center", "marginTop": "1rem", "fontSize": "0.9rem"})
    ]
)

# Update function for dynamic damping visualization
@app.callback(
    [Output('pi-damping-graph', 'figure'),
     Output('timestamp', 'children')],
    [Input('pi-slider', 'value')]
)
def update_graph(pi_star):
    # Simulate time series
    t = np.linspace(0, 10, 200)
    P0, P_target = 0.4, 1.0
    t_half = 3.0

    # π*-damped recovery function
    P = P0 + (1 - np.exp(-pi_star * np.sqrt(t / t_half))) * (P_target - P0)

    # Build figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=t, y=P, mode='lines', line=dict(width=3, color='#ffcc00'),
        name=f'π* = {pi_star:.2f}'
    ))

    # Add reference lines
    fig.add_hline(y=P_target, line_dash="dot", line_color="#00ff99", annotation_text="Steady State")
    fig.add_hline(y=P0, line_dash="dot", line_color="#ff6666", annotation_text="Anomaly Baseline")

    fig.update_layout(
        template="plotly_dark",
        title="Adaptive Priority Recovery After Anomaly",
        xaxis_title="Time (t)",
        yaxis_title="Normalized Priority (P)",
        margin=dict(l=40, r=40, t=80, b=40),
        showlegend=True
    )

    # Timestamp for live refresh
    ts = f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"

    return fig, ts


if __name__ == "__main__":
    app.run_server(debug=True)