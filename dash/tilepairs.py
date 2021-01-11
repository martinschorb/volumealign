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
import os
import subprocess

from app import app
from utils import launch_jobs

import importlib




module='tilepairs_'




main=html.Div(id=module+'main',children=html.H3("Generate TilePairs for Render stack"))

intervals = html.Div([dcc.Interval(id=module+'interval1', interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Interval(id=module+'interval2', interval=params.idle_interval,
                                       n_intervals=0),
                      html.Div(id='runstep',style={'display':'none'}),
                      dcc.Store(id=module+'tmpstore')
                      ])

page1 = html.Div(id=module+'page1',children=[html.H4('Current active stack:'),
                                             html.Div([html.Div('Owner:',style={'margin-right': '1em','margin-left': '2em'}),
                                                       dcc.Dropdown(id=module+'owner_dd',className='dropdown_inline',style={'width':'120px'},
                                                          persistence=True,
                                                          clearable=False),
                                                       html.Div('Project',style={'margin-left': '2em'}),
                                                       html.A('(Browse)',id=module+'browse_proj',target="_blank",style={'margin-left': '0.5em','margin-right': '1em'}),
                                                       dcc.Dropdown(id=module+'project_dd',className='dropdown_inline',
                                                          persistence=True,
                                                          clearable=False),
                                                       html.Div('Stack',style={'margin-left': '2em'}),
                                                       html.A('(Browse)',id=module+'browse_stack',target="_blank",style={'margin-left': '0.5em','margin-right': '1em'}),
                                                       dcc.Dropdown(id=module+'stack_dd',className='dropdown_inline',
                                                          persistence=True,
                                                          clearable=False)
                                             
                                             ],style=dict(display='flex'))
                                             ])


page2 = html.Div(id=module+'page2',children=[html.H3('Directory to store tilepair file:'),
                                             dcc.Input(id=module+"input1", type="text",debounce=True,persistence=True,className='dir_textinput'),
                                             html.Button('Browse',id=module+"browse1"),
                                             'graphical browsing works on cluster login node ONLY!',
                                             html.Br()])





@app.callback([Output(module+'owner_dd','options'),
               Output(module+'store','data'),               
               Output(module+'owner_dd','value'),
                Output(module+'project_dd','value'),
                Output(module+'stack_dd','value')
               ],
              [Input('mipmaps_'+'store','data'),
               Input('url', 'pathname')],
              State(module+'store','data'))
def tilepairs_update_stack_state(prevstore,page,thisstore):  
    for key in ['owner','project','stack']: thisstore[key] = prevstore[key]
    # print('mipmaps-store')
    # print(thisstore)
    # print(thisstore['stack'])
    # get list of projects on render server
    
    
    url = params.render_base_url + params.render_version + 'owners'
    owners = requests.get(url).json() 
    
    url = params.render_base_url + params.render_version + 'owner/' + thisstore['owner'] + '/project/' + thisstore['project'] + '/stacks'
    stacks = requests.get(url).json()
    thisstore['allstacks'] = stacks
    
    # assemble dropdown
    dd_options = list(dict())
    for item in owners: 
        dd_options.append({'label':item, 'value':item})
    
    thisstore['run_state'] = 'wait'
    
    if thisstore['stack']+'_mipmaps' in  [stacks[i]['stackId']['stack'] for i in range(len(stacks))]:
        thisstore['stack'] = thisstore['stack']+'_mipmaps'

    return dd_options,thisstore,thisstore['owner'],thisstore['project'],thisstore['stack']



###  SELECT STACK TO WORK....
##============================================================
#dropdown callback
@app.callback([Output(module+'browse_proj','href'),
               Output(module+'project_dd','options'),
               Output(module+'store','data')],
    Input(module+'owner_dd', 'value'),
    State(module+'store','data'))
def tilepairs_own_dd_sel(owner_sel,thisstore):
    href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+owner_sel

   # get list of projects on render server
    url = params.render_base_url + params.render_version + 'owner/' + owner_sel + '/projects'
    projects = requests.get(url).json()

    # assemble dropdown
    dd_options = list(dict())
    for item in projects: 
        dd_options.append({'label':item, 'value':item})
    
    thisstore['owner'] = owner_sel
    
    return href_out, dd_options, thisstore


#dropdown callback
@app.callback([Output(module+'browse_stack','href'),
               Output(module+'stack_dd','options'),
               Output(module+'store','data')],
              Input(module+'project_dd', 'value'),
              State(module+'store','data'))
def tilepairs_proj_dd_sel(proj_sel,thisstore): 
        
    href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+thisstore['owner']+'&renderStackProject='+proj_sel
   # get list of projects on render server
    url = params.render_base_url + params.render_version + 'owner/' + thisstore['owner'] + '/project/' + proj_sel + '/stacks'
    stacks = requests.get(url).json()
     
    # assemble dropdown
    dd_options = list(dict())
    for item in stacks: dd_options.append({'label':item['stackId']['stack'], 'value':item['stackId']['stack']})

    
    thisstore['project'] = proj_sel
    thisstore['allstacks'] = stacks

    return href_out, dd_options, thisstore


# ===============================================




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
        if not 'Error' in status:
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
              Output(module+'interval1', 'interval'),
              Output('runstep','children')],
              Input(module+'store','data'),
               [State('runstep','children'),
               State(module+'compute_sel','value'),
               State(module+'input1','value')])
def tilepairs_get_status(storage,runstep,comp_sel,mipmapdir):
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
    
    
    return status,status_style,log_refresh,runstep




@app.callback([Output(module+'get-status','children'),
               Output(module+'store','data')],
              Input(module+'cancel', 'n_clicks'),
              State(module+'store','data'))
def tilepairs_cancel_jobs(click,storage):

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
def tilepairs_update_output(n,outfile):
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
def tilepairs_update_outfile(update,data):           
    return data['log_file']



# Full page layout:
    
page = [intervals,page1, page2]#, gobutton]
page.append(collapse_stdout)