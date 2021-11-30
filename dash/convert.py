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

inputmodules = ['inputtypes.sbem_conv',
                'inputtypes.serialem_conv']

defaulttype = 'SBEM'





storeinit={}            

store = pages.init_store(storeinit, module)

main = html.Div(children=[html.H3("Import volume EM datasets - Choose type:",id='conv_head'),dcc.Dropdown(
        id={'component': 'import_type_dd', 'module': module},persistence=True,
        options=inputtypes,
        value=defaulttype
        )
    ])

intervals = html.Div([dcc.Interval(id={'component': 'interval1', 'module': module}, interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Interval(id={'component': 'interval2', 'module': module}, interval=params.idle_interval,
                                       n_intervals=0)
                      ])


page = [intervals,main]

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

switch_out = [Output('nullpage','style'),
              Output({'component':'render_seldiv','module':module},'style')]


page3=[]

for inputsel,impmod in zip(inputtypes,inputmodules):
    thismodule = importlib.import_module(impmod)
    
    page1.append(html.Div(getattr(thismodule,'page1'),
                         id={'component':'page1','module':inputsel['value']},
                         style = {'display':'none'}))
    switch_out.append(Output({'component':'page1','module':inputsel['value']},'style'))
    
    page3.append(html.Div(getattr(thismodule,'page2'),
                         id={'component':'page2','module':inputsel['value']},
                         style = {'display':'none'}))
    switch_out.append(Output({'component':'page2','module':inputsel['value']},'style'))



page2 = html.Div(pages.render_selector(module,create=True,show=['stack','project'],header='Select target stack:'),
                 id={'component':'render_seldiv','module':module},
                 style = {'display':'none'})




@app.callback(switch_out,
              Input({'component': 'import_type_dd', 'module': module}, 'value'))
def convert_output(dd_value):
    
    outputs = dash.callback_context.outputs_list
    
    outstyles = [{'display':'none'}]*len(outputs)
    
    modules = [m['id']['module'] for m in outputs[2:]]
    
    for ix, mod in enumerate(modules):
        if mod == dd_value:
            outstyles[ix+2]={}
    
    if dd_value in modules:
        outstyles[1]={}
    else:
        outstyles[0]={}
        
    return outstyles

    
    # else:
                
    #     return {},{'display':'none'},


page.append(html.Div(page1))
page.append(html.Div(page2))
page.append(html.Div(page3))


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

