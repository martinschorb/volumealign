#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate

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

from utils import launch_jobs,pages

# element prefix
label = "sift_pointmatch"
parent = "pointmatch"



page=[]


matchtrial = html.Div([html.H4("Select appropriate Parameters for the SIFT search"),
                       html.Div(['Organism: ',
                       dcc.Dropdown(id=label+'organism_dd',persistence=True,
                                    clearable=False),
                       html.Div(["Select existing Match Trial parameters."
                                 ],
                                id=label+'mt_sel'),
                       dcc.Store(id=label+'picks'),
                       dcc.Dropdown(id=label+'matchID_dd',persistence=True,
                                    clearable=False),
                       html.Div(id=label+'mtbrowse',
                             children=[html.A('Explore MatchTrial',
                                              id=label+'mt_link',
                                              target="_blank",style={'margin-left': '0.5em','margin-right': '1em'}),
                                       ])
                       ])
                                 ])

page.append(matchtrial)


gobutton = html.Div(children=[html.Br(),
                              html.Button('Start PointMatch Client',id=label+"go",disabled=True),
                              pages.compute_loc(parent,c_options = ['sparkslurm','standalone'],
                                                c_default = 'sparkslurm'),
                              ]
                    ,style={'display': 'inline-block'})

page.append(gobutton)
              
#  =============================================
# Start Button
               

@app.callback([Output(label+'organism_dd','options'),
               Output(label+'picks','data')],              
              [Input(parent+'tp_dd','value')],              
              )
def sift_pointmatch_organisms(tilepairdir):
    mT_jsonfiles = os.listdir(params.json_match_dir)
    
    organisms=list()
    
    picks = dict()
    
    for mT_file in mT_jsonfiles:
        with open(os.path.join(params.json_match_dir,mT_file),'r') as f:
            indict = json.load(f)
            if not indict['organism'] in organisms:
                organisms.append(indict['organism'])
                picks[indict['organism']] = [indict['render']]
                picks[indict['organism']][0]['type']=indict['type']
                picks[indict['organism']][0]['ID']=indict['MatchTrial']
            else:
                picks[indict['organism']].append(indict['render'])
                picks[indict['organism']][-1]['type']=indict['type']
                picks[indict['organism']][-1]['ID']=indict['MatchTrial']
    
    dd_options = list(dict())
        
    for item in organisms: 
        dd_options.append({'label':item, 'value':item})

    return dd_options, picks



@app.callback([Output(label+'matchID_dd','options')],              
              [Input(label+'organism_dd','value'),
               Input(label+'picks','data')],              
              prevent_initial_call=True)
def sift_pointmatch_IDs(organism,picks):
    if not dash.callback_context.triggered: 
        raise PreventUpdate
        
    matchtrials = picks[organism]
        
    dd_options = list(dict())
        
    for item in matchtrials: 
        ilabel = item['project']+'-'+item['stack']+'-'+item['type']
        dd_options.append({'label':ilabel, 'value':item['ID']})
    
    return [dd_options]
    

@app.callback([Output(label+'mt_link','href')],              
              Input(label+'matchID_dd','value'),
               # State(label+'picks','data'),              
              prevent_initial_call=True)
def sift_browse_matchTrial(matchID):
    
    mc_url = params.render_base_url + 'view/match-trial.html?'
    mc_url += 'matchTrialId=' + matchID

            
    return [mc_url]


# =============================================
   
#  LAUNCH CALLBACK FUNCTION

# =============================================
  
    

# @app.callback([Output(label+'go', 'disabled'),
#                 Output(parent+'store','data'),
#                 Output(parent+'interval1','interval')
#                 ],
#               Input(label+'go', 'n_clicks'),
#               [State(label+'input1','value'),               
#                 State(label+'project_dd', 'value'),
#                 State(label+'stack_state', 'children'),
#                 State(label+'compute_sel','value'),
#                 State(parent+'store','data')]
#               )                 

# def sift_pointmatch_execute_gobutton(click,sbemdir,proj_dd_sel,stack_sel,compute_sel,storage):    
#     # prepare parameters:∂
    
#     importlib.reload(params)
        
#     param_file = params.json_run_dir + '/' + label + params.run_prefix + '.json' 
    
#     run_params = params.render_json.copy()

#     run_params['render']['project'] = proj_dd_sel
    
#     with open(os.path.join(params.json_template_dir,'SBEMImage_importer.json'),'r') as f:
#         run_params.update(json.load(f))
    
#     run_params['image_directory'] = sbemdir
#     run_params['stack'] = stack_sel
    
#     with open(param_file,'w') as f:
#         json.dump(run_params,f,indent=4)

#     log_file = params.render_log_dir + '/' + 'sbem_conv-' + params.run_prefix
#     err_file = log_file + '.err'
#     log_file += '.log'
    

        
#     #launch
#     # -----------------------
    
#     sbem_conv_p = launch_jobs.run(target=compute_sel,pyscript='$rendermodules/rendermodules/dataimport/generate_EM_tilespecs_from_SBEMImage.py',
#                     json=param_file,run_args=None,logfile=log_file,errfile=err_file)
    
    
    
#     storage['log_file'] = log_file
#     storage['run_state'] = 'running'
#     params.processes[parent.strip('_')] = sbem_conv_p
    

#     return True,storage,params.refresh_interval

