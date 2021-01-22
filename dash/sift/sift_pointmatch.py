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
from dash.dependencies import Input,Output,State

# import sys
import os
import json
import importlib


from app import app
import params

from utils import pages,matchTrial

from utils import helper_functions as hf


# element prefix
label = "sift_pointmatch"
parent = "pointmatch"



page=[]


matchtrial = html.Div([html.H4("Select appropriate Parameters for the SIFT search"),
                       html.Div(['Organism: ',
                       dcc.Dropdown(id=label+'organism_dd',persistence=True,
                                    clearable=False),
                       html.Br(),
                       html.Div(["Select existing Match Trial parameters."
                                 ],
                                id=label+'mt_sel'),
                       dcc.Store(id=label+'picks'),
                       dcc.Dropdown(id=label+'matchID_dd',persistence=True,
                                    clearable=False),
                       html.Br(),
                       html.Div(id=label+'mtbrowse',
                             children=[html.A('Explore MatchTrial',
                                              id=label+'mt_link',
                                              target="_blank"),                                      
                                       ]),
                       html.Br(),
                       html.Div(["Use this Match Trial as compute parameters:",
                                 dcc.Input(id=label+'mtselect', type="text",
                                 style={'margin-right': '1em','margin-left': '3em'},
                                 debounce=True,placeholder="MatchTrial ID",persistence=False)],style={'display':'flex'}),
                       html.Br()
                       ])
                                 ])

page.append(matchtrial)


gobutton = html.Div(children=[html.Br(),
                              html.Button('Start PointMatch Client',id=label+"go"),
                              pages.compute_loc(parent,c_options = ['sparkslurm','standalone'],
                                                c_default = 'sparkslurm'),
                              html.Div(id=label+'mtnotfound')
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
    

@app.callback([Output(label+'mt_link','href'),
               Output(label+'mtselect','value')],              
              Input(label+'matchID_dd','value'),
               # State(label+'picks','data'),              
              )
def sift_browse_matchTrial(matchID):
    
    mc_url = params.render_base_url + 'view/match-trial.html?'
    mc_url += 'matchTrialId=' + matchID

            
    return mc_url, matchID


# =============================================
   
#  LAUNCH CALLBACK FUNCTION

# =============================================
  

@app.callback([Output(label+'go', 'disabled'),
               Output(label+'mtnotfound','children'),
               Output({'component': 'store_r_launch', 'module': parent},'data'),
               Output({'component': 'store_render_launch', 'module': parent},'data')],
              [Input(label+'go', 'n_clicks'),
               Input(label+'mtselect','value')],
              [State({'component':'store_owner','module' : parent},'data'),
                State({'component':'store_project','module' : parent},'data'),
                State({'component':'stack_dd','module' : parent},'value')]
              ,prevent_initial_call=True)                 
def tilepairs_execute_gobutton(click,matchID,owner,project,stack): 
    ctx = dash.callback_context
        
    trigger = ctx.triggered[0]['prop_id']
    
    if 'mtselect' in trigger:
        return False,'',dash.no_update,dash.no_update
        
    
    elif 'go' in trigger:
        if click is None: return dash.no_update
        
        # prepare parameters:
        importlib.reload(params)
    
        run_params = params.render_json.copy()
        run_params['render']['owner'] = owner
        run_params['render']['project'] = project
        
        run_params_generate = run_params.copy()
        

        try:
            mt_params = matchTrial.mt_parameters(matchID)
        except json.JSONDecodeError:
            return True,'Could not find this MatchTrial ID!',dash.no_update,dash.no_update
            
        
        
        
        #generate script call...
        
        
        with open(os.path.join(params.json_template_dir,'tilepairs.json'),'r') as f:
                run_params_generate.update(json.load(f))
        
        # run_params_generate['output_json'] = tilepairdir + '/tiles_'+ stack
        
        # run_params_generate['minZ'] = startsection
        # run_params_generate['maxZ'] = endsection
        
        run_params_generate['stack'] = stack
        
        # if pairmode == '2D':
        #     run_params_generate['zNeighborDistance'] = 0
        #     run_params_generate['excludeSameLayerNeighbors'] = 'False'
            
        # elif pairmode == '3D':
        #     run_params_generate['zNeighborDistance'] = slicedepth
        #     run_params_generate['excludeSameLayerNeighbors'] = 'True'
    
    
        param_file = params.json_run_dir + '/' + parent + '_' + params.run_prefix + '.json' 
    
               
        with open(param_file,'w') as f:
            json.dump(run_params_generate,f,indent=4)
    
        log_file = params.render_log_dir + '/' + parent + '_' + params.run_prefix
        err_file = log_file + '.err'
        log_file += '.log'
        
        # tilepairs_generate_p = launch_jobs.run(target=comp_sel,pyscript='$rendermodules/rendermodules/pointmatch/create_tilepairs.py',
                            # json=param_file,run_args=None,target_args=None,logfile=log_file,errfile=err_file)
            
        # params.processes[parent].extend(tilepairs_generate_p)
        
        
        print(run_params)
        
        launch_store=dict()
        launch_store['logfile'] = log_file
        launch_store['state'] = 'running'
        
        outstore = dict()
        outstore['owner'] = owner
        outstore['project'] = project
        outstore['stack'] = stack
    
        return True,'', launch_store, outstore

    
