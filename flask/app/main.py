import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import pandas as pd
import numpy as np
import json
import pathlib
import flask
import re

from dash.dependencies import Input, Output, State
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt
from app import server
from flask_caching import Cache

from app.visualisation import plotly_bargraph
from app.transform import * 
from app.config import COUCHDB_URL, COUCHDB_USER, COUCHDB_PASSWORD


app = dash.Dash(
    __name__, server = server, url_base_pathname = '/',
    meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

# Set cache timeout for 30 mins
TIMEOUT = 1800

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
              'Mental Health \n(Hospitalisation per 10,000 people)': mental_health,
              'Overseas-born Rate': overseas_born,
              'Employment Rate': employment_rate,
              'None': None
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
                        dcc.Loading(id = "loading-icon0", 
                        children=[dcc.Graph(id="bargraph",
                                  config={'displayModeBar': False})],
                        type='circle'),
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
                        children=[dcc.Graph(id="map-graph",
                                    clear_on_unhover = True)],
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
                                        html.Label('Select Social, Health & Financial Measure:'),
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
                                        # html.P("Statistic Description:"),
                                        # html.P(id="stat-info"),
                                        html.Label('Select Topic for Sentiment Analysis:'),
                                        dcc.Dropdown(
                                            id="topic-dropdown",
                                            placeholder="Select Topic",
                                            value=[2],
											clearable=False,
                                            multi=True
                                        ),
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        html.Label('Filter Year:'),
                                        dcc.Dropdown(
                                            id="year-dropdown",
                                            placeholder="Select year",
                                            value=2020,
											clearable=False
                                        ),
                                        # dcc.Store(id='local', storage_type='local')
                                        dcc.Loading(id = "loading-icon2", 
                        children=[html.Div(id='rawview-data', style={'display': 'none'})],
                        type='circle'),
                                        html.Label('Grouping Level:'),
                                        dcc.Dropdown(
                                            id="precision-dropdown",
                                            options=[
                                                {'label':'Country' ,'value':'country'},
                                                {'label':'State' ,'value':'state'},
                                                {'label':'County' ,'value':'county'},
                                                {'label': 'City','value':'city'},
                                                {'label': 'Suburb','value':'suburb'}
                                            ],
                                            placeholder="Select sentiment",
                                            value='county',
											clearable=False
                                        ),
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
                                                         dcc.Loading(id = "loading-icon3", 
                        children=[dcc.Store(id='view-data', storage_type='local')],
                        type='circle'),
                            ],
                        ),
                        dcc.Markdown(
                            children=[
                                "Source: [AURIN](https://aurin.org.au/), [Twitter](https://twitter.com/)"
                            ]
                        ),
                    ],
                ),
            ],
        )
    ]
)

@app.callback(
     Output('rawview-data','children'),
    [Input("precision-dropdown","value")]
)
@cache.memoize(timeout=TIMEOUT)
def get_data(selectedPrecision):
    data = get_view(selectedPrecision)
    return data.to_json(orient='split')

@app.callback(
    Output('topic-dropdown', 'options'),
    [Input("rawview-data",'children'),])
def set_topic_options(jsonified_rawdata):
    topic_map = {0:"General",1:"Covid APP",2:"Politics",3:"Politics & Covid APP"}
    df_view = pd.read_json(jsonified_rawdata, orient='split')
    return [{"label": topic_map.get(i,i), "value": i}
        for i in df_view.topic.unique().tolist()+['All']]

@app.callback(
    Output('year-dropdown', 'options'),
    [Input("rawview-data",'children'),])
def set_year_options(jsonified_rawdata):
    df_view = pd.read_json(jsonified_rawdata, orient='split')
    return [{"label": i, "value": i}
         for i in df_view.year.unique().tolist()+['All']]

@cache.memoize(timeout=TIMEOUT)
def filter_view(df,year='All',topic='All',grouping='None'):
    if year!='All':
        df=df.loc[df.year==year]
    if topic!='All' and 'All' not in topic:
        df=df.loc[df.topic.isin(topic)]
    if grouping!='None':
        df=df.groupby(grouping,observed=True) \
              .apply(lambda x: pd.Series({
                  'lat'       : x['lat'].mean(),
                  'lon'       : x['lon'].mean(),
                  'count'      : x['count'].sum(),
                  'avg_sentiment'  : x['avg_sentiment'].mean(),
                  'pos_sentiment_pct': "{:0.2f}".format(sum(x['avg_sentiment']==1)/x.shape[0]*100),
                  'neg_sentiment_pct': "{:0.2f}".format(sum(x['avg_sentiment']==-1)/x.shape[0]*100),
                  'neu_sentiment_pct': "{:0.2f}".format(sum(x['avg_sentiment']==0)/x.shape[0]*100)
              })
            ).reset_index()
    return df

@app.callback(
    Output('view-data','data'),
    [Input("rawview-data",'children'),
    Input("year-dropdown", "value"),
    Input("topic-dropdown", "value"),
    Input("precision-dropdown", "value")]
)
def filter_data(jsonified_rawdata, selectedYear, selectedTopic, selectedGrouping):
    df_view = pd.read_json(jsonified_rawdata, orient='split')
    df = filter_view(df_view,selectedYear,selectedTopic,selectedGrouping)
    data = df.to_json(orient='split')
    return data

@cache.memoize(timeout=TIMEOUT)
def get_scatter(df):
    scatter = Scattermapbox(
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
    return [scatter]

# MELB MAP
@app.callback(
    Output("map-graph", "figure"),
    [
        Input('view-data','data'),
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
    regstat = [go.Choroplethmapbox(geojson=base_layer[selectedLayer],
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
        )] if selectedLayer!='None' else []
    return go.Figure(
        data = regstat + get_scatter(df),
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

@cache.memoize(timeout=TIMEOUT)
def get_text():
    params = (
                ('reduce', 'false'),
                ('group', 'false'),
                ('include_docs', 'false'),
             )
    response = requests.get(f'{COUCHDB_URL}/ui_db/_design/a/_view/new-view', params=params, auth=(COUCHDB_USER, COUCHDB_PASSWORD))
    return response

@app.callback(
    Output("bargraph", "figure"),
    [Input("topic-dropdown","value")]
)
def update_bargraph_plot(topics):
    """ Callback to rerender bargraph plot """
    response = get_text()
    if "All" in topics:
        text_ = "".join([i["value"].lower() for i in response.json()["rows"] if i["key"]])
    else:
        text_ = "".join([i["value"].lower() for i in response.json()["rows"] if i["key"] in topics])
    pattern = '(#[\w\u0E00-\u0E7F]+)'
    hashtags = re.findall(pattern,text_)
    bargraph = plotly_bargraph(" ".join(hashtags))
    return(bargraph)

@app.callback(
    output=Output("sentiment-gauge", "value"),
    inputs=[Input("view-data","data"),
            Input("map-graph","hoverData")],
)
def update_gauge(jsonified_data,idx):
    df = pd.read_json(jsonified_data, orient='split')
    if idx is None:
        return df["avg_sentiment"].mean()
    if idx["points"][0]["curveNumber"]==1:
        index = idx["points"][0]["pointIndex"] 
        value = df.iloc[index]["avg_sentiment"]
        return value

@app.callback(
    output=Output("tweet-led", "value"),
    inputs=[Input("view-data","data"),
            Input("map-graph","hoverData")],
)
def update_led(jsonified_data,idx):
    df = pd.read_json(jsonified_data, orient='split')
    if idx is None:
        return df["count"].sum()
    if idx["points"][0]["curveNumber"]==1:
        index = idx["points"][0]["pointIndex"] 
    value = df.iloc[index]["count"]
    return value

if __name__ == '__main__':
    app.run_server(debug=True)
