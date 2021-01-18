#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 16:15:27 2020

@author: schorb
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
import params
import json
import requests
import os
import importlib
import numpy as np

import subprocess

from app import app
from utils import launch_jobs, pages
from callbacks import runstate



module='mipmaps_'

storeinit = {}            

store = pages.init_store(storeinit, module)


table_cols = ['stack',
              'slices',
              'tiles',
              'Gigapixels']


compute_table_cols = ['Num_CPUs',
                      'runtime_minutes',
                      'section_split']

# =========================================

main=html.Div(id=module+'main',children=html.H3("Generate MipMaps for Render stack"))

intervals = html.Div([dcc.Interval(id=module+'interval1', interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Interval(id=module+'interval2', interval=params.idle_interval,
                                       n_intervals=0),
                      html.Div(id=module+'tmpstore')
                      ])

page1 = html.Div(id=module+'page1',children=[html.H4('Current active stack:'),
                                             html.Div([html.Div('Owner:',style={'margin-right': '1em','margin-left': '2em'}),
                                                       dcc.Dropdown(id=module+'owner_dd',className='dropdown_inline',options=[{'label':'1','value':'1'}],style={'width':'120px'},
                                                          persistence=True,
                                                          clearable=False),
                                                       html.Div(id=module+'owner',style={'display':'none'}),
                                                       html.Div('Project',style={'margin-left': '2em'}),
                                                       html.A('(Browse)',id=module+'browse_proj',target="_blank",style={'margin-left': '0.5em','margin-right': '1em'}),
                                                       dcc.Dropdown(id=module+'project_dd',className='dropdown_inline',
                                                          persistence=True,
                                                          clearable=False),
                                                       html.Div(id=module+'proj',style={'display':'none'}),
                                                       html.Div('Stack',style={'margin-left': '2em'}),
                                                       html.A('(Browse)',id=module+'browse_stack',target="_blank",style={'margin-left': '0.5em','margin-right': '1em'}),
                                                       dcc.Dropdown(id=module+'stack_dd',className='dropdown_inline',
                                                          persistence=True,
                                                          clearable=False),
                                                       dcc.Store(id=module+'stacks'),
                                             
                                             ],style=dict(display='flex'))
                                             ])


page2 = html.Div(id=module+'page2',children=[html.H3('Mipmap output directory (subdirectory "mipmaps")'),
                                             dcc.Input(id=module+"input1", type="text",debounce=True,persistence=True,className='dir_textinput'),
                                             html.Button('Browse',id=module+"browse1"),
                                             'graphical browsing works on cluster login node ONLY!',
                                             html.Br()])
compute_stettings = html.Details(id=module+'compute',children=[html.Summary('Compute settings:'),
                                             html.Table([html.Tr([html.Th(col) for col in table_cols]),
                                                  html.Tr([html.Td('',id=module+'t_'+col) for col in table_cols])
                                             ],className='table'),
                                             html.Br(),
                                             html.Table([html.Tr([html.Th(col) for col in compute_table_cols]),
                                                  html.Tr([html.Td(dcc.Input(id=module+'input_'+col,type='number',min=1)) for col in compute_table_cols])
                                             ],className='table'),
                                             ])

collapse_stdout = pages.log_output(module)


# OUTPUT TO OWNER DROPDOWN (options and value)

@app.callback([Output(module+'owner_dd','options'),
               Output(module+'owner_dd','value'),
               Output(module+'store_owner','data'),
               Output(module+'store_allowners','data')],
              [Input(module+'page1','children'),
               Input('convert_'+'store','data')],
              State(module+'store_owner','data'))
def mipmaps_fill_owner_dd(page,owner): 
    url = params.render_base_url + params.render_version + 'owners'
    owners = requests.get(url).json()        
        # assemble dropdown
        
    dd_options = list(dict())
    for item in owners: 
        dd_options.append({'label':item, 'value':item})
    
    if owner is None:
        owner = owners[0]
    
    
    print(' -----------     -----------         -------------- ')
    return dd_options, owner, owner, owners
    
    

    

# @app.callback([Output(module+'store','data'), 
#                 Output(module+'owner_dd','options'),
#                 Output(module+'owner_dd','value'),
#                 Output(module+'project_dd','value'),
#                 Output(module+'stack_dd','value')],
#               Input('convert_'+'store','data'),              
#               State(module+'store','data'))
# def mipmaps_update_stack_state(prevstore,thisstore): 
#     print('update from previous')
#     print(thisstore)
#     print(prevstore)

#     for key in ['owner','project','stack']: 
#         print(key)
#         if key in prevstore.keys() and not prevstore[key]=='-':
#             print(key)
#             print(thisstore[key])
#             print(prevstore[key])
#             thisstore[key] = prevstore[key]
            
    
#     owners = thisstore['all_owners']
    
#         # assemble dropdown
#     dd_options = list(dict())
#     for item in owners: 
#         dd_options.append({'label':item, 'value':item})
    
    
#     url = params.render_base_url + params.render_version + 'owner/' + thisstore['owner'] + '/project/' + thisstore['project'] + '/stacks'
#     stacks = requests.get(url).json()
#     thisstore['allstacks'] = stacks

#     thisstore['run_state'] = 'wait'
     
#     print('=======')
#     print(thisstore)
#     return thisstore,dd_options,thisstore['owner'],thisstore['project'],thisstore['stack']




##  SELECT STACK TO WORK....
#============================================================
#dropdown callback
# @app.callback([Output(module+'browse_proj','href'),
#                 Output(module+'project_dd','options'),
#                 Output(module+'proj_dd','value'),
#                 Output(module+'store','data')],
#               Input(module+'owner_dd', 'value'),
#               State(module+'store','data'), prevent_initial_call=True)
# def mipmaps_own_dd_sel(owner_sel,thisstore):
#     print('owner->proj')  
    
#     print(thisstore)
    

#     href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+owner_sel
    
#     # get list of projects on render server
#     url = params.render_base_url + params.render_version + 'owner/' + owner_sel + '/projects'
#     projects = requests.get(url).json()
    
#     out_project=projects[0]

#     # assemble dropdown
#     dd_options = list(dict())
#     for item in projects:
#         if 'project' in thisstore.keys():
#             if item == thisstore['project']:out_project=item
#         dd_options.append({'label':item, 'value':item})
   
#     thisstore['owner'] = owner_sel
#     thisstore['project'] = out_project
    
#     print(thisstore)
#     print(' -----------     -----------         -------------- ')
#     return href_out, dd_options, out_project, thisstore





# @app.callback(Output(module+'proj_dd','value'),               
#               Input(module+'project','children'),
#                )
# def mipmaps_init_proj(proj): 
#     return proj



# #dropdown callback
# @app.callback([Output(module+'browse_stack','href'),
#                 Output(module+'stack_dd','options'),
#                 Output(module+'stack_dd','value'),
#                 Output(module+'store','data')],
#               Input(module+'project_dd', 'value'),
#               State(module+'store','data'))
# def mipmaps_proj_dd_sel(proj_sel,thisstore): 
    
    
#     print('proj->stack')
#     print(proj_sel)  
    
#     print(thisstore)
   
    
#     # href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+thisstore['owner']+'&renderStackProject='+proj_sel
#     # # get list of projects on render server
#     # url = params.render_base_url + params.render_version + 'owner/' + thisstore['owner'] + '/project/' + proj_sel + '/stacks'
#     # stacks = requests.get(url).json()
    
#     # out_stack=stacks[0]['stackId']['stack']
    
#     # # assemble dropdown
#     # dd_options = list(dict())
#     # for item in stacks:
#     #     if item['stackId']['stack'] == thisstore['stack']:out_stack=item
#     #     dd_options.append({'label':item['stackId']['stack'], 'value':item['stackId']['stack']})

    
#     # thisstore['project'] = proj_sel
#     # thisstore['allstacks'] = stacks
    
    
#     # print(thisstore.keys())
#     print(' -----------     -----------         -------------- ')
#     return [dash.no_update] * 4#href_out, dd_options, out_stack, thisstore



# @app.callback(Output(module+'stack_dd','value'),               
#               Input(module+'stack','children'),
#                )
# def mipmaps_init_stack(stack): 
#     return stack


# # ===============================================

# stackoutput = [Output(module+'input1','value'),
#                 Output(module+'stack','data'),
#                 Output(module+'store','data')]

# tablefields = [Output(module+'t_'+col,'children') for col in table_cols]
# compute_tablefields = [Output(module+'input_'+col,'value') for col in compute_table_cols]

# stackoutput.extend(tablefields)  
# stackoutput.extend(compute_tablefields)        

# @app.callback(stackoutput,
#               Input(module+'stack_dd', 'value'),
#               [State(module+'stacks', 'data'),
#               State(module+'store','data')]
#               )
# def mipmaps_stacktodir(stack_sel,allstacks,thisstore):
    
#     dir_out=''
    
#     t_fields = ['']*len(table_cols)
#     ct_fields = [1]*len(compute_table_cols)
        
#     thisstore['allstacks']=allstacks
    
#     print('stacktodir')
    
#     print(thisstore.keys())
    
#     print(stack_sel)
    
#     print('allstacks' in thisstore.keys())
    
#     if (not stack_sel=='-' ) and (not allstacks is None):   
#         print(allstacks)
#         stacklist = [stack for stack in thisstore['allstacks'] if stack['stackId']['stack'] == stack_sel]        
        
#         if not stacklist == []:
#             stackparams = stacklist[0]        
#             thisstore['stack'] = stackparams['stackId']['stack']
#             thisstore['stackparams'] = stackparams
#             thisstore['zmin']=stackparams['stats']['stackBounds']['minZ']
#             thisstore['zmax']=stackparams['stats']['stackBounds']['maxZ']
#             thisstore['numtiles']=stackparams['stats']['tileCount']
#             thisstore['numsections']=stackparams['stats']['sectionCount']
         
#             num_blocks = int(np.max((np.floor(thisstore['numsections']/params.section_split),1)))
            
#             url = params.render_base_url + params.render_version + 'owner/' + thisstore['owner'] + '/project/' + thisstore['project'] + '/stack/' +thisstore['stack'] + '/z/'+ str(stackparams['stats']['stackBounds']['minZ']) +'/render-parameters'
#             tiles0 = requests.get(url).json()
            
#             tilefile0 = os.path.abspath(tiles0['tileSpecs'][0]['mipmapLevels']['0']['imageUrl'].strip('file:'))
            
#             basedirsep = params.datasubdirs[thisstore['owner']]
#             dir_out = tilefile0[:tilefile0.find(basedirsep)]
            
#             thisstore['gigapixels']=thisstore['numtiles']*stackparams['stats']['maxTileWidth']*stackparams['stats']['maxTileHeight']/(10**9)
            
#             t_fields=[thisstore['stack'],str(stackparams['stats']['sectionCount']),str(stackparams['stats']['tileCount']),'%0.2f' %thisstore['gigapixels']]
            
#             n_cpu = params.n_cpu_script
            
#             timelim = np.ceil(thisstore['gigapixels'] / n_cpu * params.mipmaps['min/Gpix/CPU']*(1+params.time_add_buffer)/num_blocks)
            
#             ct_fields = [n_cpu,timelim,params.section_split]  
          
   
#     outlist=[dir_out, thisstore['stack'], thisstore]        
#     outlist.extend(t_fields)
#     outlist.extend(ct_fields)     
    
#     return outlist



# comp_values = [Input(module+'input_'+col,'value') for col in compute_table_cols]
# comp_labels = [State(module+'input_'+col,'id') for col in compute_table_cols]

# stackinput = comp_values
# stackstate = comp_labels
# stackstate.append(State(module+'store','data'))

# @app.callback(Output(module+'store','data'),                            
#               stackinput,
#               stackstate
#                 )
# def mipmaps_store_compute_settings(*inputs): 
#     comp_numset=len(compute_table_cols)
#     storage=inputs[-1]
    
#     storage['comp_settings']=dict()
    
#     in_values = np.array(inputs)[range(comp_numset)]
#     in_labels = np.array(inputs)[np.array(range(comp_numset))+ comp_numset]
    
#     for input_idx,label in enumerate(in_labels):
        
#         # print('label:')
#         # print(label)    
#         # print('value:')
#         # print(in_values[input_idx])
        
#         label = label[label.find('_input_')+7:]
        
#         storage['comp_settings'][label] = in_values[input_idx]
#     return storage




# @app.callback([Output(module+'tmpstore', 'children'),
#                 Output(module+'store','data')],                            
#               Input(module+'run_state','children'),
#               State(module+'store','data')
#                 )
# def mipmaps_store_runstate(runstate,storage):  
#     storage['run_state']=runstate
#     return [],storage


# =============================================
# Start Button

gobutton = html.Div(children=[html.Br(),
                              html.Button('Start MipMap generation & apply to current stack',id=module+"go",disabled=True),
                              html.Div(id=module+'buttondiv'),
                              html.Div(id=module+'directory-popup'),
                              html.Br(),
                              html.Details([html.Summary('Compute location:'),
                                            dcc.RadioItems(
                                                options=[
                                                    {'label': 'Cluster (slurm)', 'value': 'slurm'},
                                                    {'label': 'locally (this submission node)', 'value': 'standalone'}
                                                ],
                                                value='slurm',
                                                labelStyle={'display': 'inline-block'},
                                                id=module+'compute_sel'
                                                )],
                                  id=module+'compute'),
                              html.Br(),
                              html.Div(id=module+'run_state', style={'display': 'none'},children='wait')])


# @app.callback([Output(module+'go', 'disabled'),
#                 Output(module+'directory-popup','children'),
#                 Output(module+'run_state','children')],              
#               Input(module+'input1','value'),
#               State(module+'store','data'),
#                 )
# def mipmaps_activate_gobutton(in_dir,storage):      
#     rstate = 'wait'          
#     out_pop=dcc.ConfirmDialog(        
#         id=module+'danger-novaliddir',displayed=True,
#         message='The selected directory does not exist or is not writable!'
#         )
#     if any([in_dir=='',in_dir==None]):
#         if not (storage['run_state'] == 'running'): 
#                 rstate = 'wait'
#         return True,'No input directory chosen.',rstate
    
#     elif os.path.isdir(in_dir):
#             if os.path.exists(os.path.join(in_dir,params.mipmapdir)):
#                 rstate = 'input'
#                 out_pop.message = 'Warning: there already exists a MipMap directory. Will overwrite it.'
#                 return False,out_pop,rstate

#             if not (storage['run_state'] == 'running'): 
#                 rstate = 'input'
            
#             return False,'',rstate       
#     else:
#         if not (storage['run_state'] == 'running'): 
#             rstate = 'wait'
#         return True, [out_pop, 'The selected directory does not exist or is not writable!'], rstate
    


# @app.callback([Output(module+'go', 'disabled'),
#                 Output(module+'store','data'),
#                 Output(module+'interval1','interval'),
#                 Output('runstep','children')
#                 ],
#               Input(module+'go', 'n_clicks'),
#               [State(module+'input1','value'),
#                 State(module+'compute_sel','value'),
#                 State('runstep','children'),
#                 State(module+'store','data')]
#               )                 

# def mipmaps_execute_gobutton(click,mipmapdir,comp_sel,runstep,storage):    
#     # prepare parameters:
    
#     # print('output log1!')
#     # print(storage['stack'])
#     # with open('log1.json','w') as f:
#     #     json.dump(storage,f,indent=4)

#     importlib.reload(params)
#     runstep = 'generate'
    
#     run_params = params.render_json.copy()
#     run_params['render']['owner'] = storage['owner']
#     run_params['render']['project'] = storage['project']
   
#     run_params_generate = run_params.copy()
    
    
#     #generate mipmaps script call...
    
#     run_params_generate['input_stack'] = storage['stack']
    
#     mipmapdir += '/mipmaps'
    
#     if not os.path.exists(mipmapdir): os.makedirs(mipmapdir)
    
#     run_params_generate['output_dir'] = mipmapdir
    
#     with open(os.path.join(params.json_template_dir,'generate_mipmaps.json'),'r') as f:
#             run_params_generate.update(json.load(f))
        
#     sec_start = storage['zmin']
#     sliceblock_idx = 0
#     sec_end = sec_start
    
#     while sec_end <= storage['zmax']:
#         sec_end = int(np.min([sec_start+storage['comp_settings']['section_split'],storage['zmax']]))
#         run_params_generate['zstart'] = sec_start
#         run_params_generate['zend'] = sec_end
        
#         run_params_generate['output_json'] = os.path.join(params.json_run_dir,'output_' + module + params.run_prefix + '_' + str(sliceblock_idx)+'.json' )
        
#         param_file = params.json_run_dir + '/' + runstep+ '_' + module + params.run_prefix + '_' + str(sliceblock_idx)+'.json' 
    
               
#         with open(param_file,'w') as f:
#             json.dump(run_params_generate,f,indent=4)
    
#         log_file = params.render_log_dir + '/' + runstep+ '_' + module + params.run_prefix+ '_' + str(sliceblock_idx)
#         err_file = log_file + '.err'
#         log_file += '.log'
        
        
#         sec_start = sec_end + 1
#         sec_end = sec_start
#         sliceblock_idx += 1
    
            
            
#         #launch
#         # -----------------------
        
        
#         # check resource settings
#         target_args=None
        
#         if comp_sel == 'slurm':
#             cset = storage['comp_settings']

#             slurm_args=['-N1']
#             slurm_args.append('-n1')
#             slurm_args.append('-c '+str(cset['Num_CPUs']))
#             slurm_args.append('--mem  '+str(params.mem_per_cpu)+'G')
#             slurm_args.append('-t 00:%02i:00' %cset['runtime_minutes'])
            
#             target_args=slurm_args
        
        
        
#         mipmap_generate_p = launch_jobs.run(target=comp_sel,pyscript='$rendermodules/rendermodules/dataimport/generate_mipmaps.py',
#                         json=param_file,run_args=None,target_args=target_args,logfile=log_file,errfile=err_file)
        
#         params.processes[module.strip('_')].extend(mipmap_generate_p)
        
#     storage['log_file'] = log_file
#     storage['run_state'] = 'running'
    
    
#     return True,storage,params.refresh_interval,runstep




# =============================================
# Processing status

cus_out,cus_in,cus_state = runstate.init_update_status(module)

@app.callback(cus_out,cus_in,cus_state)
def convert_update_status(*args): 
    return runstate.update_status(*args)



cgs_out,cgs_in,cgs_state = runstate.init_get_status(module)

@app.callback(cgs_out,cgs_in,cgs_state)
def convert_get_status(*args):
    return runstate.get_status(*args)


rs_out, rs_in = runstate.init_run_state(module)

@app.callback(rs_out, rs_in)
def covert_run_state(*args):
    return runstate.run_state(*args)  

# # =============================================
# # PROGRESS OUTPUT

uo_out,uo_in,uo_state = runstate.init_update_output(module)

@app.callback(uo_out,uo_in,uo_state)
def convert_update_output(*args):
    return runstate.update_output(*args)



# Full page layout:
    
page = [intervals,page1, page2, gobutton, compute_stettings]
page.append(collapse_stdout)
