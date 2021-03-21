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
import datetime as dt


from app import app
from apps import deep_dive, flows, live_balance



config_file_path = './/configfile.ini'
session = wapi.Session(config_file=config_file_path)


PLOTLY_LOGO = "https://upload.wikimedia.org/wikipedia/commons/9/9f/Alpiq_intec_logo.png"

search_bar = dbc.Row(
    [
        dbc.Col(
            dbc.Button("Live Balance", color="primary", className="ml-2", href='/live_balance'),
            width="auto",
        ),
        dbc.Col(
            dbc.Button("Deep Dive", color="primary", className="ml-2", href='/deep_dive'),
            width="auto",
        ),
        dbc.Col(
            dbc.Button("Flows", color="primary", className="ml-2", href='/flows'),
            width="auto",
        ),
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(dbc.NavbarBrand("The Market at a glance", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="https://plot.ly",
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(search_bar, id="navbar-collapse", navbar=True),
    ],
    color="dark",
    dark=True,
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])



@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/live_balance':
        return live_balance.layout
    elif pathname == '/deep_dive':
        return deep_dive.layout
    elif pathname == '/flows':
        return flows.layout

    # return html.Div([
    #     html.H3('You are on page {}'.format(pathname))
    # ])

    return children




if __name__ == "__main__":
    app.run_server(debug=False)