import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, dash_table, Output, Input, State
import dash_bootstrap_components as dbc

# Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Data path
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "..", "data_input", "data_preparation.csv")
df = pd.read_csv(data_path)

# Columns
ELEC_COLS = ["electricity_demand", "electricity_generation"]

COUNTRY_COLS = {
    "country": "Country",
    "iso_code": "ISO Code:",
    "population": "Population",
    "gdp": "GDP",
    "net_elec_imports_share_demand": "Net Electricity Imports",
    "per_capita_electricity": "Electricity Generation Per Person:",
    "risk_sum": "Risk Potential:"
}

SOURCE_MAPPING = {
    "gas_electricity": ("Gas", "orange"),
    "coal_electricity": ("Coal", "orange"),
    "oil_electricity": ("Oil", "orange"),
    "nuclear_electricity": ("Nuclear", "red"),
    "solar_electricity": ("Solar", "green"),
    "wind_electricity": ("Wind", "green"),
    "hydro_electricity": ("Hydro", "green"),
    "biofuel_electricity": ("Biofuel", "green"),
    "other_renewable_exc_biofuel_electricity": ("Other Renewable", "green")
}

SOURCE_COLS = list(SOURCE_MAPPING.keys())

# Initial Map
fig = px.choropleth(
    df,
    locations="iso_code",
    color="risk_sum",
    color_continuous_scale="RdYlGn_r",
    hover_name="country",
    title="World Map of Energy Data 2022",
    labels={"risk_sum": "Risk Potential:"},
    hover_data={"iso_code": False}
)
fig.update_layout(
    geo=dict(fitbounds="locations", projection_scale=1, center=dict(lat=20, lon=0)),
    coloraxis_colorbar=dict(title="Risk Potential:", x=-0.1, thickness=10, len=0.6, tickfont=dict(size=10)),
    margin=dict(l=10, r=10, t=30, b=10)
)

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H3("Global Energy Dashboard"), width=9),
        dbc.Col(html.Div([
            dbc.Button("Reset Selection", id="reset-button", color="secondary", size="sm", className="float-end")
        ]), width=3)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dcc.Graph(id="world-map", figure=fig, style={"height": "50vh", "width": "100%"})
            ]),
            dbc.Row([
                html.H5("Electricity Mix"),
                dcc.Graph(id="source-bar", style={"height": "45vh"})
            ])
        ], width=8),
        dbc.Col([
            dbc.Row([
                html.H5("Country Data"),
                dash_table.DataTable(
                    id="country-table",
                    style_table={'height': '45vh', 'overflowY': 'auto'},
                    style_cell={'textAlign': 'left', 'fontSize': 12, 'padding': '5px'}
                )
            ]),
            dbc.Row([
                html.H5("Electricity Demand / Generation"),
                dcc.Graph(id="demand-pie", style={"height": "45vh"})
            ])
        ], width=4)
    ])
], fluid=True, style={"height": "100vh", "padding": "10px"})


# Callback
@app.callback(
    [Output("country-table", "data"),
     Output("country-table", "columns"),
     Output("demand-pie", "figure"),
     Output("source-bar", "figure"),
     Output("world-map", "figure")],
    [Input("world-map", "clickData"),
     Input("reset-button", "n_clicks")]
)
def update_visuals(clickData, reset_clicks):
    triggered = dash.callback_context.triggered_id

    # Wenn Reset oder keine Auswahl → Standardzustand
    if triggered == "reset-button" or clickData is None:
        empty_fig = go.Figure()
        return [], [], empty_fig, empty_fig, fig

    clicked_iso = clickData["points"][0]["location"]
    country_df = df[df["iso_code"] == clicked_iso]

    if country_df.empty:
        empty_fig = go.Figure()
        return [], [], empty_fig, empty_fig, fig

    # Tabelle
    country_subset = country_df[list(COUNTRY_COLS.keys())].iloc[0]
    values = []
    for key, label in COUNTRY_COLS.items():
        val = country_subset[key]
        if pd.isnull(val):
            formatted = ""
        elif key in ["population", "gdp", "per_capita_electricity"]:
            formatted = f"{val:,.0f}"
        elif key == "net_elec_imports_share_demand":
            formatted = f"{val:.2f}"
        elif key == "risk_sum":
            formatted = f"{val:.0f}"
        else:
            formatted = val
        values.append(formatted)

    transposed = pd.DataFrame({
        "Attribute": list(COUNTRY_COLS.values()),
        "Value": values
    })

    data_table = transposed.to_dict("records")
    columns_table = [{"name": "Attribute", "id": "Attribute"},
                     {"name": "Value", "id": "Value"}]

    # Pie Chart
    elec_data = country_df[ELEC_COLS].mean()
    pie_fig = go.Figure(data=[go.Pie(
        labels=["Demand", "Generation"],
        values=[elec_data["electricity_demand"], elec_data["electricity_generation"]],
        marker_colors=["red", "green"],
        textinfo="label+percent"
    )])
    pie_fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))

    # Bar Chart
    mix = country_df[SOURCE_COLS].mean()
    bar_fig = go.Figure()
    for col in SOURCE_COLS:
        label, color = SOURCE_MAPPING[col]
        bar_fig.add_trace(go.Bar(
            x=[label],
            y=[mix[col]],
            marker_color=color
        ))
    bar_fig.update_layout(
        xaxis_title="Source",
        yaxis_title="Electricity Generation",
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20)
    )

    # World Map mit nur ausgewähltem Land
    df_selected = df.copy()
    df_selected["z"] = df_selected["iso_code"].apply(lambda iso: df.loc[df["iso_code"] == iso, "risk_sum"].values[0] if iso == clicked_iso else None)

    map_fig = go.Figure(go.Choropleth(
        locations=df_selected["iso_code"],
        z=df_selected["z"],
        text=df_selected["country"],
        hoverinfo="text+z",
        colorscale="RdYlGn_r",
        zmin=df["risk_sum"].min(),
        zmax=df["risk_sum"].max(),
        marker_line_width=0.5,
        locationmode="ISO-3",
        showscale=True,
        colorbar=dict(title="Risk Potential:", x=-0.1, thickness=10, len=0.6, tickfont=dict(size=10))
    ))

    map_fig.update_geos(
        fitbounds="locations",
        projection_scale=1,
        center=dict(lat=20, lon=0)
    )
    map_fig.update_layout(
        title="World Map of Energy Data 2022",
        margin=dict(l=10, r=10, t=30, b=10)
    )

    return data_table, columns_table, pie_fig, bar_fig, map_fig


if __name__ == "__main__":
    app.run(debug=True)
