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
import numpy as np
import os
import json
import requests
import importlib


from app import app
import params

from utils import pages,launch_jobs
from utils import helper_functions as hf

from callbacks import substack_sel, filebrowse



# element prefix
label = "N5_export"
parent = "export"



status_table_cols = ['stack',
              'slices',
              'Gigapixels']         


compute_table_cols = ['Num_CPUs',
                      # 'MemGB_perCPU',
                      'runtime_minutes']

page=[html.Br()]

# # ===============================================
# Compute Settings

compute_settings = html.Details(children=[html.Summary('Compute settings:'),
                                             html.Table([html.Tr([html.Th(col) for col in status_table_cols]),
                                                  html.Tr([html.Td('',id={'component': 't_'+col, 'module': label}) for col in status_table_cols])
                                             ],className='table'),
                                             html.Br(),
                                             html.Table([html.Tr([html.Th(col) for col in compute_table_cols]),
                                                  html.Tr([html.Td(dcc.Input(id={'component': 'input_'+col, 'module': label},type='number',min=1)) for col in compute_table_cols])
                                             ],className='table'),
                                             dcc.Store(id={'component':'store_compset','module':label})
                                             ])
page.append(compute_settings)


# callbacks

@app.callback(Output({'component':'store_compset','module':label},'data'),                            
              [Input({'component': 'input_'+col, 'module': label},'value') for col in compute_table_cols],
              prevent_initial_call=True)
def n5export_store_compute_settings(*inputs): 
    
    storage=dict()
        
    in_labels,in_values  = hf.input_components()
    
    for input_idx,label in enumerate(in_labels):
        
        storage[label] = in_values[input_idx]
    
    return storage




# Update directory and compute settings from stack selection


bbox0=[]


for dim in ['X','Y','Z']:
    bbox0.append(Input({'component': 'start'+dim,'module' : parent},'value'))
    bbox0.append(Input({'component': 'end'+dim,'module' : parent},'value'))


stackinput = [Input({'component': 'stack_dd', 'module': parent},'value')]
stackinput.extend(bbox0)
stackinput.append(Input({'component': "path_input", 'module': label},'n_blur'))


stackoutput = [Output({'component': 'path_ext', 'module': label},'data'),
               # Output({'component': 'store_stackparams', 'module': module}, 'data')
               ]
tablefields = [Output({'component': 't_'+col, 'module': label},'children') for col in status_table_cols]
compute_tablefields = [Output({'component': 'input_'+col, 'module': label},'value') for col in compute_table_cols]

stackoutput.extend(tablefields) 
 
stackoutput.extend(compute_tablefields)        

@app.callback(stackoutput,
              stackinput,
              [State({'component': 'store_owner', 'module': parent}, 'data'),
               State({'component': 'store_project', 'module': parent}, 'data'),
               State({'component': 'store_stack', 'module': parent}, 'data'),
               State({'component': 'store_allstacks', 'module': parent}, 'data'),
               State({'component': "path_input", 'module': label},'value')]
              )
def n5export_stacktodir(stack_sel,
                       xmin,xmax,ymin,ymax,zmin,zmax,
                       browsetrig,
                       owner,project,stack,allstacks,
                       browsedir):
    
    dir_out=''
    out=dict()
    
    t_fields = ['']*len(status_table_cols)
    ct_fields = [1]*len(compute_table_cols)

    
    if (not stack_sel=='-' ) and (not allstacks is None):   
        stacklist = [stack for stack in allstacks if stack['stackId']['stack'] == stack_sel]        
        stack = stack_sel
        
        if not stacklist == []:
            stackparams = stacklist[0]   
            
            if 'None' in (stackparams['stackId']['owner'],stackparams['stackId']['project']):
                    return dash.no_update
            
            out['zmin']=zmin
            out['zmax']=zmax
            out['numsections']=zmax-zmin
                     
            url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack + '/z/'+ str(out['zmin']) +'/render-parameters'
            tiles0 = requests.get(url).json()
            
            tilefile0 = os.path.abspath(tiles0['tileSpecs'][0]['mipmapLevels']['0']['imageUrl'].strip('file:'))
            
            basedirsep = params.datasubdirs[owner]
            dir_out = tilefile0[:tilefile0.find(basedirsep)]
            
            out['gigapixels']=out['numsections'] * (xmax-xmin) * (ymax-ymin)/(10**9)
            
            t_fields=[stack,str(out['numsections']),'%0.2f' % int(out['gigapixels'])]
            
            n_cpu = params.n_cpu_spark
            
            timelim = np.ceil(out['gigapixels'] / n_cpu * params.export['min/GPix/CPU_N5']*(1+params.time_add_buffer))
            
            ct_fields = [n_cpu,timelim]  
            
    trigger = hf.trigger()  
    
    if trigger == 'path_input':
        dir_out = browsedir
    
    outlist=[dir_out] #,out]   
    outlist.extend(t_fields)
    outlist.extend(ct_fields)     
        
    return outlist

# @app.callback(Output({'component': 'input1', 'module': label},'value'),
#               Input({'component': 'path_input', 'module': label},'value'))
# def input2browsestate(inpath):
#     print(inpath)
#     return inpath




# =============================================




page2 = html.Div(id={'component': 'page2', 'module': label},children=[html.H4('Output path'),
                                             dcc.Input(id={'component': "path_input", 'module': label}, type="text",debounce=True,persistence=True,className='dir_textinput'),
                                             # dcc.Input(id={'component': "path_input", 'module': label}, type="text",style={'display': 'none'})
                                             # html.Button('Browse',id={'component': "browse1", 'module': label}),
                                             # 'graphical browsing works on cluster login node ONLY!',
                                             # html.Br()
                                             ])

page.append(page2)
                                            
pathbrowse = pages.path_browse(label)

page.append(pathbrowse)



# =============================================
# Start Button

gobutton = html.Div(children=[html.Br(),
                              html.Button('Start Export',
                                          id={'component': 'go', 'module': label},disabled=True),
                              html.Div(id={'component': 'buttondiv', 'module': label}),
                              html.Br(),
                              pages.compute_loc(label,c_options=['sparkslurm'],c_default='sparkslurm'),
                              html.Br(),
                              html.Div(id={'component': 'run_state', 'module': parent}, style={'display': 'none'},children='wait')])


page.append(gobutton)


# =============================================
   
#  LAUNCH CALLBACK FUNCTION

# =============================================

# TODO! (#1) Fix store  outputs to enable additional modules

bbox=[]


for dim in ['X','Y','Z']:
    bbox.append(State({'component': 'start'+dim,'module' : parent},'value'))
    bbox.append(State({'component': 'end'+dim,'module' : parent},'value'))
    
states = [State({'component':'compute_sel','module' : label},'value'),        
          State({'component':'store_owner','module' : parent},'data'),
          State({'component':'store_project','module' : parent},'data')]

states.extend(bbox)
states.append(State({'component': 'store_stackparams', 'module': parent}, 'data'))
states.append(State({'component':'sliceim_section_in_0','module': parent},'value'))

@app.callback([Output({'component': 'go', 'module': label}, 'disabled'),
                Output({'component': 'buttondiv', 'module': label},'children'),
                Output({'component': 'store_r_launch', 'module': parent},'data'),
                Output({'component': 'store_render_launch', 'module': parent},'data')],
              [Input({'component': 'go', 'module': label}, 'n_clicks'),
               Input({'component': "path_input", 'module': label},'value'),
               Input({'component':'stack_dd','module' : parent},'value'),
               Input({'component': 'input_Num_CPUs', 'module': label},'value'),
               Input({'component': 'input_runtime_minutes', 'module': label},'value')],
              states
              ,prevent_initial_call=True)                 
def n5export_execute_gobutton(click,outdir,stack,n_cpu,timelim,comp_sel,owner,project,
                                     Xmin,Xmax,Ymin,Ymax,Zmin,Zmax,
                                     sp_store,slice_in): 
    
    if not dash.callback_context.triggered: 
            raise PreventUpdate
    
    if None in [outdir,stack,n_cpu,timelim,comp_sel,owner,project,Xmin,Xmax,Ymin,Ymax,Zmin,Zmax,
                                     sp_store,slice_in]:
        raise PreventUpdate
    
    trigger = hf.trigger()
    
    # stackparams = sp_store['stackparams']
    
    outstore = dict()
    outstore['owner'] = owner
    outstore['project'] = project
    outstore['stack'] = stack

    
    
    if 'go' in trigger:
        if click is None: return dash.no_update
        
        # prepare parameters:
        importlib.reload(params)
    
        run_params = params.render_json.copy()
        run_params['render']['owner'] = owner
        run_params['render']['project'] = project
        
        run_params_generate = run_params.copy()
          
        
        param_file = params.json_run_dir + '/' + parent + '_' + params.run_prefix + '.json' 
    
        
        
        if comp_sel == 'standalone':    
            # =============================
            
            # TODO - STANDALONE PROCEDURE NOT TESTED !!!!
            
            # =============================

            
            
            return dash.no_update
            
        elif comp_sel == 'sparkslurm':
            spsl_p = dict()
            
            spsl_p['--baseDataUrl'] = params.render_base_url + params.render_version.rstrip('/')
            spsl_p['--owner'] = owner
            spsl_p['--stack'] = stack
            spsl_p['--project'] = project
            
            
            # create output directory 
            aldir = os.path.join(outdir,params.outdirbase)
            
            if not os.path.isdir(aldir):
                os.makedirs(aldir)
            
            timestamp = params.timestamp
            
            n5dir = os.path.join(aldir,'{}{:02d}{:02d}'.format(timestamp.tm_year,timestamp.tm_mon,timestamp.tm_mday))
            
            slices = ''
            
            if Zmin == sp_store['zmin'] and Zmax == sp_store['zmax']:
                slices = '_full'
            else:
                slices = '_Z' + str(Zmin) + '-' + str(Zmax)               
                        
            n5dir += '/' + stack + slices  + '.n5'             
            
            n5run_p = dict()
            
            with open(os.path.join(params.json_template_dir,'n5export.json'),'r') as f:
                n5run_p.update(json.load(f))
                
            n5run_p['--n5Path'] = n5dir  
            
            
            # get tile size from single tile
            
            
            url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack
            url += '/z/' + str(slice_in) + '/tile-specs'
            
            tilespecs = requests.get(url).json()
            
            
            # tilesize = '{:.0f},{:.0f}'.format(tilespecs[0]['width'], tilespecs[0]['height'])
                           
            # n5run_p['--tileSize'] = tilesize
            
            
            n5run_p['--tileWidth'] = '{:.0f}'.format(tilespecs[0]['width'])
            n5run_p['--tileHeight'] = '{:.0f}'.format(tilespecs[0]['height'])
            
            blocksize = list(map(int,n5run_p['--blockSize'].split(',')))
            factors = list(map(int,n5run_p['--factors'].split(',')))
        
            for idx,dim in enumerate(['X','Y','Z']):
                                
                n5run_p['--min'+dim] = eval(dim+'min')
                n5run_p['--max'+dim] = eval(dim+'max') + 1
                
                
                # make sure blocksize and factors are not bigger than data
                
                extent = n5run_p['--max'+dim] - n5run_p['--min'+dim]                                               

                blocksize[idx] = min(blocksize[idx],extent)
                factors[idx] = min(blocksize[idx],factors[idx])
                
                
            
            # optimize block size
            
            while np.prod(blocksize) < params.min_chunksize:
                blocksize[0] *= 2
                blocksize[1] *= 2
            
            
            n5run_p['--blockSize'] = ','.join(map(str,blocksize))
            n5run_p['--factors'] = ','.join(map(str,factors))    
            
            # fill parameters
                        
            spark_p = dict()
            
            spark_p['--time'] = '00:' + str(timelim)+':00'
                        
            spark_p['--worker_cpu'] = params.cpu_pernode_spark
            spark_p['--worker_nodes'] = hf.spark_nodes(n_cpu)
            
            
            run_params_generate = spsl_p.copy()
                       
            
            run_params_generate.update(n5run_p)
            
            target_args = spark_p.copy()
            run_args = run_params_generate.copy()
            
            script = 'org.janelia.render.client.spark.n5.N5Client'            
            
            
            # #   This is how to enforce custom jar files
            
            # script = 'org.janelia.saalfeldlab.hotknife.SparkConvertRenderStackToN5'
            # script  += " --jarfile=" + params.hotknife_dir + "/target/hot-knife-0.0.4-SNAPSHOT.jar"
            
                  
   
            
        #generate script call...
        
        with open(param_file,'w') as f:
            json.dump(run_params_generate,f,indent=4)
            
        
    
        log_file = params.render_log_dir + '/' + parent + '_' + params.run_prefix
        err_file = log_file + '.err'
        log_file += '.log'

        
        sift_pointmatch_p = launch_jobs.run(target=comp_sel,pyscript=script,
                            json=param_file,run_args=run_args,target_args=target_args,logfile=log_file,errfile=err_file)
            # ['sparkslurm__12539018']
            
        params.processes[parent].extend(sift_pointmatch_p)

        
        launch_store=dict()
        launch_store['logfile'] = log_file
        
        # launch_store['logfile']='/g/emcf/software/render-logs/pointmatch_schorb_20210226-1630.log'
        
        launch_store['state'] = 'launch'
        
        return True,'', launch_store, outstore

    else:
        if outdir == '':
            return True,'No output directory selected!',dash.no_update,outstore
    
        if not os.access(outdir,os.W_OK | os.X_OK):
            return True,'Output directory not writable!',dash.no_update,outstore

        else:
            return False,'',dash.no_update,outstore
    
    
