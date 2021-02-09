#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State

import params
from app import app
from utils import pages
from callbacks import runstate

import browse 

module='convert'

storeinit={}            

store = pages.init_store(storeinit, module)

main = html.Div(children=[html.H3("Import volume EM datasets - Choose type:",id='conv_head'),dcc.Dropdown(
        id={'component': 'import_type_dd', 'module': module},persistence=True,
        options=[
            {'label': 'SBEMImage', 'value': 'SBEMImage'}            
        ],
        value='SBEMImage'
        )
    ])

intervals = html.Div([dcc.Interval(id={'component': 'interval1', 'module': module}, interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Interval(id={'component': 'interval2', 'module': module}, interval=params.idle_interval,
                                       n_intervals=0)
                      ])


page = [intervals,main]

r_sel = pages.render_selector(module)
r_sel.style = {'display':'none'}

page.append(r_sel)

page1 = html.Div(id={'component': 'page1', 'module': module})

# # =============================================
# # # Page content

@app.callback([Output({'component': 'page1', 'module': module}, 'children'),
               ],
                Input({'component': 'import_type_dd', 'module': module}, 'value'))
def convert_output(dd_value):
    if dd_value=='SBEMImage':
        return [html.Div(browse.page)]
    
    else:
        return [html.Div([html.Br(),'No data type selected.'])]



page.append(page1)


# =============================================
# Processing status

# initialized with store
# embedded from callbacks import runstate

# # =============================================
# # PROGRESS OUTPUT


collapse_stdout = pages.log_output(module)

# ----------------

# Full page layout:
    

page.append(collapse_stdout)

