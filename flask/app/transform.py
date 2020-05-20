import numpy as np
import pandas as pd

def parse_view(view):
    year = [i['key'][0] for i in view['rows']]
    topic = [i['key'][1] for i in view['rows']] 
    sentiment = [i['key'][2] for i in view['rows']] 
    city =  [i['key'][3]['city'] if 'city' in i['key'][3].keys() else '' for i in view['rows']] 
    suburb =  [i['key'][3]['suburb'] if 'suburb' in i['key'][3].keys() else '' for i in view['rows']] 
    county =  [i['key'][3]['county'] if 'county' in i['key'][3].keys() else '' for i in view['rows']] 
    state =  [i['key'][3]['state'] if 'state' in i['key'][3].keys() else '' for i in view['rows']] 
    lat =  [i['key'][3]['lat']for i in view['rows']]
    lon =  [i['key'][3]['lon']for i in view['rows']]
    count = [i['value'] for i in view['rows']]
    df = pd.DataFrame({
             'suburb':suburb,
             'city':city,
             'county':county,
             'state':state,
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

def filter_view(df,year='All',topic='All',grouping='None'):
    df1 = df.copy()
    if year!='All':
        df=df.loc[df.year==year]
    if topic!='All':
        df=df.loc[df.topic==topic]
    if grouping!='None':
        df=df.groupby(grouping) \
              .apply(lambda x: pd.Series({
                  'lat'       : x['lat'].mean(),
                  'lon'       : x['lon'].mean(),
                  'count'      : x['count'].sum(),
                  'avg_sentiment'  : x['avg_sentiment'].mean(),
                  'pos_sentiment_pct': np.round(sum(x['avg_sentiment']==1)/x.shape[0]*100,2),
                  'neg_sentiment_pct': np.round(sum(x['avg_sentiment']==-1)/x.shape[0]*100,2),
                  'neu_sentiment_pct': np.round(sum(x['avg_sentiment']==0)/x.shape[0]*100,2)
              })
            ).reset_index()
    return df

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