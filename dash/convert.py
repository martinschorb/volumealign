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
import params
import subprocess

from index import processes

from app import app

from sbem import sbem_conv
from utils import launch_jobs


module='convert_'


main = html.Div([html.H3("Import volume EM datasets - Choose type:",id='conv_head'),dcc.Dropdown(
        id=module+'dropdown1',persistence=True,
        options=[
            {'label': 'SBEMImage', 'value': 'SBEMImage'}            
        ],
        value='SBEMImage'
        )
    
    ])

page1 = html.Div(id=module+'page1')



@app.callback([Output(module+'page1', 'children'),
               Output(module+'store','data')],
              Input(module+'dropdown1', 'value'),
              State(module+'store','data'))
def convert_output(value,thisstore):
    if value=='SBEMImage':
        thisstore['owner']='SBEM'
        return sbem_conv.page, thisstore
    
    else:
        return [html.Br(),'No data type selected.'],thisstore


# sbem = sbem_conv.page


# =============================================
# PROGRESS OUTPUT


collapse_stdout = html.Div(children=[
                html.Br(),
                html.Div(id=module+'job-status',children=['Status of current processing run: ',html.Div(id=module+'get-status',style={"font-family":"Courier New"},children='not running')]),
                html.Br(),
                html.Details([
                    html.Summary('Console output:'),
                    html.Div(id=module+"collapse",                 
                     children=[
                         dcc.Interval(id=module+'interval1', interval=params.idle_interval,
                                      n_intervals=0),
                         dcc.Interval(id=module+'interval2', interval=params.idle_interval,
                                      n_intervals=0),
                         html.Div(id=module+'div-out',children=['Log file: ',html.Div(id=module+'outfile',style={"font-family":"Courier New"})]),
                         dcc.Textarea(id=module+'console-out',className="console_out",
                                      style={'width': '100%','height':200,"color":"#000"},disabled='True')                         
                         ])
                ])
            ],id=module+'consolebox')


@app.callback(Output(module+'console-out','value'),
    [Input(module+'interval1', 'n_intervals'),Input(module+'outfile','children')])
def update_output(n,outfile):    
    data=''
    
    if outfile is not None:
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




@app.callback(Output(module+'store','data'),
     Input(module+'interval2', 'n_intervals'),
     State(module+'store','data'))     
def update_status(a,n,storage):     
    # processes = storage['processes']
    procs=processes[module.strip('_')]
    
    if (type(procs) is subprocess.Popen or len(procs)>0):        
        status = launch_jobs.status(procs)    
        storage['run_state'] = status    
        # storage['processes'] = processes    
    
    return storage


@app.callback([Output(module+'get-status','children'),
              Output(module+'get-status','style'),
              Output(module+'interval1', 'interval')],
              Input(module+'store','data'))
def get_status(storage):
    status_style = {"font-family":"Courier New",'color':'#000'} 
    log_refresh = params.idle_interval
    
    if storage['run_state'] == 'running':        
        status = html.Div([html.Img(src='assets/gears.gif',height=72),html.Br(),'running'])
        log_refresh = params.refresh_interval        
    elif storage['run_state'] == 'input':
        status='process will start on click.'
    elif storage['run_state'] == 'done':
        status='DONE'
    elif storage['run_state'] == 'pending':
        status = 'Waiting for cluster resources to be allocated.'
    elif storage['run_state'] == 'wait':
        status='not running'
    else:
        status=storage['run_state']
    
    return status,status_style,log_refresh



@app.callback(Output(module+'outfile', 'children'),
              [Input(module+'page1', 'children'),
               Input(module+'store', 'data')]
              )
def update_outfile(update,data):           
    return data['log_file']






# Full page layout:
    
page = []
page.append(page1)
page.append(collapse_stdout)

