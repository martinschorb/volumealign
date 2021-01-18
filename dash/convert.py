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

from sbem import sbem_conv


module='convert_'

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


intervals = html.Div([dcc.Interval(id=module+'interval1', interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Interval(id=module+'interval2', interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Store(id=module+'tmpstore'),
                      dcc.Store(id=module+'stack')
                      ])

junk = html.Div(id=module+'junk')

page1 = html.Div(id=module+'page1')

collapse_stdout = pages.log_output(module)

print(collapse_stdout)

# =============================================
# # Page content

@app.callback([Output(module+'page1', 'children'),
               Output(module+'store_owner','data')],
                Input(module+'dropdown1', 'value'))
def convert_output(dd_value):
    if dd_value=='SBEMImage':
        thisstore='SBEM'
        return sbem_conv.page, thisstore
    
    else:
        return [html.Br(),'No data type selected.'],None



# =============================================
# Processing status

cus_out,cus_in,cus_state = runstate.init_update_status(module)

@app.callback(cus_out,cus_in,cus_state)
def convert_update_status(*args): 
    return runstate.update_status(*args)



cgs_out,cgs_in,cgs_state = runstate.init_get_status(module)

@app.callback(cgs_out,cgs_in,cgs_state)
def convert_get_status(*args):
    return runstate.get_status(*args)


rs_out, rs_in = runstate.init_run_state(module)

@app.callback(rs_out, rs_in)
def covert_run_state(*args):
    return runstate.run_state(*args)  

# # =============================================
# # PROGRESS OUTPUT

uo_out,uo_in,uo_state = runstate.init_update_output(module)

@app.callback(uo_out,uo_in,uo_state)
def convert_update_output(*args):
    return runstate.update_output(*args)



# Full page layout:
    
page = []
page.append(intervals)
page.append(page1)
page.append(collapse_stdout)

