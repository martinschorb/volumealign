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
import importlib


from app import app
from utils import launch_jobs, pages

from callbacks import runstate,render_selector,substack_sel




module='tilepairs'


storeinit = {}            
store = pages.init_store(storeinit, module)

store.append(dcc.Store(id={'component':'runstep','module':module},data='generate'))



main=html.Div(id={'component': 'main', 'module': module},children=html.H3("Generate TilePairs for Render stack"))

intervals = html.Div([dcc.Interval(id={'component': 'interval1', 'module': module}, interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Interval(id={'component': 'interval2', 'module': module}, interval=params.idle_interval,
                                       n_intervals=0)
                      ])


page = [intervals,main]



# # ===============================================
#  RENDER STACK SELECTOR

# Pre-fill render stack selection from previous module

us_out,us_in,us_state = render_selector.init_update_store(module,'mipmaps')

@app.callback(us_out,us_in,us_state,
              prevent_initial_call=True)
def mipmaps_update_store(*args): 
    return render_selector.update_store(*args)

page1 = pages.render_selector(module)

page.append(page1)






# gobutton = html.Div(children=[html.Br(),
#                               html.Button('Start TilePair generation',id={'component':"go", 'module': module}),
#                               html.Div(id={'component':'buttondiv', 'module': module}),
#                               html.Div(id={'component':'directory-popup', 'module': module}),
#                               html.Br(),
#                               html.Details([html.Summary('Compute location:'),
#                                             dcc.RadioItems(
#                                                 options=[
#                                                     {'label': 'Cluster (slurm)', 'value': 'slurm'},
#                                                     {'label': 'locally (this submission node)', 'value': 'standalone'}
#                                                 ],
#                                                 value='slurm',
#                                                 labelStyle={'display': 'inline-block'},
#                                                 id={'component':'compute_sel', 'module': module}
#                                                 )],
#                                   id={'component':'compute', 'module': module}),
#                               html.Br(),
#                               html.Div(id={'component':'run_state', 'module': module}, style={'display': 'none'},children='wait')])


# # # ===============================================


page2 = html.Div(id={'component':'page2', 'module': module},
                 children=[html.H4('Pair assignment mode'),
                           html.Div([dcc.RadioItems(options=[
                                                          {'label': '2D (tiles in montage/mosaic)', 'value': '2D'},
                                                          {'label': '3D (across sections)', 'value': '3D'}],
                                                      value='2D',                                                
                                                      id={'component':'pairmode', 'module': module}),
                               html.Div(id={'component':'3Dslices', 'module': module},
                                        children=['range of sections to consider:  ',
                                                  dcc.Input(id={'component':'input_1', 'module': module},type='number',min=1,max=10,value=0)],
                                                      style={'display':'none'})]
                               ,style={'display':'inline,block'}),
                           html.Br()  
                           ])
                                                                           
page.append(page2)

page.append(pages.substack_sel(module))



# @app.callback([Output(module+'startsection','max'),
#                 Output(module+'endsection','min')],
#               [Input(module+'startsection', 'value'),
#                 Input(module+'endsection','value'),
#                 Input(module+'input_1','value')]
#               )
# def tilepairs_sectionlimits(start_sec,end_sec,sec_range):
    
#     if not sec_range is None and not start_sec is None and not end_sec is None:
#         return end_sec - sec_range, start_sec + sec_range
#     else:
#         return end_sec, start_sec




# # # ===============================================

# @app.callback([Output(module+'3Dslices','style'),
#                 Output(module+'input_1','value')],
#               Input(module+'pairmode','value'))
# def tilepairs_3D_status(pairmode):

#     if pairmode == '2D':
#         style = {'display':'none'}
#         val = 0
#     elif pairmode == '3D':
#         style = {'display':'block'}
#         val = 1
#     return style, val



# @app.callback([Output(module+'go', 'disabled'),
#                 Output(module+'store','data'),
#                 Output(module+'interval1','interval')
#                 ],
#               Input(module+'go', 'n_clicks'),
#               [State(module+'input_1','value'),
#                 State(module+'compute_sel','value'),
#                 State(module+'pairmode','value'),
#                 State(module+'startsection','value'),
#                 State(module+'endsection','value'),
#                 State(module+'store','data')]
#               )                 
# def tilepairs_execute_gobutton(click,slicedepth,comp_sel,pairmode,startsection,endsection,storage):   
    
#     if click>0:
        
#         # prepare parameters:
#         importlib.reload(params)
    
#         run_params = params.render_json.copy()
#         run_params['render']['owner'] = storage['owner']
#         run_params['render']['project'] = storage['project']
       
#         run_params_generate = run_params.copy()
        
        
#         #generate script call...
        
#         tilepairdir = params.json_run_dir + '/tilepairs_' + params.run_prefix + '_'+ storage['stack'] + '_' + pairmode
        
#         if not os.path.exists(tilepairdir): os.makedirs(tilepairdir)
        
#         run_params_generate['output_dir'] = tilepairdir
        
#         with open(os.path.join(params.json_template_dir,'tilepairs.json'),'r') as f:
#                 run_params_generate.update(json.load(f))
        
#         run_params_generate['output_json'] = tilepairdir + '/tiles_'+ storage['stack'] + '_' + pairmode
        
#         run_params_generate['minZ'] = startsection
#         run_params_generate['maxZ'] = endsection
        
#         run_params_generate['stack'] = storage['stack']
        
#         if pairmode == '2D':
#             run_params_generate['zNeighborDistance'] = 0
#             run_params_generate['excludeSameLayerNeighbors'] = 'False'
            
#         elif pairmode == '3D':
#             run_params_generate['zNeighborDistance'] = slicedepth
#             run_params_generate['excludeSameLayerNeighbors'] = 'True'
    
    
#         param_file = params.json_run_dir + '/' + module + params.run_prefix + '_' + pairmode + '.json' 
    
               
#         with open(param_file,'w') as f:
#             json.dump(run_params_generate,f,indent=4)
    
#         log_file = params.render_log_dir + '/' + module + params.run_prefix + '_' + pairmode
#         err_file = log_file + '.err'
#         log_file += '.log'
        
#         tilepairs_generate_p = launch_jobs.run(target=comp_sel,pyscript='$rendermodules/rendermodules/pointmatch/create_tilepairs.py',
#                             json=param_file,run_args=None,target_args=None,logfile=log_file,errfile=err_file)
            
#         params.processes[module.strip('_')].extend(tilepairs_generate_p)
        
#         storage['run_state'] = 'running'
#         storage['log_file'] = log_file
#         storage['tilepairdir'] = tilepairdir
        
#         return True,storage,params.refresh_interval


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