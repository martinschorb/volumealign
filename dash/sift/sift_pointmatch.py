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

from utils import pages,matchTrial,launch_jobs

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
                       pages.tile_view(parent,numpanel=2,showlink=True),
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
                              pages.compute_loc(parent,c_options = ['sparkslurm'],#'standalone'],
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
        
    dd_options = list(dict())
    
    if not organism is None:
        matchtrials = picks[organism]
       
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
    if matchID is None:
        return dash.no_update
    
    mc_url = params.render_base_url + 'view/match-trial.html?'
    mc_url += 'matchTrialId=' + matchID

            
    return mc_url, matchID


# =============================================
   
#  LAUNCH CALLBACK FUNCTION

# =============================================
  

@app.callback([Output(label+'go', 'disabled'),
               Output(label+'mtnotfound','children'),
               Output({'component': 'store_r_launch', 'module': parent},'data'),
               Output({'component': 'store_render_launch', 'module': parent},'data'),
               Output({'component': 'store_tpmatchtime', 'module': parent}, 'data')],
              [Input(label+'go', 'n_clicks'),
               Input(label+'mtselect','value')],
              [State({'component':'compute_sel','module' : parent},'value'),
                State({'component':'matchcoll_dd','module': parent},'value'),
                State({'component': 'mc_owner_dd', 'module': parent},'value'),
                State(parent+'tp_dd','value'),
                State({'component':'store_owner','module' : parent},'data'),
                State({'component':'store_project','module' : parent},'data'),
                State({'component':'stack_dd','module' : parent},'value'),
                State({'component': 'input_Num_CPUs', 'module': parent},'value'),
                State({'component': 'input_runtime_minutes', 'module': parent},'value')]
              ,prevent_initial_call=True)                 
def sift_pointmatch_execute_gobutton(click,matchID,comp_sel,matchcoll,mc_owner,tilepairdir,owner,project,stack,n_cpu,timelim): 
    ctx = dash.callback_context
        
    trigger = ctx.triggered[0]['prop_id']
    
    try:
            mt_params = matchTrial.mt_parameters(matchID)
    except json.JSONDecodeError:
        return True,'Could not find this MatchTrial ID!',dash.no_update,dash.no_update,dash.no_update
    
    if mt_params == {}:
        return True,'No MatchTrial selected!',dash.no_update,dash.no_update,dash.no_update
    print(owner)
    print(stack)
    print(mt_params)
    outstore = dict()
    outstore['owner'] = owner
    outstore['project'] = project
    outstore['stack'] = stack
    outstore['mt_params'] = mt_params
    
    if tilepairdir == '':
        return True,'No tile pair directory selected!',dash.no_update,dash.no_update,dash.no_update
        
    
    if 'mtselect' in trigger:
        
        return False,'',dash.no_update,outstore,mt_params['ptime']
        
    
    elif 'go' in trigger:
        if click is None: return dash.no_update
        
        # prepare parameters:
        importlib.reload(params)
    
        run_params = params.render_json.copy()
        run_params['render']['owner'] = owner
        run_params['render']['project'] = project
        
        run_params_generate = run_params.copy()
          
        # tilepair files:
        
        tp_dir = os.path.join(params.json_run_dir, tilepairdir)
            
        tp_json = os.listdir(tp_dir)
        
        tp_jsonfiles = [os.path.join(params.json_run_dir,tpj) for tpj in tp_json]
        
        param_file = params.json_run_dir + '/' + parent + '_' + params.run_prefix + '.json' 
    
        
        
        if comp_sel == 'standalone':    
            # =============================
            
            # TODO - STANDALONE PROCEDURE NOT TESTED !!!!
            
            # =============================

            
            # TODO!  render-modules only supports single tilepair JSON!!!
            
            cv_params = {
            "ndiv": mt_params['siftFeatureParameters']['steps'],
            "downsample_scale": mt_params['scale'],
            
            "pairJson": os.path.join(params.json_run_dir,tp_json[0]),
            "input_stack": stack,
            "match_collection": matchcoll,
        
            "ncpus": params.ncpu_standalone,
            "output_json":params.render_log_dir + '/' + '_' + params.run_prefix + "_SIFT_openCV.json",
            }
            
            run_params_generate.update(cv_params)            
            
            target_args = None
            run_args = None
            script = '$rendermodules/rendermodules/pointmatch/generate_point_matches_opencv.py'
            
        elif comp_sel == 'sparkslurm':
            spsl_p = dict()
            
            spsl_p['--baseDataUrl'] = params.render_base_url
            spsl_p['--owner'] = mc_owner
            spsl_p['--collection'] = matchcoll
            spsl_p['--pairJson'] = tp_jsonfiles
            
            mtrun_p = dict()
            
            # some default values...
            
            mtrun_p['--matchMaxNumInliers'] = 200
            mtrun_p['--maxFeatureCacheGb'] = 6
            mtrun_p['--maxFeatureSourceCacheGb'] = 6
            
            
            # fill parameters
            
            mtrun_p['--renderScale'] = mt_params['scale']
            
            for item in mt_params['siftFeatureParameters'].items():
                mtrun_p['--SIFT'+item[0]] = item[1]
                
            for item in mt_params['matchDerivationParameters'].items():
                mtrun_p['--'+item[0]] = item[1]
            
            if 'clipPixels' in mt_params.keys():
                mtrun_p['--clipHeight'] = mt_params['clipPixels']
                mtrun_p['--clipWidth'] = mt_params['clipPixels']
            
            
            
            spark_p = dict()
            
            spark_p['--time'] = '00:' + str(timelim)+':00'
                        
            spark_p['--worker_cpu'] = params.cpu_pernode_spark
            spark_p['--worker_nodes'] = hf.spark_nodes(n_cpu)
            
            run_params_generate = spsl_p.copy()
            run_params_generate.update(mtrun_p)
            
            target_args = spark_p.copy()
            run_args = run_params_generate.copy()
            
            script = 'org.janelia.render.client.spark.SIFTPointMatchClient'
            
            
            
            
        #generate script call...
        
        with open(param_file,'w') as f:
            json.dump(run_params_generate,f,indent=4)
            
        
    
        log_file = params.render_log_dir + '/' + parent + '_' + params.run_prefix
        err_file = log_file + '.err'
        log_file += '.log'
        
        
        
        
        sift_pointmatch_p = launch_jobs.run(target=comp_sel,pyscript=script,
                            json=param_file,run_args=run_args,target_args=target_args,logfile=log_file,errfile=err_file)
            
        params.processes[parent].extend(sift_pointmatch_p)
        
                
        launch_store=dict()
        launch_store['logfile'] = log_file
        launch_store['state'] = 'running'
    
        return True,'', launch_store, outstore, mt_params['ptime']

    
