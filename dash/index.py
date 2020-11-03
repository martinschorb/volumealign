#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 15:26:45 2020

@author: schorb
"""

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

import callbacks

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




@app.callback([Output('page-content', 'children'),Output('menu1','style'),Output('menu2','style'),Output('menu3','style')],
              [Input('url', 'pathname')])
def display_page(pathname):
    s1 = STYLE_active
    
    if pathname=="/convert":
        return [[convert.base,
                 html.Div(id='convert-page1')],s1,{},{}]    
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
        return [html.Div([
        html.H3('You are on another page.')
        ]),{},{},{}]
    
    

if __name__ == '__main__':
    app.run_server(debug=True)