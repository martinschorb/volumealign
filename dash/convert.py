#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
# import os
import params
import subprocess

from app import app

from sbem import sbem_conv
from utils import launch_jobs


module='convert_'


main = html.Div(children=[html.H3("Import volume EM datasets - Choose type:",id='conv_head'),dcc.Dropdown(
        id=module+'dropdown1',persistence=True,
        options=[
            {'label': 'SBEMImage', 'value': 'SBEMImage'}            
        ],
        value='SBEMImage'
        )    
    ])


intervals = html.Div([dcc.Interval(id=module+'interval1', interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Interval(id=module+'interval2', interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Store(id=module+'tmpstore')
                      ])

junk = html.Div(id=module+'junk')

page1 = html.Div(id=module+'page1')


# =============================================
# # Page content

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



# =============================================
# Processing status



@app.callback([Output(module+'interval2','interval'),
               Output(module+'store','data')],
              Input(module+'interval2','n_intervals'),
              State(module+'store','data'))
def convert_update_status(n,storage):  
    if n>0:        
        status = storage['run_state']
        procs=params.processes[module.strip('_')]
        if procs==[]:
            if storage['run_state'] not in ['input','wait']:
                storage['run_state'] = 'input'               
        
        if (type(procs) is subprocess.Popen or len(procs)>0): 
            status = launch_jobs.status(procs)   
            storage['run_state'] = status    

        if 'Error' in status:
            if storage['log_file'].endswith('.log'):
                storage['log_file'] = storage['log_file'][:storage['log_file'].rfind('.log')]+'.err'
            
    return params.idle_interval,storage 
    

cancelbutton = html.Button('cancel cluster job(s)',id=module+"cancel")


@app.callback([Output(module+'get-status','children'),
              Output(module+'get-status','style'),
              Output(module+'interval1', 'interval')],
              Input(module+'store','data'))
def convert_get_status(storage):
    status_style = {"font-family":"Courier New",'color':'#000'} 
    log_refresh = params.idle_interval
    procs=params.processes[module.strip('_')]    
    if storage['run_state'] == 'running':        
        if procs == []:
            status = 'not running'
        else:
            status = html.Div([html.Img(src='assets/gears.gif',height=72),html.Br(),'running'])
            log_refresh = params.refresh_interval
            if not type(procs) is subprocess.Popen:
               if  type(procs) is str:
                   status = html.Div([html.Img(src='assets/gears.gif',height=72),html.Br(),'running  -  ',cancelbutton])
               elif not type(procs[0]) is subprocess.Popen:
                   status = html.Div([html.Img(src='assets/gears.gif',height=72),html.Br(),'running  -  ',cancelbutton])
    elif storage['run_state'] == 'input':
        status='process will start on click.'
    elif storage['run_state'] == 'done':
        status='DONE'
        status_style = {'color':'#0E0'}
    elif storage['run_state'] == 'pending':
        status = ['Waiting for cluster resources to be allocated.',cancelbutton]
    elif storage['run_state'] == 'wait':
        status='not running'
    else:
        status=storage['run_state']
    
    
    return status,status_style,log_refresh



@app.callback([Output(module+'get-status','children'),
               Output(module+'store','data')],
              Input(module+'cancel', 'n_clicks'),
              State(module+'store','data'))
def convert_cancel_jobs(click,storage):

    procs = params.processes[module.strip('_')]
    
    p_status = launch_jobs.canceljobs(procs)
    
    params.processes[module.strip('_')] = []    
    
    storage['run_state'] = p_status
    
    return p_status,storage
    
    



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
                          html.Div(id=module+'div-out',children=['Log file: ',html.Div(id=module+'outfile',style={"font-family":"Courier New"})]),
                          dcc.Textarea(id=module+'console-out',className="console_out",
                                      style={'width': '100%','height':200,"color":"#000"},disabled='True')                         
                          ])
                ])
            ],id=module+'consolebox')


@app.callback(Output(module+'console-out','value'),
    [Input(module+'interval1', 'n_intervals'),Input(module+'outfile','children')])
def convert_update_output(n,outfile):    
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





@app.callback(Output(module+'outfile', 'children'),
              [Input(module+'page1', 'children'),
                Input(module+'store', 'data')]
              )
def convert_update_outfile(update,data):           
    return data['log_file']




# @app.callback(Output('test','children'),
#               Input(module+'interval2','n_intervals')
#               )
# def check_interval1(n):
#     print('this is interval 1:')
#     print(n)
#     return str(n)



# @app.callback(Output('test2','children'),
#               Input(module+'interval2','n_intervals')
#               )
# def check_interval2(n):
#     print('this is interval 2 bottom:')
#     print(n)
#     return str(n)


# Full page layout:
    
page = []
page.append(intervals)
page.append(page1)
page.append(collapse_stdout)

