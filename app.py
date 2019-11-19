# -*- coding: utf-8 -*-
"""
Created on Sat Nov  9 14:48:39 2019

@author: Administrator
"""
import os
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import requests
import reverse_geocoder as rg
import folium

pd.options.display.max_columns = 500

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import time

base_url = "https://api.waqi.info/map/bounds/?latlng="
lat1 = -90
lon1 = -180
lat2 = 90
lon2 = 180

api_access_key = os.getenv("API_ACCESS_KEY")
url = base_url+str(lat1)+","+str(lon1)+","+str(lat2)+","+str(lon2)+"&token="+api_access_key

countries = pd.read_csv('country_codes.csv')
countries = countries[['name', 'country-code']]
countries.rename(columns = {'name': 'label', 'country-code': 'value'}, inplace = True)

options = list(countries.T.to_dict().values())
options[153]['value']='NAM'

coordinates = (20.5937, 78.9629)
tiles='CartoDB dark_matter'
folium_map = folium.Map(location = coordinates, tiles = tiles, width='100%', height='100%', zoom_start = 4, prefer_canvas = True)


backgroundColor = '#1E2730'
color = '#fec036'


app = dash.Dash(__name__)
server = app.server

#Main-Panel-Layout

dashboard_title = html.Div(
                            id = "dashboard-title",
                            children = [
                                        html.H1('Air Quality Index (AQI)')
                                        ]
                           )

aqi_map = html.Div(
                    id = "folium-map-wrapper",
                    children = [
                                html.Iframe(
                                            id = 'folium-map',
                                            srcDoc = folium_map._repr_html_(),
                                            ),
                                ],
                    )

#Side-Panel-Layout

country_dropdown_text = html.H2(
                               id = "country-dropdown-text",
                               children = ["Select a country",
                                           html.Br()]
                               )

country_dropdown = html.Div(
                            id = "country-dropdown",
                            children = [
                                        dcc.Dropdown(
                                                    id = "country-dropdown-component",
                                                    options = options,
                                                    clearable = False,
                                                    value = "IN",
                                                    multi = False
                                                    ),
                                        html.Br()
                                        ],
                            )


n_locations = html.Div(
                       id = "control-panel-locations",
                       children = [
                                   daq.LEDDisplay(
                                               id = "control-panel-locations-component",
                                               value = "0",
                                               label = "# Locations",
                                               size = 25,
                                               color = "#fec036",
                                               backgroundColor = "#2b2b2b"
                                               ),
                                    html.Br()
                                    ],
                        n_clicks = 0,
                        )
                        
max_aqi = html.Div(
                   id = "control-panel-max-aqi",
                   children = [
                               daq.LEDDisplay(
                                           id = "control-panel-maxaqi-component",
                                           value = "0",
                                           label = "AQI_Max",
                                           size = 25,
                                           color = "#fec036",
                                           backgroundColor = "#2b2b2b"
                                           ),
                                       html.Br()
                                   ],
                   n_clicks = 0,
                   )
                   
min_aqi = html.Div(
                   id = "control-panel-min-aqi",
                   children = [
                               daq.LEDDisplay(
                                           id = "control-panel-minaqi-component",
                                           value = "0",
                                           label = "AQI_Min",
                                           size = 25,
                                           color = "#fec036",
                                           backgroundColor = "#2b2b2b"
                                           ),
                                       html.Br()
                                   ],
                   n_clicks = 0,
                   )
                   
utc = html.Div(
               id="control-panel-utc",
               children=[
               daq.LEDDisplay(
                             id="control-panel-utc-component",
                             value="16:23",
                             label="Time",
                             size=25,
                             color="#fec036",
                             backgroundColor="#2b2b2b"
                             )
                        ],
                n_clicks=0,
                )
          
side_panel_layout = html.Div(
                            id = "side-panel",
                            children = [
                                        html.Div("*Powered by waqi.info"),
                                        country_dropdown_text,
                                        country_dropdown,
                                        html.Div(
                                                id = "aqi-summary",
                                                children = [
                                                            n_locations,
                                                            max_aqi,
                                                            min_aqi,
                                                            utc
                                                            ]
                                                )
                                        ]
                            )

main_panel_layout = html.Div(
                            id = "upper-lower-panel",
                            children = [
                                        dashboard_title,
                                        aqi_map
                                        ]
                            )

app.layout = html.Div(
                      id = "root",
                      children = [
                                  dcc.Store(id = "memory-output"),
                                  side_panel_layout,
                                  main_panel_layout,
                                  dcc.Interval(
                                              id = 'interval-component',
                                              interval = 1*120000,
                                              n_intervals = 0
                                              ),
                                  ],
                      )

                     
@app.callback(Output('memory-output', 'data'),
              [Input('country-dropdown-component', 'value'),
               Input('interval-component', 'n_intervals')])
def update_filter_data(country, n):
    df = pd.DataFrame(requests.get(url).json()['data'])
    station = json_normalize(df['station'])
    df.drop(['station'], axis = 1, inplace = True)
    df = pd.concat([df, station], axis = 1)
    df.drop(['time'], axis = 1, inplace = True)
    location = rg.search(list(zip(df.lat, df.lon)))
    df['coordinates'] = location
    df['location'] = df['coordinates'].apply(lambda x: x['name'])
    df['cc'] = df['coordinates'].apply(lambda x: x['cc'])
    df.drop(['coordinates','name', 'uid'], axis = 1, inplace = True)
    df = df.merge(countries, how = "inner", left_on = "cc", right_on = "value")
    df.rename(columns = {'label': 'country'}, inplace = True)
    df.drop(['value'], axis = 1, inplace = True)
    df.aqi.replace('-',np.NaN, inplace = True)
    df.dropna(axis = 0, inplace = True)
    df['aqi'] = pd.to_numeric(df['aqi'])
    df['marker_color'] = pd.cut(df['aqi'], [0,50,100,150,200,300,df['aqi'].max()], labels=['green', 'yellow', 'orange', 'red', 'purple', 'brown'])
    df['country'] = df['country'].apply(lambda x: 'USA' if (x=='United States of America') else x)
    df = df[df['cc']==country]
    df.reset_index(drop = True, inplace = True)
    return df.to_dict('records')


@app.callback(Output('folium-map', 'srcDoc'),
              [Input('interval-component', 'n_intervals'),
               Input('memory-output', 'data')])
def update_map(n, data):
    data = pd.DataFrame(data)
    try:
        lat_max = data['lat'].max()
        lat_min = data['lat'].min()
        lon_max = data['lon'].max()
        lon_min = data['lon'].min()
        if len(data):
            latc = np.mean([lat_min, lat_max])
            lonc = np.mean([lon_min, lon_max])
            coordinates = (latc, lonc)
        else:
            coordinates = (0,0)
        #width='100%', height='100%', 
        folium_map = folium.Map(location = coordinates, tiles = tiles, zoom_start = 4, prefer_canvas = True)  #, tiles='CartoDB dark_matter'
        for index, row in data.dropna().iterrows():
            popup_text = "{}<br> Location: {:}".format(
                              row['aqi'],
                              row["location"]
                              )
            test = folium.Html(popup_text, script=True)
            popup = folium.Popup(test, max_width=300,min_width=100)
            folium.CircleMarker(location=[row["lat"],row["lon"]],
                                radius= 8,
                                color=row['marker_color'],
                                popup=popup,
                                fill=True).add_to(folium_map)
        return folium_map._repr_html_()
    except:
        raise PreventUpdate
        

@app.callback(Output('control-panel-locations-component', 'value'),
              [Input('interval-component', 'n_intervals'),
               Input('memory-output', 'data')])
def update_n_locations(n, data):
    return len(data)


@app.callback(Output('control-panel-maxaqi-component', 'value'),
              [Input('interval-component', 'n_intervals'),
               Input('memory-output', 'data')])
def update_max_aqi(n, data):
    try:
        return pd.DataFrame(data)['aqi'].max()
    except:
        raise PreventUpdate


@app.callback(Output('control-panel-minaqi-component', 'value'),
              [Input('interval-component', 'n_intervals'),
               Input('memory-output', 'data')])
def update_min_aqi(n, data):
    try:
        return pd.DataFrame(data)['aqi'].min()
    except:
        raise PreventUpdate


@app.callback(Output("control-panel-utc-component", "value"),
              [Input("interval-component", "n_intervals")])
def update_time(interval):
    hour = time.localtime(time.time())[3]
    hour = str(hour).zfill(2)

    minute = time.localtime(time.time())[4]
    minute = str(minute).zfill(2)
    return hour + ":" + minute


if __name__ == '__main__':
    app.run_server(debug=True)