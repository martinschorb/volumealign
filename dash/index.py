#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 15:26:45 2020

@author: schorb
"""

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from pydoc import locate

import importlib
from app import app



# Webapp Layout
STYLE_active = {"background-color": "#077","color":"#f1f1f1"}

sidebar_back = html.Nav(className='sidebar_back',children='')


menu_items=['convert',
            'mipmaps',
            'tilepairs']

menu_text=['Convert & upload',
           'Generate MipMaps',
           'Find Tile Pairs']


#import UI page elements from dynamic menu

for lib in menu_items:
    globals()[lib] = importlib.import_module(lib)
                   
menu=[]

for m_ind,m_item in enumerate(menu_items):
    menu.append(dcc.Link(id='menu_'+m_item,href='/'+m_item,children=menu_text[m_ind]))
    menu.append(html.Br())

sidebar = html.Nav(className='sidebar',children=menu)


mainbody = html.Div(className='main',id='page-content')


app.layout = html.Div(
    [
    html.Div(className='header', children=[html.H1(dcc.Link(href='/',children='Volume EM alignment with Render'))]),
    html.Section([
        dcc.Location(id='url', refresh=False),
    sidebar_back,
    sidebar,
    mainbody
    ])])



menu_cb_out = [Output('page-content', 'children')]
for m_i in menu_items: menu_cb_out.append(Output('menu_'+m_i,'style'))


@app.callback(menu_cb_out,
              [Input('url', 'pathname')])
def display_page(pathname):
    s1 = STYLE_active
    styles = [{}]*len(menu_items)    
    
    outlist=[html.Div([html.H3('You are on another page.')])]
           
    for m_ind,m_item in enumerate(menu_items):
        thispage = locate(m_item+".main")
        
        if pathname=="/"+m_item:            
            styles[m_ind]=s1
            mod_page = [thispage,html.Div(id=m_item+'-page1')]            
            outlist=[mod_page]
        
            
            
    outlist.extend(styles)
        
    return outlist
    
    
    

if __name__ == '__main__':
    app.run_server(debug=True)