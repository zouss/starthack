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



voluo_ids = {
    'solar': {
        'forecast': 'pro de spv ec00 mwh/h cet min15 f',
        'actual': 'pro de spv mwh/h cet min15 a',
        'normal': 'pro de spv mwh/h cet min15 n',
        'code': 'spv'
    },
    'wind': {
        'forecast': 'pro de wnd ec00 mwh/h cet min15 f',
        'actual': 'pro de wnd mwh/h cet min15 a',
        'normal': 'pro de wnd mwh/h cet min15 n',
        'code': 'wnd'
    }
}


dropdown_items = [
    dbc.DropdownMenuItem("Solar", id='dd-spv'),
    dbc.DropdownMenuItem("Wind", id='dd-wnd'),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Price", id='dd-prices'),
]


layout = html.Div(
    [
        dbc.DropdownMenu(
            dropdown_items,
            label='Time Series',
            id='main-dd'
        ),
        dcc.Graph(
            id='first-graph'
        ),
        dcc.Graph(
            id='main-graph'
        )
    ]
)


@app.callback(
    [
        Output('main-dd', 'label'),
        Output("first-graph", "figure"),
        Output("main-graph", "figure")
    ], 
    [
        Input("dd-spv", "n_clicks"),
        Input("dd-wnd", "n_clicks")
    ]
)
def count_clicks(*args):
    dic = {
        'spv': 'solar',
        'wnd': 'wind'
    }

    ctx = dash.callback_context
    selected_code = ctx.triggered[0]['prop_id'].split('.')[0].split('-')[1]
    selected = dic[ctx.triggered[0]['prop_id'].split('.')[0].split('-')[1]]
    

    forecast_curve = session.get_curve(name=voluo_ids[selected]['forecast'])
    forecast = forecast_curve.get_latest().to_pandas()
    forecast.name = 'forecast'
    forecast_min_date, forecast_max_date = forecast.index.min(),  forecast.index.max()

    nomral_curve = session.get_curve(name=voluo_ids[selected]['normal'])
    normal_ts = nomral_curve.get_data(data_from=forecast_min_date, data_to=forecast_max_date)
    normal = normal_ts.to_pandas()
    normal.name = 'normal'

    forecast_df = pd.merge(forecast, normal, left_index=True, right_index=True)
    forecast_df['diff'] = forecast_df['forecast'] - forecast_df['normal']


    layout = {
        'height': 800
    }

    fig = go.Figure(layout=layout)

    subs = make_subplots(
        rows=2,
        cols=2,
        shared_xaxes=True,
        shared_yaxes=True,
        column_widths=[0.7, 0.3],
        figure=fig
    )


    subs.add_trace(go.Scatter(y=forecast_df['normal'], x=forecast_df['normal'].index, name='Normal'), row=1, col=1)
    subs.add_trace(go.Scatter(y=forecast_df['forecast'], x=forecast_df['forecast'].index, name='Forecast'), row=1, col=1)

    mask = forecast_df['diff'] >= 0
    subs.add_trace(go.Scatter(x=forecast_df[mask].index, y=forecast_df[mask]['diff'],  mode='none',fill='tozeroy', fillcolor='green', name='Divergence (+)'), row=2, col=1)
    subs.add_trace(go.Scatter(x=forecast_df[~mask].index, y=forecast_df[~mask]['diff'], mode='none', fill='tozeroy', fillcolor='red', name='Divergence (-)'), row=2, col=1)
    # subs.add_trace(go.Scatter(y=forecast_df['diff'], x=forecast_df['diff'].index, name='Divergence from Normal'), row=2, col=1)


    forecast_df['tt']=(forecast_df['diff']-0).abs()>5000
    forecast_df['tf']=forecast_df['tt'].shift()
    forecast_df = forecast_df.dropna()
    def check(tt, tf, pos):
        if tt and not(tf) and pos=='start':
            return True
        if tf and not(tt) and pos=='end':
            return True
        return False
    forecast_df['start'] = forecast_df.apply(lambda x: check(x['tt'], x['tf'], 'start'), axis=1)
    forecast_df['end'] = forecast_df.apply(lambda x: check(x['tt'], x['tf'], 'end'), axis=1)

    to_highlight = pd.merge(
        forecast_df[forecast_df['start']].reset_index().rename(columns={'index': 'StartD'})['StartD'], 
        forecast_df[forecast_df['end']].reset_index().rename(columns={'index': 'EndD'})['EndD'],
        right_index=True,
        left_index=True
    )

    for th in  to_highlight.iterrows():
        subs.add_vrect(
            x0=th[1]['StartD'], x1=th[1]['EndD'],
            fillcolor="LightSalmon", opacity=0.5,
            layer="below", line_width=0,
            row=2, col=1
        ),


    actual_curve = session.get_curve(name=voluo_ids[selected]['actual'])
    actual_ts = actual_curve.get_data(data_from='2021-01-01', data_to=dt.date.today())
    actual = actual_ts.to_pandas()
    actual.name = 'actual'
    actual_min_date, actual_max_date = actual.index.min(), actual.index.max()

    nomral_curve = session.get_curve(name=voluo_ids[selected]['normal'])
    normal_ts = nomral_curve.get_data(data_from=actual_min_date, data_to=actual_max_date)
    normal = normal_ts.to_pandas()
    normal.name = 'normal'

    div_df = pd.merge(actual, normal, left_index=True, right_index=True)
    div_df['diff'] = div_df['actual'] - div_df['normal']
    subs.add_trace(go.Histogram(y=div_df['diff'], nbinsy=20, histnorm='probability', name='Divergence Histogram'), row=2, col=2)
    mu, std = norm.fit(div_df['diff'])
    x = np.linspace(norm.ppf(0.01, loc=mu, scale=std), norm.ppf(0.99, loc=mu, scale=std), 100)
    subs.add_trace(go.Scatter(y=x, x=norm.pdf(x, loc=mu, scale=std)), row=2, col=2)


    
    region = 'de'

    concerned_runs = [pd.Timestamp.now().floor('6H') - pd.Timedelta(hours=6*i) for i in range(2,5)]

    layout = {
        'showlegend': True,
        'hovermode': 'x',
        'spikedistance': -1,
        'xaxis': {
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'showline': True,
            'showgrid': True,
        },
        'height': 800
    }
    fig1 = go.Figure(layout=layout)
    subs = make_subplots(
        rows=2,
        cols=1,
        figure=fig1
    )

    ## Get PV actuals
    curve_name = 'pro ' + region + ' {} mwh/h cet min15 a'.format(selected_code)
    yesterday = pd.Timestamp.now().floor('D') - pd.Timedelta(days=1)
    pv = session.get_curve(name=curve_name).get_data(data_from=yesterday).to_pandas()
    subs.add_trace(go.Scatter(x=pv.index, y=pv, mode='lines+markers', line={'color': 'black'}, name='Actuals'), row=1, col=1)

    for concerned_run_i, concerned_run in enumerate(concerned_runs):
        issue_date = concerned_run.floor('D')
        run_hour = str(concerned_run.hour).zfill(2)

        ## Get EC PV forecast data
        curve_name = 'pro ' + region + ' {} ec{} mwh/h cet min15 f'.format(selected_code, run_hour)
        ec00  = session.get_curve(name=curve_name).get_instance(issue_date=issue_date).to_pandas()
        ec00 = ec00.loc[pv.index]


        # GFS PV forecast
        curve_name = 'pro ' + region + ' {} gfs{} mwh/h cet min15 f'.format(selected_code, run_hour)
        gfs00 = session.get_curve(name=curve_name).get_instance(issue_date=issue_date).to_pandas()
        gfs00 = gfs00.loc[pv.index]

        # ICON PV forecast
        curve_name = 'pro ' + region + ' {} icon{} mwh/h cet min15 f'.format(selected_code, run_hour)
        icon00 = session.get_curve(name=curve_name).get_instance(issue_date=issue_date).to_pandas()
        icon00 = icon00[(icon00.index<=pv.index.max()) & (icon00.index>=pv.index.min())]

        

    

        line_dash = None if concerned_run_i==0 else 'dash'
        showlegend = True if concerned_run_i==0 else False
        add_to_name = concerned_run.strftime(' (%Y-%m-%d %H:00)') if concerned_run_i!=0 else ''
        
        subs.add_trace(go.Scatter(x=ec00.index, y=ec00, line={'color': px.colors.sequential.Reds[8-2*concerned_run_i-1], 'dash': line_dash}, name='EC{}'.format(add_to_name), showlegend=showlegend), row=1, col=1)
        subs.add_trace(go.Scatter(x=gfs00.index, y=gfs00, line={'color': px.colors.sequential.Greens[8-2*concerned_run_i-1], 'dash': line_dash}, name='GFS{}'.format(add_to_name), showlegend=showlegend), row=1, col=1)
        subs.add_trace(go.Scatter(x=icon00.index, y=icon00, line={'color': px.colors.sequential.Blues[8-2*concerned_run_i-1], 'dash': line_dash}, name='ICON{}'.format(add_to_name), showlegend=showlegend), row=1, col=1)

    subs.add_trace(go.Box(y=(pv.values - ec00.values), name='EC', marker_color = px.colors.sequential.Reds[7], showlegend=False), row=2, col=1)
    subs.add_trace(go.Box(y=(pv.values - gfs00.values), name = 'GFS', marker_color = px.colors.sequential.Greens[7], showlegend=False), row=2, col=1)
    subs.add_trace(go.Box(y=(icon00 - pv).dropna(), name = 'ICON', marker_color = px.colors.sequential.Blues[7], showlegend=False), row=2, col=1)



    return [selected, fig1, fig]