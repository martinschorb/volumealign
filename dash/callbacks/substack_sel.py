#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 14:52:17 2021

@author: schorb
"""


import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate


from app import app


@app.callback(Output({'component': 'store_stackparams', 'module': MATCH}, 'data'),
              Input({'component':'stack_dd','module' : MATCH},'value'),
              State({'component': 'store_allstacks', 'module': MATCH},'data')
              )
def stacktoparams(stack_sel,allstacks):    
    if not dash.callback_context.triggered: 
        raise PreventUpdate

    if allstacks in (None,'',[]):
        raise PreventUpdate

    thisstore=dict()
    
    if not(stack_sel=='-' ):   
        stacklist = [stack for stack in allstacks if stack['stackId']['stack'] == stack_sel]        
        if not stacklist == []:
            stackparams = stacklist[0]
            
            if 'None' in (stackparams['stackId']['owner'],stackparams['stackId']['project']):
                return dash.no_update
            
            thisstore['stack'] = stackparams['stackId']['stack']
            thisstore['stackparams'] = stackparams
            thisstore['zmin']=stackparams['stats']['stackBounds']['minZ']
            thisstore['zmax']=stackparams['stats']['stackBounds']['maxZ']
            thisstore['numtiles']=stackparams['stats']['tileCount']
            thisstore['numsections']=stackparams['stats']['sectionCount']

    return thisstore



@app.callback([Output({'component':'startsection','module' : MATCH},'value'),
                Output({'component':'startsection','module' : MATCH},'min'),
                Output({'component':'endsection','module' : MATCH},'value'),
                Output({'component':'endsection','module' : MATCH},'max')],
              Input({'component': 'store_stackparams', 'module': MATCH}, 'data'),
             )
def paramstosections(thisstore):    
    if not dash.callback_context.triggered: 
        raise PreventUpdate

    if not 'zmin' in thisstore.keys():
        return dash.no_update
    
    sec_start = int(thisstore['zmin'])
    sec_end = int(thisstore['zmax'])

    
    return sec_start, sec_start, sec_end, sec_end



@app.callback([Output({'component':'startsection','module' : MATCH},'max'),
                Output({'component':'endsection','module' : MATCH},'min')],
              [Input({'component':'startsection','module' : MATCH}, 'value'),
                Input({'component':'endsection','module' : MATCH},'value'),
                Input({'component':'sec_input1','module' : MATCH},'value')]
              )
def sectionlimits(start_sec,end_sec,sec_range=0):
    
    if not sec_range is None and not start_sec is None and not end_sec is None:
        return end_sec - sec_range, start_sec + sec_range
    else:
        return end_sec, start_sec

