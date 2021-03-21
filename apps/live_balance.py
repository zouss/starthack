import dash
import wapi
import pandas as pd
import numpy as np
from scipy.stats import norm
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output, State
import plotly.express as px
import datetime as dt

from app import app

config_file_path = './/configfile.ini'
session = wapi.Session(config_file=config_file_path)


actual_consumption = session.get_curve(name='con de mwh/h cet min15 a').get_data(data_from='2021-03-20T00:00Z', data_to='2021-03-23T00:00Z').to_pandas().rename('act')
forcast_consumption = session.get_curve(name='con de ec00 mwh/h cet min15 f').get_latest(data_from='2021-03-20T12:00Z').to_pandas().rename('fct')[:100]
forcast_consumption = pd.merge(forcast_consumption, actual_consumption, how='outer', left_index=True, right_index=True)
forcast_consumption = forcast_consumption[forcast_consumption['act'].isnull()]['fct']

production_dict = {
    'Nuc': {'actual': 'pro de nuc mwh/h cet h af', 'forecast': 'cap de nuc mw cet h af'},
    'Hydro': {'actual': 'pro de hydro tot mwh/h cet h af', 'forecast': 'pro de hydro tot mwh/h cet h af'},
    'Solar':  {'actual': 'pro de spv mwh/h cet min15 a', 'forecast': 'pro de spv ec00 mwh/h cet min15 f'},
    'Wind':  {'actual': 'pro de wnd mwh/h cet min15 a', 'forecast': 'pro de wnd ec00 mwh/h cet min15 f'},
    'Gas':  {'actual': 'pro de thermal gas mwh/h cet min15 a', 'forecast': 'cap de avail thermal gas mw cet h f'},
    'Lignite':  {'actual': 'pro de thermal lignite mwh/h cet min15 a', 'forecast': 'cap de avail thermal lignite mw cet h f'},
    'Coal': {'actual': 'pro de thermal coal mwh/h cet min15 a', 'forecast': 'cap de avail thermal coal mw cet h f'},
}

production = pd.DataFrame()
for source in production_dict.keys():
    df = session.get_curve(name=production_dict[source]['actual']).get_data(data_from='2021-03-20T00:00Z', data_to='2021-03-21T00:00Z').to_pandas()
    production = pd.concat([production, df.to_frame(source)], verify_integrity=True, axis=1)
production['Nuc'] = production['Nuc'].fillna(method='ffill')
production['Hydro'] = production['Hydro'].fillna(method='ffill')
production = production.dropna(subset=['Coal', 'Solar', 'Wind', 'Gas', 'Lignite'], how='all')


production_ft = pd.DataFrame()
for source in production_dict.keys():
    if source in ['Nuc', 'Hydro']:
        df = session.get_curve(name=production_dict[source]['forecast']).get_data(data_from='2021-03-20T00:00Z', data_to='2021-03-22T00:00Z').to_pandas()
    else:
        df = session.get_curve(name=production_dict[source]['forecast']).get_latest(data_from='2021-03-20T12:00Z').to_pandas()
    production_ft = pd.concat([production_ft, df.to_frame(source)], verify_integrity=True, axis=1)
production_ft = production_ft.fillna(method='ffill')[:100]


layout = {
    'barmode': 'stack'
}
data = [
    go.Scatter(x=actual_consumption.index, y=actual_consumption, name='Consumption', line={'color': px.colors.qualitative.Plotly[0]}),
    go.Scatter(x=forcast_consumption.index, y=forcast_consumption, name='Consumption (f)', line={'dash': 'dash', 'color': px.colors.qualitative.Plotly[0]}, showlegend=False),
]

for i, col in enumerate(production.columns):
    trace = go.Bar(
        x=production.index, 
        y=production[col], 
        name='Production {}'.format(col),
        marker_color=px.colors.qualitative.Plotly[i]
    )
    data.append(trace)

    fct = pd.merge(production_ft[col], production[col], how='outer', left_index=True, right_index=True, suffixes=('_f', '_a'))
    fct = fct[fct[col+'_a'].isnull()][col+'_f']
    trace = go.Bar(
        x=fct.index, 
        y=fct, 
        name='Production {}'.format(col),
        marker_color=px.colors.qualitative.Plotly[i],
        opacity=0.3,
        showlegend=False
    )
    data.append(trace)


fig = go.Figure(data=data, layout=layout)


layout = html.Div(
    [
        dcc.Graph(figure=fig)
    ]
)