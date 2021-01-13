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

import params

import startpage

# Webapp Layout
STYLE_active = {"background-color": "#077","color":"#f1f1f1"}

sidebar_back = html.Nav(className='sidebar_back',children='')


menu_items=[#'convert',
            'mipmaps',
            # 'tilepairs',
            # 'pointmatch'
            ]

menu_text=[#'Convert & upload',
           'Generate MipMaps',
           # 'Find Tile Pairs',
           # 'Find PointMatches'
            ]


#import UI page elements from dynamic menu

for lib in menu_items:
    globals()[lib] = importlib.import_module(lib)
 
consolefile = params.render_log_dir+'/out.txt'                 
menu=list()
store=list()
params.processes=dict()

for m_ind,m_item in enumerate(menu_items):
    menu.append(dcc.Link(id='menu_'+m_item,href='/'+m_item,children=menu_text[m_ind]))
    menu.append(html.Br())
    
    store.append(dcc.Store(id=m_item+'_store', storage_type='session',
                            data={'log_file':consolefile,
                                  'run_state':'wait',
                                  'owner':'SBEM',
                                  'project':'-',
                                  'stack':'-'}) )
    
    params.processes[m_item]=[]
    
    


sidebar = html.Nav(className='sidebar',children=menu)


mainbody = html.Div(className='main',id='page-content')
                    
                    
                    
                    

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
    styles = [{}]*len(menu_items)    
    
    outlist=[html.Div([html.H3('Welcome to the Render-based alignment suite.'),
                       startpage.content])]
           
    for m_ind,m_item in enumerate(menu_items):
        thispage = locate(m_item+".main")

        if pathname=="/"+m_item:  
            subpage = locate(m_item+".page")
            styles[m_ind]=s1
            mod_page = [thispage]
            mod_page.extend(subpage)
            outlist=[mod_page]
        
            
            
    outlist.extend(styles)

    return outlist
    
    
    

if __name__ == '__main__':
    app.run_server(debug=True)
