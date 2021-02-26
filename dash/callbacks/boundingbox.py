#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 14:52:17 2021

@author: schorb
"""


import dash
# import dash_core_components as dcc
# import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate


from app import app

# import params
from utils import helper_functions as hf


for dim in ['X','Y','Z']:
    @app.callback([Output({'component': 'start'+dim,'module' : MATCH},'value'),
                    Output({'component': 'start'+dim,'module' : MATCH},'min'),
                    Output({'component': 'end'+dim,'module' : MATCH},'value'),
                    Output({'component': 'end'+dim,'module' : MATCH},'max')],
                  Input({'component': 'store_stackparams', 'module': MATCH}, 'data')
                  )
    def paramstoouterlimits(thisstore):
        if not dash.callback_context.triggered: 
            raise PreventUpdate
        
        oc = hf.output_components()
        
        dim = oc[0][0][-1]
        
        stackparams = thisstore['stackparams']
        minval = stackparams['stats']['stackBounds']['min'+dim]
        maxval = stackparams['stats']['stackBounds']['max'+dim]
        
        return minval,minval,maxval,maxval

    
    @app.callback([Output({'component': 'start'+dim,'module' : MATCH},'max'),
                    Output({'component':'end'+dim,'module' : MATCH},'min')],
                  [Input({'component': 'start'+dim,'module' : MATCH}, 'value'),
                    Input({'component':'end'+dim,'module' : MATCH},'value')]
                  )
    def innerlimits(minval,maxval):
        return maxval, minval

