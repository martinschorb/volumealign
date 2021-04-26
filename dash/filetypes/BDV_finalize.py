#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input,Output,State

# import sys
import numpy as np
import os
import json
import requests
import importlib


from app import app
import params

from utils import pages,launch_jobs
from utils import helper_functions as hf




# element prefix
label = "BDV_finalize"
parent = "finalize"


page=[html.Br()]

# =============================================
# Start Button

gobutton = html.Div(children=[html.Br(),
                              html.Button('Start Format conversion',
                                          id={'component': 'go', 'module': label},disabled=True),
                              html.Div(id={'component': 'buttondiv', 'module': label}),
                              html.Br(),
                              pages.compute_loc(label,c_default='standalone'),
                              html.Br(),
                              html.Div(id={'component': 'run_state', 'module': parent}, style={'display': 'none'},children='wait')])



page.append(gobutton)


# =============================================
   
#  LAUNCH CALLBACK FUNCTION

# =============================================
             



@app.callback([Output({'component': 'go', 'module': label}, 'disabled'),
               Output({'component': 'buttondiv', 'module': label}, 'children'),
               Output({'component': 'store_r_launch', 'module': parent},'data'),
               ],
              [Input({'component': 'go', 'module': label}, 'n_clicks'),
               Input(parent+'_input_dd', 'value')]
              )
def n5export_execute_gobutton(click,n5file): 
    
    if not dash.callback_context.triggered: 
        raise PreventUpdate
            
    if n5file is None:
        raise PreventUpdate
                
    out = dict()
    out['state'] = 'wait'
    out['logfile'] = ''
            
    if not os.path.exists(n5file):    

        return True, 'Input data file does not exist.', dash.no_update
    
    if not os.access(n5file,os.W_OK | os.X_OK):
        return True,'Output directory not writable!', dash.no_update
    
    
    
        
        
      
    
    
