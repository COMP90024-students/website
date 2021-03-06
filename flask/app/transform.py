import numpy as np
import pandas as pd
import requests

from app.config import COUCHDB_URL, COUCHDB_USER, COUCHDB_PASSWORD


def parse_view(view):
    year = [i['key'][0] for i in view['rows']]
    topic = [i['key'][1] for i in view['rows']] 
    sentiment = [i['key'][2] for i in view['rows']] 
    city =  [i['key'][3]['city'] if 'city' in i['key'][3].keys() else '' for i in view['rows']] 
    suburb =  [i['key'][3]['suburb'] if 'suburb' in i['key'][3].keys() else '' for i in view['rows']] 
    county =  [i['key'][3]['county'] if 'county' in i['key'][3].keys() else '' for i in view['rows']] 
    state =  [i['key'][3]['state'] if 'state' in i['key'][3].keys() else '' for i in view['rows']] 
    country =  [i['key'][3]['country'] if 'country' in i['key'][3].keys() else '' for i in view['rows']] 
    lat =  [i['key'][3]['lat']for i in view['rows']]
    lon =  [i['key'][3]['lon']for i in view['rows']]
    count = [i['value'] for i in view['rows']]
    df = pd.DataFrame({
             'suburb':suburb,
             'city':city,
             'county':county,
             'state':state,
             'country':country,
             'year':year,
             'topic':topic,
             'avg_sentiment':sentiment,
             'pos_sentiment_pct': [100 if i==1 else 0 for i in sentiment],
             'neg_sentiment_pct': [100 if i==-1 else 0 for i in sentiment],
             'neu_sentiment_pct': [100 if i==0 else 0 for i in sentiment],
             'lat':lat,
             'lon':lon,
             'count':count})
    return df

def get_view(precision):
    params = (
        ('reduce', 'true'),
        ('group', 'true'),
        ('include_docs', 'false'),
    )
    response = requests.get(f'{COUCHDB_URL}/ui_db/_design/'+precision+'/_view/'+precision+'_view', params=params, auth=(COUCHDB_USER, COUCHDB_PASSWORD))
    return parse_view(response.json())

def city_dropdown(lon,lat,city,zoom):
    return dict(args=[
                       {
                        "mapbox.zoom": zoom,
                        "mapbox.center.lon": lon,
                        "mapbox.center.lat": lat,
                       }
                     ],
                     label=city,
                     method="relayout")
