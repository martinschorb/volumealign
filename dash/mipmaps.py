#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 16:15:27 2020

@author: schorb
"""
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
import params
import json
import requests

from app import app



module='mipmaps_'



main=html.Div(id=module+'main',children=html.H4("Generate MipMaps for Render stack"))


page1 = html.Div(id=module+'page1',children=[html.H4('Current active stack:'),
                                             html.Div('Owner:'),
                                             dcc.Dropdown(id=module+'owner_dd',persistence=True,
                                    clearable=False,value='123')
                                             
                                             ])
     

@app.callback([Output(module+'store','data'),
               Output(module+'owner_dd','options'),
               Output(module+'owner_dd','value')],
              [Input('convert_'+'store','data'),
               Input(module+'page1','children')],
              State(module+'store','data'))
def update_stack_state(prevstore,page,thisstore):   

    for key in ['owner','project','stack']: thisstore[key] = prevstore[key]
    # print('mipmaps-store')
    # print(thisstore)
    
    # get list of projects on render server
    url = params.render_base_url + params.render_version + 'owners'
    owners = requests.get(url).json()
    # print(owners)    
    
    # assemble dropdown
    dd_options = list(dict())
    for item in owners: 
        dd_options.append({'label':item, 'value':item})
    
                 
    return thisstore,dd_options,thisstore['owner']





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
                         dcc.Interval(id=module+'interval1', interval=10000,
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



@app.callback(Output(module+'outfile', 'children'),
              [Input(module+'page1', 'children'),
               Input(module+'store', 'data')]
              )
def update_outfile(update,data):           
    return data['log_file']



@app.callback([Output(module+'get-status','children'),
              Output(module+'get-status','style')],
              Input(module+'store','data'))
def get_status(storage):
    status_style = {"font-family":"Courier New",'color':'#000'} 
    
    if storage['run_state'] == 'running':        
        status = html.Div([html.Img(src='assets/gears.gif',height=72),html.Br(),'running'])        
    elif storage['run_state'] == 'input':
        status='process will start on click.'
    else:
        status='not running'
    
    return status,status_style



# Full page layout:
    
page = []
page.append(page1)
page.append(collapse_stdout)