# synara_rmp_dashboard.py
app.layout = html.Div([
    dcc.Graph(id="79hz-coherence-heatmap"),
    dcc.Graph(id="glyph-tree"),
    dcc.Graph(id="pi-star-drift"),
    dcc.Graph(id="gamma-pulse"),
    dcc.Graph(id="fuel-burn-rate"),
    html.H1("SKODEN — MESH IS LIVE")
])