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
import numpy as np
import requests

import params

from app import app

from utils import pages
from utils import helper_functions as hf

from callbacks import runstate,render_selector,substack_sel,match_selector,tile_view


from sift import sift_pointmatch


module='solve'



storeinit = {}            
store = pages.init_store(storeinit, module)

store.append(dcc.Store(id={'component':'runstep','module':module},data='generate'))

for storeitem in params.match_store.keys():       
        store.append(dcc.Store(id={'component':'store_'+storeitem,'module':module}, storage_type='session',data=params.match_store[storeitem]))
    

main=html.Div(id={'component': 'main', 'module': module},children=html.H3("Solve tile Positions from PointMatchCollection"))

intervals = html.Div([dcc.Interval(id={'component': 'interval1', 'module': module}, interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Interval(id={'component': 'interval2', 'module': module}, interval=params.idle_interval,
                                       n_intervals=0)
                      ])


page = [intervals,main]



# # ===============================================
#  RENDER STACK SELECTOR

# Pre-fill render stack selection from previous module

us_out,us_in,us_state = render_selector.init_update_store(module,'pointmatch')

@app.callback(us_out,us_in,us_state,
              prevent_initial_call=True)
def solve_update_store(*args): 
    return render_selector.update_store(*args)

page1 = pages.render_selector(module)


page.append(page1)


page2 = pages.match_selector(module)

       
page.append(page2)       


# ===============================================
  


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