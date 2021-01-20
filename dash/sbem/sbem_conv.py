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
import socket
#for file browsing dialogs
import tkinter
from tkinter import filedialog
import json
import requests
import importlib


from app import app
import params
from utils import launch_jobs


# element prefix
label = "sbem_conv"
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


directory_sel = html.Div(children=[html.H4("Select dataset root directory:"),
                                   html.Script(type="text/javascript",children="alert('test')"),                                   
                                   dcc.Input(id=label+"input1", type="text", debounce=True,placeholder="/g/"+group,persistence=True,className='dir_textinput'),
                                   html.Button('Browse',id=label+"browse1"),' graphical browsing works on cluster login node ONLY!',
                                   html.Div(id=label+'warning-popup')
                                   ])

page = [directory_sel]

@app.callback([Output(label+'input1', 'value'),
                Output(label+'warning-popup','children')],
              [Input(label+'browse1', 'n_clicks'),
                Input(label+'danger-novaliddir','submit_n_clicks'),
                Input(label+'danger-novaliddir','cancel_n_clicks')])
def sbem_conv_convert_filebrowse1(browse_click,popupclick1,popupclick2):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0].partition(label)[2]
    outpage=''
    conv_inputdir = ''
    
    if 'browse1'in trigger:        
        hostname = socket.gethostname()
    
        if hostname=='login-gui02.cluster.embl.de':    
            root = tkinter.Tk()
            root.withdraw()
            conv_inputdir = filedialog.askdirectory()
            root.destroy()
            outpage=''
        else:
            outpage=dcc.ConfirmDialog(        
            id=label+'danger-wrong_host',displayed=True,
            message='This functionality only works when accessing this page from the graphical login node.'
            )
               
    return conv_inputdir, outpage 

   


#------------------

# SET PROJECT



# assemble dropdown
url = params.render_base_url + params.render_version + 'owner/' + owner + '/projects'
projects = requests.get(url).json()

orig_projdiv=html.Div(id=label+'orig_proj',style={'display':'none'},children=projects)
   
        

proj_dd_options = [{'label':'Create new Project', 'value':'newproj'}]
for item in projects: 
    proj_dd_options.append({'label':item, 'value':item})
       
project_dd = html.Div([html.H4("Select Render Project:"),
                        dcc.Dropdown(id=label+'project_dd',persistence=True,
                                    options=proj_dd_options,clearable=False),
                        html.Br(),
                        html.Div(['Enter new project name: ',
                                  dcc.Input(id=label+"proj_input", type="text", debounce=True,placeholder="new_project",persistence=False)
                                  ],
                                id=label+'render_project',style={'display':'none'}),                               
                        html.Div([html.Br(),html.A('Browse Project',href=params.render_base_url+'view/stacks.html?renderStackOwner='+owner,
                                id=label+'browse_proj',target="_blank")]),
                        orig_projdiv
                        ])
page.append(project_dd)

                       
#dropdown callback

# Fills the project DropDown

@app.callback([Output(label+'browse_proj','href'),
                Output(label+'render_project','style')],
              Input(label+'project_dd', 'value'))
def sbem_conv_proj_dd_sel(project_sel):
    divstyle = {'display':'none'}
    href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+owner
    
    if not (project_sel is None):
        if project_sel=='newproj':       
            divstyle = {'display':'block'}                       
        else:            
            href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+owner+'&renderStackProject='+project_sel
    
    return href_out, divstyle


# Create a new Project

@app.callback([Output(label+'project_dd', 'options'),
                Output(label+'project_dd', 'value')],
              Input(label+'proj_input', 'value'),
              State(label+'project_dd', 'options'))
def sbem_conv_new_proj(project_name,dd_options): 
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id']
    if trigger != '.':        
        # get list of projects on render server            
        dd_options.append({'label':project_name, 'value':project_name})

    return dd_options,project_name



#------------------
# SET STACK


# assemble dropdown

stack_div = html.Div(id=label+'sbem_conv_stack_div',children=[html.H4("Select Render Stack:"),
                                                              dcc.Dropdown(id=label+'stack_dd',persistence=True,
                                                                            clearable=False,style={'display':'none'}),
                                                              html.Div(children=['Enter new stack name: ',
                                                                                  dcc.Input(id=label+"stack_input", type="text", debounce=True,placeholder="new_stack",persistence=False)
                                                                                  ],id=label+'newstack',style={'display':'none'}),
                                                              html.Br(),                                                          
                                                              html.A('Browse Stack',href=params.render_base_url+'view/stacks.html?renderStackOwner='+owner,
                                                                      id=label+'browse_stack',target="_blank"),
                                                              html.Br(),]
                        )

page.append(stack_div)

#dropdown callback

# Fills the Stack DropDown

@app.callback([Output(label+'stack_dd','options'),   
                Output(label+'stack_dd','style'), 
                Output(label+'stack_dd','value'),
                ],
              [Input(label+'project_dd', 'value'),               
                Input(label+'stack_input', 'value')],
              [State(label+'orig_proj','children'),
                State(label+'stack_dd', 'options')])    
def sbem_conv_stacks(project_sel,newstack_name,orig_proj,dd_options):    
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0].partition(label)[2]
    dd_style = {'display':'block'}    
    stack = 'newstack'

    if trigger == 'project_dd':
        dd_options = [{'label':'Create new Stack', 'value':'newstack'}]
        
        if project_sel in orig_proj:
            # get list of STACKS on render server
            url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project_sel + '/stacks'
            stacks = requests.get(url).json()  
            
            # assemble dropdown
            
            for item in stacks: dd_options.append({'label':item['stackId']['stack'], 'value':item['stackId']['stack']})
            
            
            stack = stacks[0]['stackId']['stack']
            
        else:    
            dd_style = {'display':'none'}
            
            
            
    elif trigger == 'stack_input':
        dd_options.append({'label':newstack_name, 'value':newstack_name})
        stack = newstack_name

    return dd_options, dd_style, stack

    
    
@app.callback([Output(label+'browse_stack','href'),
                Output(label+'browse_stack','style')],
              Input(label+'stack_dd','value'),
              State(label+'project_dd', 'value'))
def sbem_conv_update_stack_browse(stack_state,project_sel):      
    if stack_state == 'newstack':
        return params.render_base_url, {'display':'none'}
    else:
        return params.render_base_url+'view/stack-details.html?renderStackOwner='+owner+'&renderStackProject='+project_sel+'&renderStack='+stack_state, {'display':'block'}
                                


# Create a new Stack
    
@app.callback(Output(label+'newstack','style'),
              Input(label+'stack_dd','value'))
def sbem_conv_new_stack_input(stack_value):
    if stack_value=='newstack':
        style={'display':'block'}
    else:
        style={'display':'none'}
    
    return style



# =============================================
# Start Button

gobutton = html.Div(children=[html.Br(),
                              html.Button('Start conversion',id=label+"go",disabled=True),
                              html.Div([],id=label+'directory-popup',style = {'color':'#E00'}),
                              dcc.ConfirmDialog(
                                  id=label+'danger-novaliddir',displayed=False,
                                  message='The selected directory does not exist or is not readable!'
                                  ),
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

page.append(gobutton)
 



# =============================================
   
#  LAUNCH CALLBACK FUNCTION

# =============================================


@app.callback([Output(label+'go', 'disabled'),
                Output(label+'directory-popup','children'),
                Output(label+'danger-novaliddir','displayed'),
                Output({'component': 'store_r_launch', 'module': parent},'data')
                ],             
              [Input(label+'stack_dd','value'),
                Input(label+'input1','value'),
                Input(label+'go', 'n_clicks')
                ],
              [State(label+'project_dd', 'value'),
                State(label+'compute_sel','value'),
                State({'component': 'store_run_state', 'module': parent},'data'),
                State({'component': 'store_r_launch', 'module': parent},'data')],
                )
def sbem_conv_gobutton(stack_sel, in_dir, click, proj_dd_sel, compute_sel, run_state,out):   
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0].partition(label)[2]
    but_disabled = True
    popup = ''
    pop_display = False
    log_file = out['logfile']

    if trigger == 'go':
    # launch procedure                
    
        # prepare parameters:
        
        importlib.reload(params)
            
        param_file = params.json_run_dir + '/' + label + params.run_prefix + '.json' 
        
        run_params = params.render_json.copy()
        run_params['render']['owner'] = owner
        run_params['render']['project'] = proj_dd_sel
        
        with open(os.path.join(params.json_template_dir,'SBEMImage_importer.json'),'r') as f:
            run_params.update(json.load(f))
        
        run_params['image_directory'] = in_dir
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
        
        run_state = 'running'
        params.processes[parent.strip('_')] = sbem_conv_p
        

        
    else:
    # check launch conditions and enable/disable button    
        if any([in_dir=='',in_dir==None]):
            if not (run_state == 'running'): 
                    run_state = 'wait'
                    params.processes[parent.strip('_')] = []
                    popup = 'No input directory chosen.'
                    
        elif os.path.isdir(in_dir):        
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
                popup = 'Directory not accessible.'
                pop_display = True
    
    out['logfile'] = log_file
    out['state'] = run_state
    
    return but_disabled, popup, pop_display, out

        