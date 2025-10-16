# file: visualize_pi_star_damping.py

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import plotly.graph_objects as go

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "π*-Damped Recovery Curve"

# Define layout
app.layout = html.Div([
    html.H2("π* Damped Feedback Recovery Visualization", style={"textAlign": "center"}),
    dcc.Slider(
        id='pi-slider', min=1, max=5, step=0.01, value=np.pi,
        marks={1: '1', 3.14: 'π', 5: '5'},
        tooltip={"always_visible": True, "placement": "bottom"}
    ),
    dcc.Graph(id='pi-damping-graph'),
    html.P("Adjust π* to visualize how feedback damping changes recovery behavior.")
])

# Define update logic
@app.callback(
    Output('pi-damping-graph', 'figure'),
    Input('pi-slider', 'value')
)
def update_graph(pi_star):
    # Simulate recovery curve
    t = np.linspace(0, 10, 200)
    P0, P_target = 0.4, 1.0
    t_half = 3.0
    P = P0 + (1 - np.exp(-pi_star * np.sqrt(t / t_half))) * (P_target - P0)

    # Create Plotly graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=P, mode='lines', line=dict(width=3),
                             name=f'π*={pi_star:.2f}'))
    fig.update_layout(
        title="Adaptive Priority Recovery After Anomaly",
        xaxis_title="Time (t)",
        yaxis_title="Normalized Priority (P)",
        template="plotly_dark"
    )
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)