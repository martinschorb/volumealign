#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 14:50:48 2021

@author: schorb
"""
from dash.dependencies import Input,Output,State
import dash
import dash_html_components as html

import subprocess

import params
from utils import launch_jobs


#  =================================================


def init_update_status(module):
    
    dash_out = [Output(module+'interval2','interval'),
                # Output(module+'store_run_state','data'),
                # Output(module+'store_logfile','data')
                ]
    
    dash_in =  [Input(module+'interval2','n_intervals'),
                Input(module+'cancel', 'n_clicks')]
    
    dash_state = [State(module+'store_run_state','data'),
                   State(module+'store_logfile','data'),
                   State(module+'name','data')]
    
    return dash_out,dash_in,dash_state

def update_status(n,click,run_state,logfile,module):     
    ctx = dash.callback_context
    trigger = ctx.inputs
    
    procs=params.processes[module.strip('_')]
    
    print(trigger)
    
    if trigger == 'interval2':
        status = run_state
        
        if procs==[]:
            if run_state not in ['input','wait']:
                run_state = 'input'               
        
        if (type(procs) is subprocess.Popen or len(procs)>0): 
            status = launch_jobs.status(procs)   
            run_state = status    

        if 'Error' in status:
            if logfile.endswith('.log'):
                logfile = logfile[logfile.rfind('.log')]+'.err'
        
        print('2')
        print(run_state)
        print('3')
        print(logfile)
        
        return params.idle_interval,run_state,logfile
    
    elif trigger == 'cancel':
        print('cancel')
        p_status = launch_jobs.canceljobs(procs)
        
        params.processes[module.strip('_')] = []    
        
        return params.idle_interval, p_status, dash.no_update
    
    else:
        return [dash.no_update] * 4



#  =================================================



def init_get_status(module):
    
    dash_out = [Output(module+'get-status','children'),
                Output(module+'get-status','style'),
                Output(module+'interval1', 'interval'),
                Output(module+'cancel','style')
                ]
    
    dash_in =  Input(module+'store_run_state','data')
    
    dash_state = State(module+'name','data')
    
    return dash_out,dash_in,dash_state

def get_status(run_state,module):

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
                c_button_style = ' '
                if  type(procs) is str:
                    status = html.Div([html.Img(src='assets/gears.gif',height=72),html.Br(),'running  -  '])
                elif not type(procs[0]) is subprocess.Popen:
                    status = html.Div([html.Img(src='assets/gears.gif',height=72),html.Br(),'running  -  '])
    elif run_state == 'input':
        status='process will start on click.'
    elif run_state == 'done':
        status='DONE'
        status_style = {'color':'#0E0'}
    elif run_state == 'pending':
        c_button_style = ' '
        status = ['Waiting for cluster resources to be allocated.']
    elif run_state == 'wait':
        status='not running'
    else:
        status=run_state
    
    
    return status, status_style, log_refresh, c_button_style



