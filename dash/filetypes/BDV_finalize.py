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
             
def n5export_execute_gobutton(): 
    
    if not dash.callback_context.triggered: 
            raise PreventUpdate
   
    
    
