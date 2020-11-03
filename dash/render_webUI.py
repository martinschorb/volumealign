# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output
from app import app

#import UI page elements
import convert


# Webapp Layout
STYLE_active = {"background-color": "#077","color":"#f1f1f1"}

sidebar = html.Nav(className='sidebar',children=[dcc.Link(id='menu1',href='/convert',children='Convert & upload'),
                                                 html.Br(),
                                                 dcc.Link(id='menu2',href='/mipmaps',children='Generate MipMaps'),
                                                 html.Br(),
                                                 dcc.Link(id='menu3',href='/tilepairs',children='Find Tile Pairs')])

mainbody = html.Div(className='main',id='page-content')


app.layout = html.Div(
    [
    html.Div(className='header', children=[html.H1(dcc.Link(href='/',children='Volume EM alignment with Render'))]),
    html.Section([
        dcc.Location(id='url', refresh=False),
    sidebar,
    mainbody,
    html.Div(id='convert-data',children='None') 
    ])])


