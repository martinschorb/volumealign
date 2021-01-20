#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 15:26:45 2020

@author: schorb
"""

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
# from pydoc import locate

import importlib
from app import app

import params

import startpage

# Webapp Layout
STYLE_active = {"background-color": "#077","color":"#f1f1f1"}

sidebar_back = html.Nav(className='sidebar_back',children='')


menu_items=['convert',
            'mipmaps',
            'tilepairs',
            # 'pointmatch'
            ]

menu_text=['Convert & upload',
            'Generate MipMaps',
            'Find Tile Pairs',
            # 'Find PointMatches'
            ]


consolefile = params.render_log_dir+'/out.txt'                 
menu=list()
store=list()
params.processes=dict()

allpages = list()

#import UI page elements from dynamic menu

for lib in menu_items:
    thismodule = importlib.import_module(lib)
    thisstore = getattr(thismodule,'store')
    store.extend(thisstore)
    thispage = getattr(thismodule,'page')
    allpages.append(html.Div(thispage,id={'component': 'page', 'module': lib}, style={'display': 'none'}))
    
for m_ind,m_item in enumerate(menu_items):
    menu.append(dcc.Link(id='menu_'+m_item,href='/'+m_item,children=menu_text[m_ind]))
    menu.append(html.Br())    
        
    params.processes[m_item]=[]
    

sidebar = html.Nav(className='sidebar',children=menu)


mainbody = html.Div(className='main',id='page-content',children=allpages)
                    
                    

# ==================================================

# STORAGE of important values across sub-modules


storediv=html.Div(store)                   
                  



# ==================================================

# MAIN LAYOUT

app.layout = html.Div(
    [
    html.Div(className='header', children=[html.H1(dcc.Link(href='/',children='Volume EM alignment with Render'))]),
    html.Section([
        dcc.Location(id='url', refresh=False),
    sidebar_back,
    sidebar,
    mainbody,
    storediv
    ])])





# ==================================================

# CALLBACKS

menu_cb_out = [Output('page-content', 'children')]
for m_i in menu_items: menu_cb_out.append(Output('menu_'+m_i,'style'))


@app.callback(menu_cb_out,
              [Input('url', 'pathname')])
def display_page(pathname):
    s1 = STYLE_active
    menu_styles = [{}]*len(menu_items)    
    
    outlist=[[html.Div([html.H3('Welcome to the Render-based alignment suite.'),
                         startpage.content])]]
    start = True
    
    for m_ind,m_item in enumerate(menu_items):
        allpages[m_ind].style = {'display': 'none'}
        if pathname=="/"+m_item:  
            menu_styles[m_ind]=s1            
            allpages[m_ind].style = {}
            start = False
            
    if start:
        outlist[0].extend(allpages)
    else:
        outlist = [allpages]
    
    outlist.extend(menu_styles)
    
    return outlist
    
    
    

if __name__ == '__main__':
    app.run_server(host= '0.0.0.0',debug=True)
