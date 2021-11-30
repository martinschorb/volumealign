#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State

import params
from app import app
from utils import pages
from callbacks import runstate,render_selector

from inputtypes import sbem_conv, serialem_conv

module='convert'

storeinit={}            

store = pages.init_store(storeinit, module)

main = html.Div(children=[html.H3("Import volume EM datasets - Choose type:",id='conv_head'),dcc.Dropdown(
        id={'component': 'import_type_dd', 'module': module},persistence=True,
        options=[
            {'label': 'SBEMImage', 'value': 'SBEMImage'},
            {'label': 'SerialEM Montage', 'value': 'SerialEM'},
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

# r_sel = pages.render_selector(module)
# r_sel.style = {'display':'none'}

# page.append(r_sel)

page1 = html.Div(id={'component': 'page1', 'module': module})

page3 = html.Div(id={'component': 'page3', 'module': module})

# # =============================================
# # # Page content

@app.callback([Output({'component': 'page1', 'module': module}, 'children'),
               Output({'component': 'page3', 'module': module}, 'children')],
                Input({'component': 'import_type_dd', 'module': module}, 'value'))
def convert_output(dd_value):
    if dd_value=='SBEMImage':
        return [html.Div(sbem_conv.page),html.Div(sbem_conv.page2)]
    
    elif dd_value=='SerialEM':
        return [html.Div(serialem_conv.page),html.Div(serialem_conv.page2)]
    else:
        return [html.Div([html.Br(),'No data type selected.']),dash.no_update]



page.append(page1)


# # ===============================================
#  RENDER STACK SELECTOR

# Pre-fill render stack selection from previous module


page2 = pages.render_selector(module,create=True,show=['stack','project'],header='Select target stack:')

page.append(page2)



# # ===============================================
# Go Button and associated events:

page.append(page3)

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

