#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 08:42:12 2020

@author: schorb
"""
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input,Output,State
from dash.exceptions import PreventUpdate

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
from utils import helper_functions as hf
from utils.checks import is_bad_filename

from callbacks import filebrowse,render_selector


# element prefix
parent = "convert"

label = parent+"_SBEM"

# SELECT input directory

# get user name and main group to pre-polulate input directory

group = params.group

# ============================
# set up render parameters

owner = "SBEM"


# =============================================
# # Page content


store = pages.init_store({}, label)


# Pick source directory


directory_sel = html.Div(children=[html.H4("Select dataset root directory:"),
                                   # html.Script(type="text/javascript",children="alert('test')"),                                   
                                   dcc.Input(id={'component': 'path_input', 'module': label}, type="text", debounce=True,value="/g/"+group,persistence=True,className='dir_textinput')
                                   ])
        
pathbrowse = pages.path_browse(label)

page1 = [directory_sel,pathbrowse,html.Div(store)]




# # ===============================================
#  RENDER STACK SELECTOR


# Pre-fill render stack selection from previous module

us_out,us_in,us_state = render_selector.init_update_store(label,parent,comp_in='store_render_init')

@app.callback(us_out,us_in,us_state)
def sbem_conv_update_store(*args):
    thispage = args[-1]
    args = args[:-1]
    thispage = thispage.lstrip('/')

    if thispage=='' or not thispage in hf.trigger(key='module'):
        raise PreventUpdate

    return render_selector.update_store(*args)


page2 = []
page2.append(html.Div(pages.render_selector(label,create=True,show=['stack','project'],header='Select target stack:'),
                 id={'component':'render_seldiv','module':label})
             )




# =============================================
# Start Button


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
# Processing status

# initialized with store
# embedded from callbacks import runstate

# # =============================================
# # PROGRESS OUTPUT


collapse_stdout = pages.log_output(label)

# ----------------

# Full page layout:
    

page2.append(collapse_stdout)



# =============================================
   
#  LAUNCH CALLBACK FUNCTION

# =============================================


@app.callback([Output(label+'go', 'disabled'),
               Output(label+'directory-popup','children'),
               # Output(label+'danger-novaliddir','displayed'),
               Output({'component': 'store_launch_status', 'module': label},'data'),
               Output({'component': 'store_render_launch', 'module': label},'data')
               ],             
              [Input({'component':'stack_dd','module':label},'value'),
               Input({'component': 'path_input', 'module': label},'value'),
               Input(label+'go', 'n_clicks')
               ],
              [State({'component':'project_dd','module':label}, 'value'),
               State(label+'compute_sel','value'),
               State({'component': 'store_run_status', 'module': label},'data'),               
               State({'component': 'store_render_launch', 'module': label},'data')]
              ,prevent_initial_call=True)
def sbem_conv_gobutton(stack_sel, in_dir, click, proj_dd_sel, compute_sel, run_state,outstore):   
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0].partition(label)[2]
    but_disabled = True
    popup = ''
    out=run_state
    log_file = run_state['logfile']
    
    # outstore = dash.no_update
    outstore = dict()
    outstore['owner'] = 'SBEM'
    outstore['project'] = proj_dd_sel
    outstore['stack'] = stack_sel
    
    if trigger == 'go':
    # launch procedure                
    
        # prepare parameters:
        run_prefix = launch_jobs.run_prefix()
            
        param_file = params.json_run_dir + '/' + label + '_' + run_prefix + '.json' 
        
        run_params = params.render_json.copy()
        run_params['render']['owner'] = owner
        run_params['render']['project'] = proj_dd_sel
        
        with open(os.path.join(params.json_template_dir,'SBEMImage_importer.json'),'r') as f:
            run_params.update(json.load(f))
        
        run_params['image_directory'] = in_dir
        run_params['stack'] = stack_sel
        
        with open(param_file,'w') as f:
            json.dump(run_params,f,indent=4)
    
        log_file = params.render_log_dir + '/' + 'sbem_conv_' + run_prefix
        err_file = log_file + '.err'
        log_file += '.log'
            
            
        #launch
        # -----------------------

        sbem_conv_p = launch_jobs.run(target=compute_sel,pyscript=params.rendermodules_dir+'/dataimport/generate_EM_tilespecs_from_SBEMImage.py',
                        jsonfile=param_file,run_args=None,logfile=log_file,errfile=err_file)
                       
        run_state['status'] = 'running'     
        run_state['id'] = sbem_conv_p
        run_state['type'] = compute_sel
        run_state['logfile'] = log_file
                
    else:
        
        # outstore = dash.no_update
    # check launch conditions and enable/disable button    
        if any([in_dir=='',in_dir==None]):
            if not (run_state['status'] == 'running'): 
                    run_state['status'] = 'wait'
                    popup = 'No input directory chosen.'

        elif is_bad_filename(in_dir):
            run_state['status'] = 'wait'
            popup = 'Wrong characters in input directory path. Please fix!'

        elif os.path.isdir(in_dir): 
            
            if any([stack_sel=='newstack', proj_dd_sel=='newproj']):
                if not (run_state['status'] == 'running'): 
                    run_state['status'] = 'wait'

            else:
                if not (run_state['status'] == 'running'): 
                    run_state['status'] = 'input'
                    but_disabled = False
            
        else:
            if not (run_state['status'] == 'running'): 
                run_state['status'] = 'wait'
                popup = 'Directory not accessible.'
                # pop_display = True

    return but_disabled, popup, out, outstore

        
        