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
                  [Input({'component': 'store_stackparams', 'module': MATCH}, 'data'),
                   Input({'component': 'sliceim_image_0', 'module': MATCH}, "relayoutData")]
                  )
    def paramstoouterlimits(thisstore,annotations):
        if not dash.callback_context.triggered: 
            raise PreventUpdate
        oc = hf.output_components()

        dim = oc[0][0][-1]

        stackparams = thisstore['stackparams']
        minval = stackparams['stats']['stackBounds']['min' + dim]
        maxval = stackparams['stats']['stackBounds']['max' + dim]

        if not annotations in ([],None) and dim !='Z':

            if "shapes" in annotations:
                last_shape = annotations["shapes"][-1]
                minv = int(last_shape[dim.lower()+'0'])
                maxv = int(last_shape[dim.lower()+'1'])

            elif any(["shapes" in key for key in annotations]):
                minv = int([annotations[key] for key in annotations if dim.lower()+'0' in key][0])
                maxv = int([annotations[key] for key in annotations if dim.lower()+'1' in key][0])

            else:
                minv=minval
                maxv=maxval

            if minv > maxv:
                minv, maxv = maxv, minv

            minval = minv
            maxval = maxv
        
        return minval,minval,maxval,maxval

    
    @app.callback([Output({'component': 'start'+dim,'module' : MATCH},'max'),
                    Output({'component':'end'+dim,'module' : MATCH},'min')],
                  [Input({'component': 'start'+dim,'module' : MATCH}, 'value'),
                    Input({'component':'end'+dim,'module' : MATCH},'value')]
                  )
    def innerlimits(minval,maxval):
        return maxval, minval

