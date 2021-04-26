#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input,Output,State


import os
import glob
import json
import numpy as np
# import requests

import params

from app import app

from utils import pages
# from utils import helper_functions as hf

from callbacks import runstate

from filetypes import BDV_finalize


module='finalize'
previous = 'export'
 
store = pages.init_store([],module)


main=html.Div(id={'component': 'main', 'module': module},children=html.H3("Finalize output format."))

intervals = html.Div([dcc.Interval(id={'component': 'interval1', 'module': module}, interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Interval(id={'component': 'interval2', 'module': module}, interval=params.idle_interval,
                                       n_intervals=0)
                      ])


page = [intervals,main,pages.render_selector(module,hidden=True)]




# ===============================================
       
page2 = html.Div([html.H4("Choose post-processing target format"),
                  dcc.Dropdown(id=module+'_format_dd',persistence=True,
                                options=[{'label': 'BigDataViewer (BDV) XML', 'value': 'BDV'}],
                                value='BDV')
                  ])                                

page.append(page2)




# select output volume


page3 = html.Div([html.H4("Choose exported volume"),
                  dcc.Dropdown(id=module+'_input_dd',persistence=True)
                  ])                                

page.append(page3)






@app.callback([Output(module+'_input_dd', 'options'),
                Output(module+'_input_dd', 'value')],
              [Input(module+'_format_dd', 'value'),
                Input({'component': 'store_r_launch', 'module': previous},'modified_timestamp')
                ])
def finalize_volume_dd(dd_in,prev_in):
    
        
    expjson_list = glob.glob(os.path.join(params.json_run_dir,'*export_'+params.user+'*'))
    
    
    dts = []
    
    dd_options=list(dict())
    
    for jsonfile in expjson_list:
        with open(jsonfile,'r') as f:
            export_json = json.load(f)
        
        datetime = jsonfile.split(params.user+'_')[1].strip('.json')
        dts.append(datetime)
        
        vfile = export_json['--n5Path']
        vdescr = ' - '.join([export_json['--project'],
                                  export_json['--stack'],
                                  datetime,
                                  vfile.split('_')[-1].split('.')[0]])
        
        dd_options.append({'label':vdescr,'value':vfile})
        
    
    latest = dd_options[np.argsort(dts)[-1]]['value']
    
    return dd_options, latest







# =============================================
# # Page content for specific export call


page4 = html.Div(id=module+'_page1')

page.append(page4)


@app.callback([Output(module+'_page1', 'children')],
                Input(module+'_format_dd', 'value'))
def finalize_output(value):
    
    if value=='BDV':
        return [BDV_finalize.page]
    
    else:
        return [[html.Br(),'No output type selected.']]



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