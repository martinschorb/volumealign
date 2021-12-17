#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 16:15:27 2020

@author: schorb
"""
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input,Output,State
import params
import json
import os
import importlib


from app import app
from utils import launch_jobs, pages

from callbacks import runstate,render_selector,substack_sel


module='tilepairs'


storeinit = {}            
store = pages.init_store(storeinit, module)

store.append(dcc.Store(id={'component':'runstep','module':module},data='generate'))


main=html.Div(id={'component': 'main', 'module': module},children=html.H3("Generate TilePairs for Render stack"))


page = [main]



# # ===============================================
#  RENDER STACK SELECTOR

# Pre-fill render stack selection from previous module

us_out,us_in,us_state = render_selector.init_update_store(module,'convert')

@app.callback(us_out,us_in,us_state,
              prevent_initial_call=True)
def tilepairs_update_store(*args): 
    return render_selector.update_store(*args)

page1 = pages.render_selector(module)

page.append(page1)



# # # ===============================================


page2 = html.Div(id={'component':'page2', 'module': module},
                 children=[html.H4('Pair assignment mode'),
                           html.Div([dcc.RadioItems(options=[
                                                          {'label': '2D (tiles in montage/mosaic)', 'value': '2D'},
                                                          {'label': '3D (across sections)', 'value': '3D'}],
                                                      value='2D',                                                
                                                      id={'component':'pairmode', 'module': module}),
                               ]
                               ,style={'display':'inline,block'}),
                           html.Br()  
                           ])
                                                                           
page.append(page2)

page.append(pages.substack_sel(module))


# # ===============================================

@app.callback([Output({'component':'3Dslices','module' : module},'style'),
                Output({'component':'sec_input1','module' : module},'value')],
              Input({'component':'pairmode','module' : module},'value'))
def tilepairs_3D_status(pairmode):

    if pairmode == '2D':
        style = {'display':'none'}
        val = 0
    elif pairmode == '3D':
        style = {'display':'block'}
        val = 1
    return style, val





# =============================================
# Start Button



gobutton = html.Div(children=[html.Br(),
                              html.Button('Start TilePair generation',
                                          id={'component': 'go', 'module': module}),
                              html.Br(),
                              pages.compute_loc(module),
                              html.Br(),
                              html.Div(id={'component': 'run_state', 'module': module}, style={'display': 'none'},children='wait')])


page.append(gobutton)


@app.callback([Output({'component': 'go', 'module': module}, 'disabled'),
               Output({'component': 'store_launch_status', 'module': module},'data'),
               Output({'component': 'store_render_launch', 'module': module},'data')],
              [Input({'component': 'go', 'module': module}, 'n_clicks'),
               Input({'component':'pairmode','module' : module},'value')],
              [State({'component':'sec_input1','module' : module},'value'),
                State({'component':'compute_sel','module' : module},'value'),

                State({'component':'startsection','module' : module},'value'),
                State({'component':'endsection','module' : module},'value'),
                State({'component':'store_owner','module' : module},'data'),
                State({'component':'store_project','module' : module},'data'),
                State({'component':'stack_dd','module' : module},'value')]
              ,prevent_initial_call=True)                 
def tilepairs_execute_gobutton(click,pairmode,slicedepth,comp_sel,startsection,endsection,owner,project,stack):
    if click is None: return dash.no_update
        
    # prepare parameters:
    run_prefix = launch_jobs.run_prefix()

    run_params = params.render_json.copy()
    run_params['render']['owner'] = owner
    run_params['render']['project'] = project
    
    run_params_generate = run_params.copy()
    
    
    #generate script call...
    
    tilepairdir = params.json_run_dir + '/tilepairs_' + run_prefix + '_'+ stack + '_' + pairmode
    
    if not os.path.exists(tilepairdir): os.makedirs(tilepairdir)
    
    run_params_generate['output_dir'] = tilepairdir
    
    with open(os.path.join(params.json_template_dir,'tilepairs.json'),'r') as f:
            run_params_generate.update(json.load(f))
    
    run_params_generate['output_json'] = tilepairdir + '/tiles_'+ stack + '_' + pairmode
    
    run_params_generate['minZ'] = startsection
    run_params_generate['maxZ'] = endsection
    
    run_params_generate['stack'] = stack
    
    if pairmode == '2D':
        run_params_generate['zNeighborDistance'] = 0
        run_params_generate['excludeSameLayerNeighbors'] = 'False'
        
    elif pairmode == '3D':
        run_params_generate['zNeighborDistance'] = slicedepth
        run_params_generate['excludeSameLayerNeighbors'] = 'True'

        if owner == 'SBEM':
            run_params_generate["xyNeighborFactor"] = 0.3

    param_file = params.json_run_dir + '/' + module + '_' + run_prefix + '_' + pairmode + '.json' 

           
    with open(param_file,'w') as f:
        json.dump(run_params_generate,f,indent=4)

    log_file = params.render_log_dir + '/' + module + '_' + run_prefix + '_' + pairmode
    err_file = log_file + '.err'
    log_file += '.log'
    
    tilepairs_generate_p = launch_jobs.run(target=comp_sel,pyscript=params.rendermodules_dir+'rendermodules/pointmatch/create_tilepairs.py',
                        jsonfile=param_file,run_args=None,target_args=None,logfile=log_file,errfile=err_file)

    
    launch_store=dict()
    launch_store['logfile'] = log_file
    launch_store['status'] = 'launch'
    launch_store['id'] = tilepairs_generate_p
    launch_store['type'] = comp_sel


    outstore = dict()
    outstore['owner'] = owner
    outstore['project'] = project
    outstore['stack'] = stack
    outstore['tilepairdir'] = tilepairdir
    
    return True, launch_store, outstore


# =============================================
# Processing status

# initialized with store
# embedded from callbacks import runstate

# # =============================================
# # PROGRESS OUTPUT


collapse_stdout = pages.log_output(module)

# ----------------

# Full page layout:
    

page.append(collapse_stdout)