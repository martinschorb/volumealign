#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 08:42:12 2020

@author: schorb
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State

import os
#for file browsing dialogs
import tkinter
from tkinter import filedialog
import json
import requests
import importlib


from app import app
import params

from utils import launch_jobs, pages, checks

from callbacks import filebrowse


# element prefix
label = "serialem_conv"
parent = "convert"


# SELECT input directory

# get user name and main group to pre-polulate input directory

group = params.group

# ============================
# set up render parameters

owner = "SBEM"


# =============================================
# # Page content


# Pick source directory


directory_sel = html.Div(children=[html.H4("Select dataset metadata file (*.idoc):"),
                                   # html.Script(type="text/javascript",children="alert('test')"),                                   
                                   dcc.Input(id={'component': 'path_input', 'module': label}, type="text", debounce=True,value="/g/"+group,persistence=True,className='dir_textinput')
                                   ])
        
pathbrowse = pages.path_browse(label,show_files=True,file_types='idoc')

page = [directory_sel,pathbrowse]

        



# =============================================
# Start Button


page2 = []

gobutton = html.Div(children=[html.Br(),
                              html.Button('Start conversion',id=label+"go",disabled=True),
                              html.Div([],id=label+'directory-popup',style = {'color':'#E00'}),
                              # dcc.ConfirmDialog(
                              #     id=label+'danger-novaliddir',displayed=False,
                              #     message='The selected directory does not exist or is not readable!'
                              #     ),
                              html.Br(),
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
                                  id=label+'compute')]
                    ,style={'display': 'inline-block'})

page2.append(gobutton)
 



# =============================================
   
#  LAUNCH CALLBACK FUNCTION

# =============================================


@app.callback([Output(label+'go', 'disabled'),
               Output(label+'directory-popup','children'),
               # Output(label+'danger-novaliddir','displayed'),
               # Output({'component': 'store_r_launch', 'module': parent},'data'),
               # Output({'component': 'store_render_launch', 'module': parent},'data')
               ],             
              [Input({'component':'stack_dd','module':parent},'value'),
               Input({'component': 'path_input', 'module': label},'value'),
               Input(label+'go', 'n_clicks')
               ],
              [State({'component':'project_dd','module':parent}, 'value'),
               State(label+'compute_sel','value'),
               State({'component': 'store_run_state', 'module': parent},'data'),
               State({'component': 'store_r_launch', 'module': parent},'data'),
               State({'component': 'store_render_launch', 'module': parent},'data')]
              ,prevent_initial_call=True)
def serialem_conv_gobutton(stack_sel, in_dir, click, proj_dd_sel, compute_sel, run_state,out,outstore):   
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0].partition(label)[2]
    but_disabled = True
    popup = ''
    pop_display = False
    log_file = out['logfile']
    
    # outstore = dash.no_update
    outstore = dict()
    outstore['owner'] = 'SBEM'
    outstore['project'] = proj_dd_sel
    outstore['stack'] = stack_sel
    
    if trigger == 'go':
    # launch procedure                
    
        # prepare parameters:
        
        importlib.reload(params)
            
        param_file = params.json_run_dir + '/' + label + '_' + params.run_prefix + '.json' 
        
        run_params = params.render_json.copy()
        run_params['render']['owner'] = owner
        run_params['render']['project'] = proj_dd_sel
        
        with open(os.path.join(params.json_template_dir,'SBEMImage_importer.json'),'r') as f:
            run_params.update(json.load(f))
        
        run_params['image_directory'] = in_dir
        run_params['stack'] = stack_sel
        
        with open(param_file,'w') as f:
            json.dump(run_params,f,indent=4)
    
        log_file = params.render_log_dir + '/' + 'sbem_conv_' + params.run_prefix
        err_file = log_file + '.err'
        log_file += '.log'
            
            
        #launch
        # -----------------------
        
        sbem_conv_p = launch_jobs.run(target=compute_sel,pyscript='$rendermodules/rendermodules/dataimport/generate_EM_tilespecs_from_SerialEMmontage.py',
                        json=param_file,run_args=None,logfile=log_file,errfile=err_file)
        
        run_state = 'running'
        params.processes[parent.strip('_')] = sbem_conv_p       
        

        
    else:
        # outstore = dash.no_update
    # check launch conditions and enable/disable button    
        if any([in_dir=='',in_dir==None]):
            if not (run_state == 'running'): 
                    run_state = 'wait'
                    params.processes[parent.strip('_')] = []
                    popup = 'No input file chosen.'
                    
        elif os.path.isfile(in_dir): 
            print(in_dir)
            if any([stack_sel=='newstack', proj_dd_sel=='newproj']):
                if not (run_state == 'running'): 
                    run_state = 'wait'
                    params.processes[parent.strip('_')] = []

            else:
                if not (run_state == 'running'): 
                    run_state = 'input'
                    params.processes[parent.strip('_')] = []
                    but_disabled = False
            
        else:
            if not (run_state == 'running'): 
                run_state = 'wait'
                params.processes[parent.strip('_')] = []
                popup = 'Input  Data not accessible.'
                pop_display = True
    
    out['logfile'] = log_file
    out['state'] = run_state
    
    return but_disabled, popup, #pop_display#, out, outstore

        