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
# from callbacks import runstate

# from sbem import sbem_conv


module='convert'

storeinit={}            

store = pages.init_store(storeinit, module)

main = html.Div(children=[html.H3("Import volume EM datasets - Choose type:",id='conv_head'),dcc.Dropdown(
        id=module+'dropdown1',persistence=True,
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


page = [intervals]

r_sel = pages.render_selector(module)
r_sel.style = {'display':'none'}

page.append(r_sel)

page1 = html.Div(id=module+'_page1')

# # =============================================
# # # Page content

# @app.callback([Output(module+'page1', 'children'),
#                 Output(module+'store_owner','data')],
#                 Input(module+'dropdown1', 'value'))
# def convert_output(dd_value):
#     # if dd_value=='SBEMImage':
#     #     thisstore='SBEM'
#     #     return sbem_conv.page, thisstore
    
#     # else:
#         return [html.Br(),'No data type selected.'],None



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

