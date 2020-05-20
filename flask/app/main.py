import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import pandas as pd
import numpy as np
import json
import pathlib
import flask
# import couchdb
# from geopy.distance import great_circle as gc
import requests

from dash.dependencies import Input, Output, State
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt
from app import server

from app.visualisation import plotly_bargraph
from app.transform import * 


app = dash.Dash(
    __name__, server = server, url_base_pathname = '/',
    meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

# Retrieve CouchDB Views
params = (
    ('reduce', 'true'),
    ('group', 'true'),
    ('include_docs', 'false'),
)
response = requests.get('http://45.113.235.78:5984/ui_db/_design/suburb/_view/suburb_view', params=params, auth=('admin', 'MGZjZGU5N'))
df_view = parse_view(response.json())

# '''
# This section is using different data on my personal instance.
# Its used for pressenting top 15 most frequent words
# Will remove this section after carlos provide raw tweet text on his DB
# '''
# # Connect couchdb
# user = "reza"
# password = "reza"
# couchserver = couchdb.Server("http://%s:%s@115.146.92.235:5984/" % (user, password))
# db = couchserver['db_test']
# # Get list of big cities in AU
# cap = pd.read_csv('/home/rezatama/Downloads/capital.csv')
# city = list(zip(cap['latitude'],cap['longitude']))
# # Get twit data
# lat_ = []
# lon_ = []
# lat_adj = []
# lon_adj= []
# text_ = []
# sntm_ = []
# for item in db.view('place/new-view'):
#     if not item.value[0]:
#         near_city=city[np.argmin([gc((item.key[1],item.key[0]),i).km for i in city])]
#         lat_adj.append(near_city[0])
#         lon_adj.append(near_city[1])
#     else:
#         lat_adj.append(item.key[1])
#         lon_adj.append(item.key[0])
#     lat_.append(item.key[1])
#     lon_.append(item.key[0])
#     text_.append(item.value[1])
#     sntm_.append(item.value[2])
# df_twit = pd.DataFrame({'Latitude':lat_,'Longitude':lon_,'Sentiment':sntm_})
# df_twit_grp = df_twit.groupby(['Latitude','Longitude'],
#     as_index=False).agg({'Sentiment':[('Sentiment Score','mean'),
#     ('Total Tweet','count')]})

# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicmV6YXRhbWEiLCJhIjoiY2s1M2l6Y3V0MDBnbjNlcmpkNnI2bG56NiJ9.q7lwXHHVHLyGJSn2MV8fPA"

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("Aurin").resolve()

# Melbourne Map Layer
with open(DATA_PATH.joinpath('median_age.json')) as json_file:
    median_age = json.load(json_file)
with open(DATA_PATH.joinpath('median_income.json')) as json_file:
    median_income = json.load(json_file)
with open(DATA_PATH.joinpath('mental_health.json')) as json_file:
    mental_health = json.load(json_file)
with open(DATA_PATH.joinpath('overseas_born.json')) as json_file:
    overseas_born = json.load(json_file)
with open(DATA_PATH.joinpath('employment_rate.json')) as json_file:
    employment_rate = json.load(json_file)

cap = pd.read_csv(DATA_PATH.joinpath('capital.csv'))

base_layer = {'Median Age': median_age,
              'Median Income': median_income,
              'Mental Health': mental_health,
              'Overseas-born Rate': overseas_born,
              'Employment Rate': employment_rate
              }

# Layout of Dash App
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="three columns bg-white",
                    children=[
                        dcc.Graph(id="bargraph",
                                  config={'displayModeBar': False}),
                        daq.Gauge(
                            id="sentiment-gauge",
                            style={
                                'margin-bottom': -15 
                            },
                            color="#1F77B4",
                            label={
                                  'label': 'Average Sentiment Score',
                                  'style': {
                                      'fontSize': 18
                                  }},
                            value=0,
                            max=1.0,
                            min=-1.0,
                            showCurrentValue=True
                        ),
                        daq.LEDDisplay(
                        id="tweet-led",
                        label={
                                  'label': 'Total Tweets',
                                  'style': {
                                      'fontSize': 18
                                  }},
                        value="0",
                        color="#1F77B4",
                        size=45,
                        ),            
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="seven columns bg-grey",
                    children=[
                        dcc.Loading(id = "loading-icon1", 
                        children=[dcc.Graph(id="map-graph")],
                        type='circle')
                    ],
                ),
                # Column for user controls
                html.Div(
                    className="two-half columns div-user-controls",
                    children=[
                        html.Img(
                            className="logo", src=app.get_asset_url("uom-logo.png")
                        ),
                        html.H2("TWITTER DATA EXPLORER"),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        html.Label('Select Topic:'),
                                        dcc.Dropdown(
                                            id="topic-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in df_view.topic.unique().tolist()+['All']
                                            ],
                                            placeholder="Select Topic",
                                            value='All',
											clearable=False
                                        ),
                                        html.Label('Select regional statistic:'),
                                        dcc.Dropdown(
                                            id="layer-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in base_layer
                                            ],
                                            placeholder="Select a base layer",
                                            value=[i for i in base_layer][0],
											clearable=False
                                        ),
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        html.Label('Filter Year:'),
                                        dcc.Dropdown(
                                            id="year-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in df_view.year.unique().tolist()+['All']
                                            ],
                                            placeholder="Select year",
                                            value='All',
											clearable=False
                                        ),
                                        html.Label('Grouping Level:'),
                                        dcc.Dropdown(
                                            id="grouping-dropdown",
                                            options=[
                                                {'label':'State' ,'value':'state'},
                                                {'label':'County' ,'value':'county'},
                                                {'label': 'City','value':'city'},
                                                {'label': 'Suburb','value':'suburb'},
                                                {'label': 'None','value':'None'}
                                            ],
                                            placeholder="Select sentiment",
                                            value='None',
											clearable=False
                                        )
                                    ],
                                ),
                                html.Label('Map Style:'),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                    dcc.RadioItems(id='mapstyle-radio',
                                                         options=[
                                                             {'label': 'Streets ',
                                                                 'value': 'streets'},
                                                             {'label': 'Dark ',
                                                              'value': 'dark'},
                                                             {'label': 'Light ',
                                                              'value': 'light'}
                                                         ],
                                                         value='streets',
                                                         labelStyle={'display': 'inline-block'}
                                                         )]),
                                html.Div(id='view-data', style={'display': 'none'}),
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

@app.callback(
    Output('view-data','children'),
    [Input("year-dropdown", "value"),
    Input("topic-dropdown", "value"),
    Input("grouping-dropdown", "value")]
)
def filter_data(selectedYear, selectedTopic, selectedGrouping):
    df = filter_view(df_view,selectedYear,selectedTopic,selectedGrouping)
    df = df[df.iloc[:,0]!='']
    data = df.to_json(orient='split')
    return data

# MELB MAP
@app.callback(
    Output("map-graph", "figure"),
    [
        Input('view-data','children'),
        Input("layer-dropdown", "value"),
        Input("mapstyle-radio", "value")
    ],
)
def update_graph(jsonified_data, selectedLayer, selectedStyle):
    zoom = 3.7
    latInitial = -25.2744
    lonInitial = 133.7751
    bearing = 0
    colours ='#ffffff' if selectedStyle=='dark' else '#000000'
    df = pd.read_json(jsonified_data, orient='split')
    return go.Figure(
        data=[
            # Plot base layer
            go.Choroplethmapbox(geojson=base_layer[selectedLayer],
                                locations=[i['id']
                                           for i in base_layer[selectedLayer]['features']],
                                z=[str(i['properties']['values'])
                                    for i in base_layer[selectedLayer]['features']],
                                colorscale='Portland',
                                marker={'opacity': 0.6},
                                text=[i['properties']['name']
                                      for i in base_layer[selectedLayer]['features']],
                                hovertemplate='<b>Suburb</b>: <b>%{text}</b>' +
                                '<br><b>'+selectedLayer+' </b>: %{z}<br>',
                                marker_line_color=colours, 
                                name = 'Regional Statistic',
                                colorbar=dict(
                title=selectedLayer,
                x=0.01,
                xpad=0,
                nticks=5,
                tickfont=dict(color=colours),
                titlefont=dict(color=colours),
                thicknessmode="pixels"),
            ),
            Scattermapbox(
            lat=df.lat ,
            lon=df.lon ,
            mode="markers",
            customdata=df.filter(regex='pct$|count$', axis=1).sort_index(axis=1).to_numpy(),
            text=df.iloc[:,0],
            hovertemplate='<b>'+df.columns[0].title() +' </b>: %{text} <br>' +
                         '<br><b>Positive Sentiment</b>: %{customdata[3]} % ' +
                         '<br><b>Negative Sentiment</b>: %{customdata[1]} % ' +
                         '<br><b>Neutral Sentiment</b>: %{customdata[2]} % ',
            marker_color="#FF1818",
            marker_size=np.log1p(df['count'])*10,
            name = 'Tweet Stats'
            )
         ],
        layout=Layout(
            autosize=True,
            margin=go.layout.Margin(l=0, r=0, t=0, b=0),
            showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(lat=latInitial, lon=lonInitial),
                style=selectedStyle,
                bearing=bearing,
                zoom=zoom,
            ),
            uirevision=True,
            updatemenus=[
                dict(
                    active=0,
                    x=0.85,
                    y=0.02,
                    xanchor="left",
                    yanchor="bottom",
                    direction="up",
                    borderwidth=1,
                    buttons=[city_dropdown(cap.iloc[i,0],
                    cap.iloc[i,1],
                    cap.iloc[i,2],
                    cap.iloc[i,3]) for i in range(cap.shape[0])]
                )
            ],
        ),
    )

# @app.callback(
#     Output("bargraph", "figure"),
#     [Input("map-graph","selectedData")]
# )
# def update_bargraph_plot(idx):
#     """ Callback to rerender bargraph plot """
#     if idx is None:
#         bargraph = plotly_bargraph(text_)
#     else:
#         index = [i["pointIndex"] for i in idx["points"] if i["curveNumber"]==1]
#         bargraph = plotly_bargraph(np.array(text_)[index])
#     return(bargraph)

@app.callback(
    output=Output("sentiment-gauge", "value"),
    inputs=[Input("view-data","children"),
            Input("map-graph","hoverData")],
)
def update_gauge(jsonified_data,idx):
    if idx is None:
        return df_view["avg_sentiment"].mean()
    if idx["points"][0]["curveNumber"]==1:
        index = idx["points"][0]["pointIndex"] 
    df = pd.read_json(jsonified_data, orient='split')
    value = df.iloc[index]["avg_sentiment"]
    return value

@app.callback(
    output=Output("tweet-led", "value"),
    inputs=[Input("view-data","children"),
            Input("map-graph","hoverData")],
)
def update_led(jsonified_data,idx):
    if idx is None:
        return df_view["count"].sum()
    if idx["points"][0]["curveNumber"]==1:
        index = idx["points"][0]["pointIndex"] 
    df = pd.read_json(jsonified_data, orient='split')
    value = df.iloc[index]["count"]
    return value

if __name__ == '__main__':
    app.run_server(debug=True)
