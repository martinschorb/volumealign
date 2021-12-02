#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input,Output,State

import importlib

import params
from app import app
from utils import pages
from callbacks import runstate,render_selector


from inputtypes import sbem_conv, serialem_conv

module='convert'



inputtypes = [
        {'label': 'SBEMImage', 'value': 'SBEM'},
        {'label': 'SerialEM Montage', 'value': 'SerialEM'},
        ]

inputmodules = [
                'inputtypes.sbem_conv',
                'inputtypes.serialem_conv'
                ]

defaulttype = 'SBEM'



main = html.Div(children=[html.H3("Import volume EM datasets - Choose type:",id='conv_head'),dcc.Dropdown(
        id={'component': 'import_type_dd', 'module': module},persistence=True,
        options=inputtypes,
        value=defaulttype
        )
    ])



page = [main]


#  RENDER STACK SELECTOR

# Pre-fill render stack selection from input selection


@app.callback(Output({'component': 'store_init_render', 'module': module},'data'),
              Input({'component': 'import_type_dd', 'module': module}, 'value'),
              prevent_initial_call=True)
def convert_update_store(owner_dd): 
    outstore=dict()
    outstore['owner'] = owner_dd
    
    return outstore



page1 = []


# # =============================================
# # # Page content

page1.append(html.Div([html.Br(),'No data type selected.'],
                      id='nullpage'))

switch_outputs = [Output('nullpage','style')]

status_inputs = []


page2=[]

for inputsel,impmod in zip(inputtypes,inputmodules):
    thismodule = importlib.import_module(impmod)
    
    page1.append(html.Div(getattr(thismodule,'page1'),
                         id={'component':'page1','module':inputsel['value']},
                         style = {'display':'none'}))
    switch_outputs.append(Output({'component':'page1','module':inputsel['value']},'style'))
    
    page2.append(html.Div(getattr(thismodule,'page2'),
                         id={'component':'page2','module':inputsel['value']},
                         style = {'display':'none'}))
    switch_outputs.append(Output({'component':'page2','module':inputsel['value']},'style'))
    
    status_inputs.append(Input({'component':'status','module':inputsel['value']},'data'))



# Switch the visibility of elements for each selected sub-page based on the import type dropdown selection

@app.callback(switch_outputs,
              Input({'component': 'import_type_dd', 'module': module}, 'value'))
def convert_output(dd_value):
    
    outputs = dash.callback_context.outputs_list
    outstyles = [{'display':'none'}]*len(outputs)
    
    modules = [m['id']['module'] for m in outputs[1:]]
    
    for ix, mod in enumerate(modules):
        
        if mod == dd_value:
            outstyles[ix+1]={}
    
    if dd_value not in modules:    
        outstyles[0]={}
        
    return outstyles



page.append(html.Div(page1))
page.append(html.Div(page2))



