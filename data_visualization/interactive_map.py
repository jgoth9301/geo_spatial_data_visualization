import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, dash_table, Output, Input
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

# Map Figure
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
        dbc.Col([
            dbc.Row([
                dcc.Graph(id="world-map", figure=fig, style={"height": "50vh", "width": "100%"})
            ]),
            dbc.Row([
                html.H5("Electricity Mix"),
                dcc.Graph(id="source-bar", style={"height": "45vh"})
            ])
        ], width=8),  # 8 von 12 → ca. 70 %
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
        ], width=4)  # 4 von 12 → ca. 30 %
    ])
], fluid=True, style={"height": "100vh", "padding": "10px"})


# Callback
@app.callback(
    [Output("country-table", "data"),
     Output("country-table", "columns"),
     Output("demand-pie", "figure"),
     Output("source-bar", "figure")],
    [Input("world-map", "clickData")]
)
def update_tables(clickData):
    if clickData:
        clicked_iso = clickData["points"][0]["location"]
        country_df = df[df["iso_code"] == clicked_iso]

        if not country_df.empty:
            # Country Data
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

            data_table = transposed.to_dict('records')
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
            pie_fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20)
            )

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

            return data_table, columns_table, pie_fig, bar_fig

    # Default empty
    empty_fig = go.Figure()
    return [], [], empty_fig, empty_fig


if __name__ == "__main__":
    app.run(debug=True)
