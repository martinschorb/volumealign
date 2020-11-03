# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

from dash.dependencies import Input,Output


app = dash.Dash(__name__)


# Webapp Layout
STYLE_active = {"background-color": "#077","color":"#f1f1f1"}
STYLE_inactive = {"background-color": "#bbb","color":"#666"}

sidebar = html.Nav(className='sidebar',children=[dcc.Link(id='menu1',href='/convert',children='Convert & upload'),
                                                 html.Br(),
                                                 dcc.Link(id='menu2',href='/mipmaps',children='Generate MipMaps'),
                                                 html.Br(),
                                                 dcc.Link(id='menu3',href='/tilepairs',children='Find Tile Pairs')])

mainbody = html.Div(className='main',id='page-content')


app.layout = html.Div(
    [
    html.Div(className='header', children=[html.H1(children='Volume EM alignment with Render')]),
    html.Section([
        dcc.Location(id='url', refresh=False),
    sidebar,
    mainbody
    ])])




@app.callback([Output('page-content', 'children'),Output('menu1','style'),Output('menu2','style'),Output('menu3','style')],
              [Input('url', 'pathname')])
def display_page(pathname):
    s1 = STYLE_active
    
    if pathname=="/convert":
        return [html.Div([
        html.H3('You are on page {}'.format(pathname))
        ]),s1,{},{}]    
    elif pathname=="/mipmaps":
        s1=STYLE_active
        return [html.Div([
        html.H3('You are on page {}'.format(pathname))
        ]),{},s1,{}]
    elif pathname=="/tilepairs":
        s1=STYLE_active
        return [html.Div('You are on tilepairs')
        ,{},{},s1]
    else:
        s1=STYLE_inactive
        return [html.Div([
        html.H3('You are on another page.')
        ]),s1,{},{}]
    
    



if __name__ == '__main__':
    app.run_server(debug=True)