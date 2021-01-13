#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""

import dash_core_components as dcc
import dash_html_components as html
import subprocess
# import sys
import os
import socket
#for file browsing dialogs
import tkinter
from tkinter import filedialog

from dash.dependencies import Input,Output,State

import json
import requests
import importlib


from app import app
import params
from utils import launch_jobs

# element prefix
label = "sbem_conv_"
parent = "convert_"






gobutton = html.Div(children=[html.Br(),
                              html.Button('Start conversion',id=label+"go",disabled=True),
                              html.Details([html.Summary('Compute location:'),
                                            dcc.RadioItems(
                                                options=[
                                                    {'label': 'Cluster (slurm)', 'value': 'slurm'},
                                                    {'label': 'locally (this submission node)', 'value': 'standalone'}
                                                ],
                                                value='slurm',
                                                labelStyle={'display': 'inline-block'},
                                                id=label+'compute_sel'
                                                )],
                                  id=label+'compute'),
                              html.Div(id=label+'directory-popup')]
                    ,style={'display': 'inline-block'})
              
#  =============================================
# Start Button
               

@app.callback([Output(label+'go', 'disabled'),
                Output(label+'directory-popup','children'),
                Output(parent+'store','data')],              
              [Input(label+'stack_state', 'children'),
                Input(label+'input1','value')],
              [State(label+'project_dd', 'value'),
                State(parent+'store','data')],
              )
def sift_pointmatch_activate_gobutton(stack_state1,in_dir,proj_dd_sel1,storage):   

    out_pop=dcc.ConfirmDialog(        
        id=label+'danger-novaliddir',displayed=True,
        message='The selected directory does not exist or is not readable!'
        )
    if any([in_dir=='',in_dir==None]):
        if not (storage['run_state'] == 'running'): 
                storage['run_state'] = 'wait'
                params.processes[parent.strip('_')] = []
        return True,'No input directory chosen.',storage
    elif os.path.isdir(in_dir):        
        if any([stack_state1=='newstack', proj_dd_sel1=='newproj']):
            if not (storage['run_state'] == 'running'): 
                storage['run_state'] = 'wait'
                params.processes[parent.strip('_')] = []
            return True,'',storage
        else:
            if not (storage['run_state'] == 'running'): 
                storage['run_state'] = 'input'
                params.processes[parent.strip('_')] = []
            return False,'',storage
        
    else:
        if not (storage['run_state'] == 'running'): 
            storage['run_state'] = 'wait'
            params.processes[parent.strip('_')] = []
        return True, out_pop,storage
    
    

@app.callback(Output(label+'input1','value'),
              [Input(label+'danger-novaliddir','submit_n_clicks'),
                Input(label+'danger-novaliddir','cancel_n_clicks')])
def sift_pointmatch_dir_warning(sub_c,canc_c):
    return ''
        
    
    
# =============================================
   
#  LAUNCH CALLBACK FUNCTION

# =============================================
  
    

@app.callback([Output(label+'go', 'disabled'),
                Output(parent+'store','data'),
                Output(parent+'interval1','interval')
                ],
              Input(label+'go', 'n_clicks'),
              [State(label+'input1','value'),               
                State(label+'project_dd', 'value'),
                State(label+'stack_state', 'children'),
                State(label+'compute_sel','value'),
                State(parent+'store','data')]
              )                 

def sift_pointmatch_execute_gobutton(click,sbemdir,proj_dd_sel,stack_sel,compute_sel,storage):    
    # prepare parameters:∂
    
    importlib.reload(params)
        
    param_file = params.json_run_dir + '/' + label + params.run_prefix + '.json' 
    
    run_params = params.render_json.copy()

    run_params['render']['project'] = proj_dd_sel
    
    with open(os.path.join(params.json_template_dir,'SBEMImage_importer.json'),'r') as f:
        run_params.update(json.load(f))
    
    run_params['image_directory'] = sbemdir
    run_params['stack'] = stack_sel
    
    with open(param_file,'w') as f:
        json.dump(run_params,f,indent=4)

    log_file = params.render_log_dir + '/' + 'sbem_conv-' + params.run_prefix
    err_file = log_file + '.err'
    log_file += '.log'
    

        
    #launch
    # -----------------------
    
    sbem_conv_p = launch_jobs.run(target=compute_sel,pyscript='$rendermodules/rendermodules/dataimport/generate_EM_tilespecs_from_SBEMImage.py',
                    json=param_file,run_args=None,logfile=log_file,errfile=err_file)
    
    
    
    storage['log_file'] = log_file
    storage['run_state'] = 'running'
    params.processes[parent.strip('_')] = sbem_conv_p
    

    return True,storage,params.refresh_interval


        


# ---- page layout

page = html.Div([gobutton])