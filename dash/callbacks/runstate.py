#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 14:50:48 2021

@author: schorb
"""
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash
import dash_html_components as html
from dash.exceptions import PreventUpdate

import subprocess
import os

from app import app


import params
from utils import launch_jobs
from utils import helper_functions as hf


#  =================================================


@app.callback([Output({'component': 'interval2', 'module': MATCH},'interval'),
                Output({'component': 'store_r_status', 'module': MATCH},'data')
                ],
              [Input({'component': 'interval2', 'module': MATCH},'n_intervals'),
                Input({'component': 'cancel', 'module': MATCH}, 'n_clicks')],
              [State({'component': 'store_run_state', 'module': MATCH},'data'),
                   State({'component': 'outfile', 'module': MATCH},'children'),
                   State({'component': 'store_r_status', 'module': MATCH},'data'),
                   State({'component': 'name', 'module': MATCH},'data')]
              )
def update_status(n,click,run_state,logfile,r_status,module):     
    if not dash.callback_context.triggered: 
        raise PreventUpdate
        
    trigger = hf.trigger_component()
    procs=params.processes[module.strip('_')]
    
    r_status['logfile']  = logfile
    r_status['state'] = run_state
    
    
    if 'interval2' in trigger:        
        
        if procs==[]:
            if run_state not in ['input','wait']:
                r_status['state'] = 'input'               
        
        if (type(procs) is subprocess.Popen or len(procs)>0): 
            r_status['state'] = launch_jobs.status(procs)   


        if 'Error' in r_status['state']:
            if logfile.endswith('.log'):
                r_status['logfile'] = logfile[logfile.rfind('.log')]+'.err'

        return params.idle_interval,r_status
    
    elif 'cancel' in trigger:

        r_status['state'] = launch_jobs.canceljobs(procs)
        
        params.processes[module.strip('_')] = []    
        
        return params.idle_interval, r_status
    
    else:
        return [dash.no_update] * 3



#  =================================================


@app.callback([Output({'component': 'get-status', 'module': MATCH},'children'),
                Output({'component': 'get-status', 'module': MATCH},'style'),
                Output({'component': 'interval1', 'module': MATCH}, 'interval'),
                Output({'component': 'cancel', 'module': MATCH},'style')
                ],
              Input({'component': 'store_run_state', 'module': MATCH},'data'),
              State({'component': 'name', 'module': MATCH},'data'))
def get_status(run_state,module):
    if not dash.callback_context.triggered: 
        raise PreventUpdate
        
    status_style = {"font-family":"Courier New",'color':'#000'} 
    log_refresh = params.idle_interval
    procs=params.processes[module.strip('_')] 
    c_button_style = {'display': 'none'}    
    if run_state == 'running':  
        
        if procs == []:
            status = 'not running'
        else:
            status = html.Div([html.Img(src='assets/gears.gif',height=72),html.Br(),'running'])
            log_refresh = params.refresh_interval
            if not type(procs) is subprocess.Popen:
                if  type(procs) is str:
                    c_button_style = {}                    
                elif not type(procs[0]) is subprocess.Popen:
                    c_button_style = {}
                    
    elif run_state == 'input':
        status='process will start on click.'
    elif run_state == 'done':
        status='DONE'
        status_style = {'color':'#0E0'}
    elif run_state == 'pending':
        c_button_style = {} 
        status = ['Waiting for cluster resources to be allocated.']
    elif run_state == 'wait':
        status='not running'
    else:
        status=run_state
    
    # print('display status:  '+str(status))
    
    return status, status_style, log_refresh, c_button_style


# #  =================================================



@app.callback(Output({'component': 'console-out', 'module': MATCH},'value'),
              [Input({'component': 'interval1', 'module': MATCH}, 'n_intervals'),
                Input({'component': 'outfile', 'module': MATCH},'children')]
              )
def update_output(n,outfile):
    if not dash.callback_context.triggered: 
        raise PreventUpdate
     
    data=''

    if outfile is not None:
        if os.path.exists(outfile):
            file = open(outfile, 'r')    
            lines = file.readlines()
            if lines.__len__()<=params.disp_lines:
                last_lines=lines
            else:
                last_lines = lines[-params.disp_lines:]
            for line in last_lines:
                data=data+line
            file.close()
        
    return data


# #  =================================================



@app.callback([Output({'component': 'store_run_state', 'module': MATCH},'data'),
                Output({'component': 'outfile', 'module': MATCH},'children')],
              [Input({'component': 'store_r_status', 'module': MATCH},'data'),
                Input({'component': 'store_r_launch', 'module': MATCH},'data')]
              )
def run_state(status_in,launch_in):
    if not dash.callback_context.triggered: 
        raise PreventUpdate
    trigger = hf.trigger_component()
    
    # print('-- merge status --')
    # print(trigger)
    
    if 'launch' in trigger:
        # print('launch triggered state:')
        # print(launch_in)
        out = launch_in

    else:
        # print('status triggered state:')
        # print(status_in)
        out = status_in.copy()        
    # print(out)
    
    return out['state'], out['logfile']