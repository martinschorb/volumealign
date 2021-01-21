#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
import os
import glob
import params
import subprocess
import requests

from app import app

from utils import launch_jobs,pages
from callbacks import runstate,render_selector,substack_sel,match_selector


# from sift import sift_pointmatch


module='pointmatch'



storeinit = {}            
store = pages.init_store(storeinit, module)

store.append(dcc.Store(id={'component':'runstep','module':module},data='generate'))

for storeitem in params.match_store.keys():       
        store.append(dcc.Store(id={'component':'store_'+storeitem,'module':module}, storage_type='session',data=params.match_store[storeitem]))
    

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

us_out,us_in,us_state = render_selector.init_update_store(module,'tilepairs')

@app.callback(us_out,us_in,us_state,
              prevent_initial_call=True)
def mipmaps_update_store(*args): 
    return render_selector.update_store(*args)

page1 = pages.render_selector(module)


page.append(page1)


page2 = pages.match_selector(module,newcoll=True)

       
page.append(page2)       


# ===============================================
       
page3 = html.Div([html.H4("Choose type of PointMatch determination:"),
                  dcc.Dropdown(id=module+'dropdown1',persistence=True,
                               options=[{'label': 'SIFT', 'value': 'SIFT'}],
                               value='SIFT'),                          
                  html.Div([html.H4("Select Tilepair source directory:"),
                            dcc.Dropdown(id=module+'tp_dd',persistence=True,
                                         clearable=False),
                            html.Br(),
                            html.Div(id=module+'tp_prefix',style={'display':'none'})                              
                            ])
              ])


page.append(page3)  


@app.callback([Output(module+'tp_dd','options'),
                Output(module+'tp_dd','value')],
              Input({'component': 'stack_dd', 'module': module},'value'))
def pointmatch_tp_dd_fill(stack):
   
    tp_dirlist = [d_item for d_item in glob.glob(params.json_run_dir+'/tilepairs_'+params.user+'*'+stack+'*') if os.path.isdir(d_item)]
    tpdir_dd_options=list(dict())
    
    
    if tp_dirlist == []:
        tpdir_dd_options.append({'label':'no tilepairs found for selected stack', 'value': ''})
    else:
        for tp_dir in tp_dirlist:
            tpdir_dd_options.append({'label':os.path.basename(tp_dir), 'value':tp_dir})
    
    

    return tpdir_dd_options,tpdir_dd_options[-1]['value']


# # =========================================

# #------------------
# # SET STACK




# # @app.callback([Output(module+'stack_dd','options'),   
# #                Output(module+'stack_dd','style'), 
# #                Output(module+'stack_state','children')],
# #     [Input(module+'project_dd', 'value'),
# #      Input(module+'orig_proj','children')],
# #     )
# # def pointmatch_proj_stack_activate(project_sel,orig_proj):    
    
# #     dd_options = [{'label':'Create new Stack', 'value':'newstack'}]
    
# #     if project_sel in orig_proj:
# #         # get list of STACKS on render server
# #         url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project_sel + '/stacks'
# #         stacks = requests.get(url).json()  
        
# #         # assemble dropdown
        
# #         for item in stacks: dd_options.append({'label':item['stackId']['stack'], 'value':item['stackId']['stack']})
                
# #         return dd_options, {'display':'block'}, stacks[0]['stackId']['stack']
        
# #     else:    
# #         return dd_options,{'display':'none'}, 'newstack'
    
    
            
# # @app.callback(Output(module+'stack_state','children'),
# #     Input(module+'stack_dd','value'))
# # def pointmatch_update_stack_state(stack_dd):        
# #     return stack_dd


# # @app.callback(Output(parent+'store','data'),
# #     [Input(module+'stack_state','children'),
# #     Input(module+'project_dd', 'value')],
# #     [State(parent+'store','data')]
# #     )
# # def pointmatch_update_active_project(stack,project,storage):
# #     storage['owner']=owner
# #     storage['project']=project
# #     storage['stack']=stack    
# #     # print('sbem -> store')
# #     # print(storage)
# #     return storage


    
# # @app.callback([Output(module+'browse_stack','href'),Output(module+'browse_stack','style')],
# #     Input(module+'stack_state','children'),
# #     State(module+'project_dd', 'value'))
# # def pointmatch_update_stack_browse(stack_state,project_sel):      
# #     if stack_state == 'newstack':
# #         return params.render_base_url, {'display':'none'}
# #     else:
# #         return params.render_base_url+'view/stack-details.html?renderStackOwner='+owner+'&renderStackProject='+project_sel+'&renderStack='+stack_state, {'display':'block'}
                                
    
# # @app.callback(Output(module+'newstack','children'),
# #     Input(module+'stack_state','children'))
# # def pointmatch_new_stack_input(stack_value):
# #     if stack_value=='newstack':
# #         st_div_out = ['Enter new stack name: ',
# #                    dcc.Input(id=module+"stack_input", type="text", debounce=True,placeholder="new_stack",persistence=False)
# #                    ]
# #     else:
# #         st_div_out = ''
    
# #     return st_div_out



# # @app.callback([Output(module+'stack_dd', 'options'),
# #                Output(module+'stack_dd', 'value'),
# #                Output(module+'stack_dd','style')],
# #               [Input(module+'stack_input', 'value')],
# #               State(module+'stack_dd', 'options'))
# # def pointmatch_new_stack(stack_name,dd_options): 
# #     dd_options.append({'label':stack_name, 'value':stack_name})
# #     return dd_options,stack_name,{'display':'block'}

 




# # =============================================
# # # Page content

# @app.callback([Output(module+'page1', 'children'),
#                 Output(module+'store','data')],
#                 Input(module+'dropdown1', 'value'),
#                 State(module+'store','data'))
# def pointmatch_output(value,thisstore):
#     if value=='SIFT':
#         return sift_pointmatch.page, thisstore
    
#     else:
#         return [html.Br(),'No method type selected.'],thisstore




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