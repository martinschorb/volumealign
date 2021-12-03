#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
import dash
from dash import dcc
from dash import html
from dash.exceptions import PreventUpdate
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
 
store = pages.init_store({},module)


main=html.Div(id={'component': 'main', 'module': module},children=html.H3("Finalize output format."))


page = [main,pages.render_selector(module,show=False)]




# ===============================================
       
page2 = html.Div([html.H4("Choose post-processing target format"),
                  dcc.Dropdown(id=module+'_format_dd',persistence=True,
                                options=[{'label': 'BigDataViewer (BDV) XML', 'value': 'BDV'}],
                                value='BDV')
                  ])                                

page.append(page2)



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