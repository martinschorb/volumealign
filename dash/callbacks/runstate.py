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
import os

import params
from utils import launch_jobs


#  =================================================


def init_update_status(module):
    
    dash_out = [Output(module+'interval2','interval'),
                Output(module+'store_r_status','data')
                ]
    
    dash_in =  [Input(module+'interval2','n_intervals'),
                Input(module+'cancel', 'n_clicks')]
    
    dash_state = [State(module+'store_run_state','data'),
                   State(module+'outfile','children'),
                   State(module+'store_r_status','data'),
                   State(module+'name','data')]
    
    return dash_out,dash_in,dash_state

def update_status(n,click,run_state,logfile,r_status,module):     
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0].partition(module)[2]
    
    procs=params.processes[module.strip('_')]
    
    logfile = r_status['logfile']    
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

    return status, status_style, log_refresh, c_button_style


#  =================================================



def init_update_output(module):
    dash_out = Output(module+'console-out','value')
    
    dash_in =  [Input(module+'interval1', 'n_intervals'),
                Input(module+'outfile','children')]
    
    dash_state = []
    
    return dash_out,dash_in,dash_state


def update_output(n,outfile):    
    
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


#  =================================================



def init_run_state(module):
    dash_out = [Output(module+'store_run_state','data'),
                Output(module+'outfile','children')]
    dash_in =  [Input(module+'store_r_status','data'),
                Input(module+'store_r_launch','data')]
    return dash_out,dash_in

def run_state(status_in,launch_in):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if 'launch' in trigger:
        # print('launch triggered state:')
        # print(launch_in)
        out = launch_in

    else:
        # print('status triggered state:')
        # print(status_in)
        out = status_in
        
    return out['state'], out['logfile']