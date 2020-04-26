import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import json
import pathlib
import flask

from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt
from app import server


app = dash.Dash(
    __name__, server = server, url_base_pathname = '/',
    meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)


# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicmV6YXRhbWEiLCJhIjoiY2s1M2l6Y3V0MDBnbjNlcmpkNnI2bG56NiJ9.q7lwXHHVHLyGJSn2MV8fPA"

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("Aurin").resolve()

# Melbourne POI Data
df1 = pd.read_csv(
    DATA_PATH.joinpath("Melb.csv")
)

# Melbourne Map Layer
with open(DATA_PATH.joinpath('median_age.json')) as json_file:
    median_age = json.load(json_file)
with open(DATA_PATH.joinpath('chronic_disease.json')) as json_file:
    chronic_disease = json.load(json_file)
with open(DATA_PATH.joinpath('mental_health.json')) as json_file:
    mental_health = json.load(json_file)
with open(DATA_PATH.joinpath('social_economic.json')) as json_file:
    social_economic = json.load(json_file)

base_layer = {'Median Age': median_age,
              'Chronic Disease': chronic_disease,
              'Mental Health': mental_health,
              'Social Economic': social_economic
              }

# Layout of Dash App
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for app graphs and plots
                html.Div(
                    className="nine columns div-for-charts bg-grey",
                    children=[
                        html.Div(
                            children=[
                                dcc.Graph(id="map-graph"),
                             ],
                            className="pretty_container",
                        ),
                    ]
                ),
                # Column for user controls
                html.Div(
                    className="three columns div-user-controls",
                    children=[
                        html.Img(
                            className="logo", src=app.get_asset_url("uom-logo.png")
                        ),
                        html.H2("MELBOURNE TWITTER DATA APP"),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        html.Label('Select base map layer:'),
                                        dcc.Dropdown(
                                            id="layer-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in base_layer
                                            ],
                                            placeholder="Select a base layer",
                                            value=[i for i in base_layer][0],
											clearable=False
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        html.Label('Select POI to show:'),
                                        dcc.Dropdown(
                                            id="points-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in df1["Industry (ANZSIC4) description"].unique()
                                            ],
                                            placeholder="Select a industry type",
                                        )
                                    ],
                                ),
                                html.Label('Map Style:'),
                                html.Div([dcc.RadioItems(id='mapstyle-radio',
                                                         options=[
                                                             {'label': 'Streets ',
                                                                 'value': 'streets'},
                                                             {'label': 'Dark ',
                                                              'value': 'dark'},
                                                             {'label': 'Light ',
                                                              'value': 'light'}
                                                         ],
                                                         value='dark'), ]),
                                html.Div(
                                    [html.Label('Layer Opacity:'),
                                    dcc.Slider(
                                    id='opacity-slider',
                                    min=0,
                                    max=1,
                                    value=0.5,
                                    marks={0: '0', 0.5: '0.5', 1: '1'},
                                    step=0.01,
                                    included=False
                                    ),
                                    ],
                                    className="div-for-slider"
                                )
                            ],
                        ),
                        dcc.Markdown(
                            children=[
                                "Source: [AURIN](https://aurin.org.au/)"
                            ]
                        ),
                    ],
                ),
            ],
        )
    ]
)

# MELB MAP
@app.callback(
    Output("map-graph", "figure"),
    [
        Input("layer-dropdown", "value"),
        Input("points-dropdown", "value"),
        Input("mapstyle-radio", "value"),
        Input("opacity-slider", "value")
    ],
)
def update_graph(selectedLayer, selectedIndustry, selectedStyle, selectedOpacity):
    zoom = 11.0
    latInitial = -37.8136
    lonInitial = 144.9631
    bearing = 0

    return go.Figure(
        data=[
            # Plot base layer
            go.Choroplethmapbox(geojson=base_layer[selectedLayer],
                                locations=[i['id']
                                           for i in base_layer[selectedLayer]['features']],
                                z=[i['properties']['values']
                                    for i in base_layer[selectedLayer]['features']],
                                colorscale='Viridis',
                                marker={'opacity': selectedOpacity},
                                text=[i['properties']['name']
                                      for i in base_layer[selectedLayer]['features']],
                                hovertemplate='<b>Suburb</b>: <b>%{text}</b>' +
                                '<br><b>'+selectedLayer+' </b>: %{z}<br>',
                                marker_line_width=0.1, 
                                colorbar=dict(
                title=selectedLayer,
                x=0.93,
                xpad=0,
                nticks=24,
                tickfont=dict(color="#d8d8d8"),
                titlefont=dict(color="#d8d8d8"),
                thicknessmode="pixels",
            ),
            ),
            # Plot POI
            Scattermapbox(
                lat=df1[df1["Industry (ANZSIC4) description"]
                        == selectedIndustry]["y coordinate"],
                lon=df1[df1["Industry (ANZSIC4) description"]
                        == selectedIndustry]["x coordinate"],
                mode="markers",
                hoverinfo="lat+lon+text",
                text=df1[df1["Industry (ANZSIC4) description"]
                         == selectedIndustry]["Trading name"],
            ),
         ],
        layout=Layout(
            autosize=True,
            margin=go.layout.Margin(l=0, r=35, t=0, b=0),
            showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                # 40.7272  # -73.991251
                center=dict(lat=latInitial, lon=lonInitial),
                style=selectedStyle,
                bearing=bearing,
                zoom=zoom,
            ),
            updatemenus=[
                dict(
                    buttons=(
                        [
                            dict(
                                args=[
                                    {
                                        "mapbox.zoom": 12,
                                        "mapbox.center.lon": "144.9631",
                                        "mapbox.center.lat": "-37.8136",
                                        "mapbox.bearing": 0,
                                        "mapbox.style": "dark",
                                    }
                                ],
                                label="Reset Zoom",
                                method="relayout",
                            )
                        ]
                    ),
                    direction="left",
                    pad={"r": 0, "t": 0, "b": 0, "l": 0},
                    showactive=False,
                    type="buttons",
                    x=0.45,
                    y=0.02,
                    xanchor="left",
                    yanchor="bottom",
                    bgcolor="#323130",
                    borderwidth=1,
                    bordercolor="#6d6d6d",
                    font=dict(color="#FFFFFF"),
                )
            ],
        ),
    )

if __name__ == '__main__':
    app.run_server(debug=True)
