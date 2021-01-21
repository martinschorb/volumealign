#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 14:52:17 2021

@author: schorb
"""


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

import requests
import json

from app import app

import params
from utils import helper_functions as hf

@app.callback([Output({'component':'startsection','module' : MATCH},'value'),
                Output({'component':'startsection','module' : MATCH},'min'),
                Output({'component':'endsection','module' : MATCH},'value'),
                Output({'component':'endsection','module' : MATCH},'max'),
                Output({'component': 'store_stackparams', 'module': MATCH}, 'data')],
              Input({'component':'stack_dd','module' : MATCH},'value'),
              State({'component': 'store_allstacks', 'module': MATCH},'data')
              ,prevent_initial_call=True)
def stacktosections(stack_sel,allstacks):
    
    if not dash.callback_context.triggered: 
        raise PreventUpdate
    sec_start = 0
    sec_end = 1
    

    
    if not(stack_sel=='-' ):   
        stacklist = [stack for stack in allstacks if stack['stackId']['stack'] == stack_sel]        
        if not stacklist == []:
            stackparams = stacklist[0]    
            thisstore=dict()
            thisstore['stack'] = stackparams['stackId']['stack']
            thisstore['stackparams'] = stackparams
            thisstore['zmin']=stackparams['stats']['stackBounds']['minZ']
            thisstore['zmax']=stackparams['stats']['stackBounds']['maxZ']
            thisstore['numtiles']=stackparams['stats']['tileCount']
            thisstore['numsections']=stackparams['stats']['sectionCount']

            
            sec_start = int(thisstore['zmin'])
            sec_end = int(thisstore['zmax'])

    return sec_start, sec_start, sec_end, sec_end, thisstore
