#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 16:15:27 2020

@author: schorb
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State, MATCH, ALL

import json
import requests
import os
import importlib
import numpy as np
import subprocess


import params
from app import app

from utils import launch_jobs, pages
from utils import helper_functions as hf

from callbacks import runstate,render_selector


module='mipmaps'

storeinit = {}            
store = pages.init_store(storeinit, module)

store.append(dcc.Store(id={'component':'runstep','module':module},data='generate'))

status_table_cols = ['stack',
              'slices',
              'tiles',
              'Gigapixels']


compute_table_cols = ['Num_CPUs',
                      'runtime_minutes',
                      'section_split']

# =========================================

main=html.Div(id={'component': 'main', 'module': module},children=html.H3("Generate MipMaps for Render stack"))

intervals = html.Div([dcc.Interval(id={'component': 'interval1', 'module': module}, interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Interval(id={'component': 'interval2', 'module': module}, interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Interval(id={'component': 'interval3', 'module': module}, interval=params.idle_interval,
                                       n_intervals=0),
                      html.Div(id={'component':'tmpstore' , 'module': module})
                      ])


page = [intervals]



# # ===============================================
#  RENDER STACK SELECTOR

# Pre-fill render stack selection from previous module

us_out,us_in,us_state = render_selector.init_update_store(module,'convert')

@app.callback(us_out,us_in,us_state)
def mipmaps_update_store(*args): 
    return render_selector.update_store(*args)

page1 = pages.render_selector(module)

page.append(page1)

# # ===============================================
#  SPECIFIC PAGE CONTENT


page2 = html.Div(id={'component': 'page2', 'module': module},children=[html.H3('Mipmap output directory (subdirectory "mipmaps")'),
                                             dcc.Input(id={'component': "input1", 'module': module}, type="text",debounce=True,persistence=True,className='dir_textinput'),
                                             html.Button('Browse',id={'component': "browse1", 'module': module}),
                                             'graphical browsing works on cluster login node ONLY!',
                                             html.Br()])

page.append(page2)



# # ===============================================
# Compute Settings

compute_settings = html.Details(id={'component': 'compute', 'module': module},children=[html.Summary('Compute settings:'),
                                             html.Table([html.Tr([html.Th(col) for col in status_table_cols]),
                                                  html.Tr([html.Td('',id={'component': 't_'+col, 'module': module}) for col in status_table_cols])
                                             ],className='table'),
                                             html.Br(),
                                             html.Table([html.Tr([html.Th(col) for col in compute_table_cols]),
                                                  html.Tr([html.Td(dcc.Input(id={'component': 'input_'+col, 'module': module},type='number',min=1)) for col in compute_table_cols])
                                             ],className='table'),
                                             dcc.Store(id={'component':'store_compset','module':module})
                                             ])
page.append(compute_settings)



# callbacks

@app.callback(Output({'component':'store_compset','module':module},'data'),                            
              [Input({'component': 'input_'+col, 'module': module},'value') for col in compute_table_cols]
              )
def mipmaps_store_compute_settings(*inputs): 
    
    storage=dict()
        
    in_labels,in_values  = hf.input_components()
    
    for input_idx,label in enumerate(in_labels):
        
        storage[label] = in_values[input_idx]
    
    return storage




# Update directory and compute settings from stack selection

stackoutput = [Output({'component': 'input1', 'module': module},'value'),
               Output({'component': 'store_stack', 'module': module}, 'data'),
               Output({'component': 'store_stackparams', 'module': module}, 'data')]
tablefields = [Output({'component': 't_'+col, 'module': module},'children') for col in status_table_cols]
compute_tablefields = [Output({'component': 'input_'+col, 'module': module},'value') for col in compute_table_cols]

stackoutput.extend(tablefields)  
stackoutput.extend(compute_tablefields)        

@app.callback(stackoutput,
              Input({'component': 'stack_dd', 'module': module},'value'),
              [State({'component': 'store_owner', 'module': module}, 'data'),
               State({'component': 'store_project', 'module': module}, 'data'),
               State({'component': 'store_stack', 'module': module}, 'data'),
               State({'component': 'store_allstacks', 'module': module}, 'data')]
              )
def mipmaps_stacktodir(stack_sel,owner,project,stack,allstacks):
    
    dir_out=''
    out=dict()
    
    t_fields = ['']*len(status_table_cols)
    ct_fields = [1]*len(compute_table_cols)

    
    if (not stack_sel=='-' ) and (not allstacks is None):   
        stacklist = [stack for stack in allstacks if stack['stackId']['stack'] == stack_sel]        
        stack = stack_sel
        
        if not stacklist == []:
            stackparams = stacklist[0]        
            out['zmin']=stackparams['stats']['stackBounds']['minZ']
            out['zmax']=stackparams['stats']['stackBounds']['maxZ']
            out['numtiles']=stackparams['stats']['tileCount']
            out['numsections']=stackparams['stats']['sectionCount']
         
            num_blocks = int(np.max((np.floor(out['numsections']/params.section_split),1)))
            
            url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack + '/z/'+ str(out['zmin']) +'/render-parameters'
            tiles0 = requests.get(url).json()
            
            tilefile0 = os.path.abspath(tiles0['tileSpecs'][0]['mipmapLevels']['0']['imageUrl'].strip('file:'))
            
            basedirsep = params.datasubdirs[owner]
            dir_out = tilefile0[:tilefile0.find(basedirsep)]
            
            out['gigapixels']=out['numtiles']*stackparams['stats']['maxTileWidth']*stackparams['stats']['maxTileHeight']/(10**9)
            
            t_fields=[stack,str(stackparams['stats']['sectionCount']),str(stackparams['stats']['tileCount']),'%0.2f' %out['gigapixels']]
            
            n_cpu = params.n_cpu_script
            
            timelim = np.ceil(out['gigapixels'] / n_cpu * params.mipmaps['min/Gpix/CPU']*(1+params.time_add_buffer)/num_blocks)
            
            ct_fields = [n_cpu,timelim,params.section_split]  
          
   
    outlist=[dir_out,stack,out]   
    outlist.extend(t_fields)
    outlist.extend(ct_fields)     
    
    return outlist






# =============================================
# Start Button

gobutton = html.Div(children=[html.Br(),
                              html.Button('Start MipMap generation & apply to current stack',id={'component': 'go', 'module': module},disabled=True),
                              html.Div(id={'component': 'buttondiv', 'module': module}),
                              html.Div(id={'component': 'directory-popup', 'module': module}),
                              html.Br(),
                              pages.compute_loc(module),
                              html.Br(),
                              html.Div(id={'component': 'run_state', 'module': module}, style={'display': 'none'},children='wait')])


page.append(gobutton)


@app.callback([Output({'component': 'go', 'module': module}, 'disabled'),
                Output({'component':'directory-popup' , 'module': module},'children'),
                Output({'component': 'run_state', 'module': module},'children'),
                Output({'component':'runstep','module':module},'data'),
                Output({'component': 'store_r_launch', 'module': module},'data'),
                Output({'component': 'interval3', 'module': module},'interval')],              
              [Input({'component': 'input1', 'module': module},'value'),
               Input({'component': 'go', 'module': module}, 'n_clicks'),
               Input({'component': 'interval3', 'module': module},'n_intervals')],
              [State({'component':'store_run_state','module':module},'data'),
               State({'component': 'compute_sel', 'module': module},'value'),
               State({'component':'runstep','module':module},'data'),
               State({'component': 'store_owner', 'module': module},'data'),
               State({'component': 'store_project', 'module': module},'data'),
               State({'component': 'store_stack', 'module': module}, 'data'),
               State({'component': 'store_stackparams', 'module': module}, 'data'),
               State({'component': 'store_compset', 'module': module}, 'data'),
               State({'component': 'go', 'module': module}, 'disabled'),
               State({'component':'directory-popup' , 'module': module},'children'),
               State({'component':'outfile' , 'module': module},'children'),
               State({'component': 'interval3', 'module': module},'interval')]
              , prevent_initial_call=True)
def mipmaps_gobutton(mipmapdir,click,click2,run_state,comp_sel,runstep_in,owner,project,stack,stackparams,comp_set,disable_out,dircheckdiv,logfile,interval):
    trigger = hf.trigger_component()    
    
    # init output    
    
    rstate = 'wait'  
    runstep = runstep_in
    
    print('------ launch ------')
    print(runstep)
    print(run_state)
    print(trigger)
    print(logfile)  
    
    launch_store = dash.no_update
    
    if logfile is None:
        logfile = params.render_log_dir + '/out.txt'
        launch_store=dict()
        launch_store['logfile'] = logfile
        launch_store['state'] = 'wait'
        run_state = 'wait'
        
        
    out_pop=dcc.ConfirmDialog(        
        id={'component': 'danger-novaliddir', 'module': module},displayed=True,
        message='The selected directory does not exist or is not writable!'
        )
    
    # ------------------------------------
    # activate button, prepare launch
    
    if 'input1' in trigger:
        interval = params.idle_interval

        disable_out = True
        if any([mipmapdir=='',mipmapdir==None]):
            if not (run_state == 'running'): 
                    rstate = 'wait'
        
        elif os.path.isdir(mipmapdir):
                if os.path.exists(os.path.join(mipmapdir,params.mipmapdir)):
                    rstate = 'input'
                    out_pop.message = 'Warning: there already exists a MipMap directory. Will overwrite it.'
                    disable_out = False
                    dircheckdiv = out_pop
                    
    
                if not (runstate == 'running'): 
                    rstate = 'input'
                    disable_out = False
  
        else:
            if not (run_state == 'running'): 
                rstate = 'wait'
                dircheckdiv = [out_pop, 'The selected directory does not exist or is not writable!']
    
    
    
    # ------------------------------------
    #  button   pressed,  launch
                  
                
    elif 'go' in trigger:
        disable_out = True
        interval = params.idle_interval * 0.4
        importlib.reload(params)
        runstep = 'generate'
        
        run_params = params.render_json.copy()
        run_params['render']['owner'] = owner
        run_params['render']['project'] = project
       
        run_params_generate = run_params.copy()
        
        
        #generate mipmaps script call...
        
        run_params_generate['input_stack'] = stack
        
        mipmapdir += '/mipmaps'
        
        if not os.path.exists(mipmapdir): os.makedirs(mipmapdir)
        
        run_params_generate['output_dir'] = mipmapdir
        
        with open(os.path.join(params.json_template_dir,'generate_mipmaps.json'),'r') as f:
                run_params_generate.update(json.load(f))
            
        sec_start = stackparams['zmin']
        sliceblock_idx = 0
        sec_end = sec_start
        
        while sec_end <= stackparams['zmax']:
            sec_end = int(np.min([sec_start+comp_set['input_section_split'],stackparams['zmax']]))
            run_params_generate['zstart'] = sec_start
            run_params_generate['zend'] = sec_end
            
            run_params_generate['output_json'] = os.path.join(params.json_run_dir,'output_' + module + '_'  + params.run_prefix + '_' + str(sliceblock_idx)+'.json' )
            
            param_file = params.json_run_dir + '/' + runstep+ '_' + module + params.run_prefix + '_' + str(sliceblock_idx)+'.json' 
        
                   
            with open(param_file,'w') as f:
                json.dump(run_params_generate,f,indent=4)
        
            log_file = params.render_log_dir + '/' + runstep + '_' + module + '_'  + params.run_prefix+ '_' + str(sliceblock_idx)
            err_file = log_file + '.err'
            log_file += '.log'
            
            
            sec_start = sec_end + 1
            sec_end = sec_start
            sliceblock_idx += 1
        
                
                
            #launch
            # -----------------------
            
            
            # check resource settings
            target_args=None
            
            if comp_sel == 'slurm':                
    
                slurm_args=['-N1']
                slurm_args.append('-n1')
                slurm_args.append('-c '+str(comp_set['input_Num_CPUs']))
                slurm_args.append('--mem  '+str(params.mem_per_cpu)+'G')
                slurm_args.append('-t 00:%02i:00' %comp_set['input_runtime_minutes'])
                
                target_args=slurm_args
            
            
            
            mipmap_generate_p = launch_jobs.run(target=comp_sel,pyscript='$rendermodules/rendermodules/dataimport/generate_mipmaps.py',
                            json=param_file,run_args=None,target_args=target_args,logfile=log_file,errfile=err_file)
            
            params.processes[module.strip('_')].extend(mipmap_generate_p)
        
        launch_store=dict()
        launch_store['logfile'] = log_file
        launch_store['state'] = 'running'
        
 
    # ------------------------------------
    # launch apply mipmaps task when generate mipmaps task has completed successfully
    
        
    elif 'interval3' in trigger:        
        
        if runstep == 'generate' and run_state == 'done' and mipmapdir is not None:
                interval = params.idle_interval * 0.4

                runstep = 'apply'
                importlib.reload(params)
                
                run_params = params.render_json.copy()
                run_params['render']['owner'] = owner
                run_params['render']['project'] = project
                
                mipmapdir += '/mipmaps/'
                
                run_params_generate = run_params.copy()
                
                with open(os.path.join(params.json_template_dir,'apply_mipmaps.json'),'r') as f:
                        run_params_generate.update(json.load(f))
                    
                # run_params_generate['output_json'] = os.path.join(params.json_run_dir,'output_' + module + params.run_prefix + '.json' )
                run_params_generate["input_stack"] = stack
                run_params_generate["output_stack"] = stack + "_mipmaps"
                run_params_generate["mipmap_prefix"] = "file://" + mipmapdir
                
                param_file = params.json_run_dir + '/' + runstep + '_' + module + '_' + params.run_prefix + '.json' 
                run_params_generate["zstart"] = stackparams['zmin']
                run_params_generate["zend"] = stackparams['zmax']
                run_params_generate["pool_size"] = params.n_cpu_script
                       
                with open(param_file,'w') as f:
                    json.dump(run_params_generate,f,indent=4)
            
                log_file = params.render_log_dir + '/' + runstep + '_' + module + '_' + params.run_prefix
                err_file = log_file + '.err'
                log_file += '.log'
                
                mipmap_apply_p = launch_jobs.run(target=comp_sel,pyscript='$rendermodules/rendermodules/dataimport/apply_mipmaps_to_render.py',
                              json=param_file,run_args=None,logfile=log_file,errfile=err_file)
                
                params.processes[module.strip('_')] = [mipmap_apply_p]
                launch_store=dict()
                launch_store['logfile'] = log_file
                launch_store['state'] = html.Div([html.Img(src='assets/gears.gif',height=72),html.Br(),'running apply mipmaps to stack'])
                
        elif runstep == 'apply' and run_state == 'done' and mipmapdir is not None:
                interval = params.idle_interval

                launch_store=dict()
                launch_store['state'] = 'done'
                launch_store['logfile'] = logfile
                params.processes[module.strip('_')]=[]
    
    print(launch_store)
        
    return disable_out, dircheckdiv, rstate, runstep, launch_store, interval



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
