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

from app import app
from utils import launch_jobs

import importlib




module='tilepairs_'




main=html.Div(id=module+'main',children=html.H3("Generate TilePairs for Render stack"))

intervals = html.Div([dcc.Interval(id=module+'interval1', interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Interval(id=module+'interval2', interval=params.idle_interval,
                                       n_intervals=0)
                      ])

page1 = html.Div(id=module+'page1',children=[html.H4('Current active stack:'),
                                             html.Div([html.Div('Owner:',style={'margin-right': '1em','margin-left': '2em'}),
                                                       dcc.Dropdown(id=module+'owner_dd',className='dropdown_inline',style={'width':'120px'},
                                                          persistence=True,
                                                          clearable=False),
                                                       html.Div('Project',style={'margin-left': '2em'}),
                                                       html.A('(Browse)',id=module+'browse_proj',target="_blank",style={'margin-left': '0.5em','margin-right': '1em'}),
                                                       dcc.Dropdown(id=module+'project_dd',className='dropdown_inline',
                                                          persistence=True,
                                                          clearable=False),
                                                       html.Div('Stack',style={'margin-left': '2em'}),
                                                       html.A('(Browse)',id=module+'browse_stack',target="_blank",style={'margin-left': '0.5em','margin-right': '1em'}),
                                                       dcc.Dropdown(id=module+'stack_dd',className='dropdown_inline',
                                                          persistence=True,
                                                          clearable=False)
                                             
                                             ],style=dict(display='flex'))
                                             ])


page2 = html.Div(id=module+'page2',children=[html.H4('Pair assignment mode'),
                                             html.Div(
                                                 [dcc.RadioItems(
                                                     options=[
                                                         {'label': '2D (tiles in montage/mosaic)', 'value': '2D'},
                                                         {'label': '3D (across sections)', 'value': '3D'}
                                                         ],
                                                     value='2D',                                                
                                                     id=module+'pairmode'
                                                     ),
                                                 html.Div(id=module+'3Dslices',children=[
                                                 'range of sections to consider:  ',
                                                 dcc.Input(id=module+'input_1',type='number',min=1,max=10,value=0)],
                                                     style={'display':'none'})]
                                                 ,style={'display':'inline,block'}),
                                             html.Br(),
                                             html.Details([html.Summary('Substack selection'),
                                                           html.Table([html.Tr([html.Td('Start slice: '),
                                                                               html.Td(dcc.Input(id=module+'startsection',type='number',min=0,value=0))]),
                                                                       html.Tr([html.Td('End slice: '),
                                                                               html.Td(dcc.Input(id=module+'endsection',type='number',min=0,value=1))])])
                                                           ])
                                             ])
                                                                           



gobutton = html.Div(children=[html.Br(),
                              html.Button('Start TilePair generation',id=module+"go"),
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




# # ===============================================

@app.callback([Output(module+'owner_dd','options'),
               Output(module+'owner_dd','value'),
                Output(module+'store','data')],
                Input('url', 'pathname'),
                State(module+'store','data'))
def tilepairs_init_page(page,storage):
    url = params.render_base_url + params.render_version + 'owners'
    owners = requests.get(url).json()
    
        # assemble dropdown
    dd_options = list(dict())
    for item in owners: 
        dd_options.append({'label':item, 'value':item})
    
    storage['all_owners']=owners
    
    return dd_options,owners[0], storage
    


@app.callback([Output(module+'owner_dd','options'),
                Output(module+'store','data'),               
                Output(module+'owner_dd','value'),
                Output(module+'project_dd','value'),
                Output(module+'stack_dd','value')
                ],
              [Input('mipmaps_'+'store','data'),
                Input('url', 'pathname')],
              [State(module+'store','data')])
def tilepairs_update_stack_state(prevstore,page,thisstore):  
    
    if 'all_owners' in thisstore.keys():
        
        for key in ['owner','project','stack']: 
            if key in prevstore.keys() and not prevstore[key]=='-':
                thisstore[key] = prevstore[key]
                
                
        # print('mipmaps-store')
        # print(thisstore)
        owners = thisstore['all_owners']
        
                # assemble dropdown
        dd_options = list(dict())
        for item in owners: 
            dd_options.append({'label':item, 'value':item})
        
        thisstore['run_state'] = 'input'
        
         
    else:
        dd_options = [] 
        
    return dd_options,thisstore,thisstore['owner'],thisstore['project'],thisstore['stack']







###  SELECT STACK TO WORK....
##============================================================
#dropdown callback
@app.callback([Output(module+'browse_proj','href'),
                Output(module+'project_dd','options'),
                Output(module+'project_dd','value'),
                Output(module+'store','data')],
              Input(module+'owner_dd', 'value'),
              State(module+'store','data'))
def tilepairs_own_dd_sel(owner_sel,thisstore):
    href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+owner_sel

    # get list of projects on render server
    url = params.render_base_url + params.render_version + 'owner/' + owner_sel + '/projects'
    projects = requests.get(url).json()

    # assemble dropdown
    dd_options = list(dict())
    for item in projects: 
        dd_options.append({'label':item, 'value':item})
    
    thisstore['owner'] = owner_sel
    
    return href_out, dd_options, thisstore['project'], thisstore


# #dropdown callback
@app.callback([Output(module+'browse_stack','href'),
                Output(module+'stack_dd','options'),
                Output(module+'stack_dd','value'),
                Output(module+'store','data')],
              Input(module+'project_dd', 'value'),
              State(module+'store','data'))
def tilepairs_proj_dd_sel(proj_sel,thisstore): 
        
    href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+thisstore['owner']+'&renderStackProject='+proj_sel
    # get list of projects on render server
    url = params.render_base_url + params.render_version + 'owner/' + thisstore['owner'] + '/project/' + proj_sel + '/stacks'
    stacks = requests.get(url).json()
     
    # assemble dropdown
    dd_options = list(dict())
    for item in stacks: dd_options.append({'label':item['stackId']['stack'], 'value':item['stackId']['stack']})
    
    if thisstore['stack']+'_mipmaps' in  [stacks[i]['stackId']['stack'] for i in range(len(stacks))]:
            thisstore['stack'] = thisstore['stack']+'_mipmaps'
           
    
    thisstore['project'] = proj_sel
    thisstore['allstacks'] = stacks

    return href_out, dd_options, thisstore['stack'],thisstore


# # ===============================================



@app.callback([Output(module+'startsection','value'),
                Output(module+'startsection','min'),
                Output(module+'endsection','value'),
                Output(module+'endsection','max'),],
              Input(module+'stack_dd', 'value'),
              State(module+'store','data')
              )
def tilepairs_stacktosections(stack_sel,thisstore):

    if stack_sel=='-' or not 'allstacks' in thisstore.keys():   
        
        sec_start = 0
        sec_end = 1
        
    
    else:        
        stackparams = [stack for stack in thisstore['allstacks'] if stack['stackId']['stack'] == stack_sel][0]        
        thisstore['stack'] = stackparams['stackId']['stack']
        thisstore['stackparams'] = stackparams
        thisstore['zmin']=stackparams['stats']['stackBounds']['minZ']
        thisstore['zmax']=stackparams['stats']['stackBounds']['maxZ']
        thisstore['numtiles']=stackparams['stats']['tileCount']
        thisstore['numsections']=stackparams['stats']['sectionCount']
        
        
        sec_start = int(thisstore['zmin'])
        sec_end = int(thisstore['zmax'])

    return sec_start, sec_start, sec_end, sec_end



@app.callback([Output(module+'startsection','max'),
                Output(module+'endsection','min')],
              [Input(module+'startsection', 'value'),
                Input(module+'endsection','value'),
                Input(module+'input_1','value')]
              )
def tilepairs_sectionlimits(start_sec,end_sec,sec_range):
    
    if not sec_range is None and not start_sec is None and not end_sec is None:
        return end_sec - sec_range, start_sec + sec_range
    else:
        return end_sec, start_sec




# # ===============================================

@app.callback([Output(module+'3Dslices','style'),
                Output(module+'input_1','value')],
              Input(module+'pairmode','value'))
def tilepairs_3D_status(pairmode):

    if pairmode == '2D':
        style = {'display':'none'}
        val = 0
    elif pairmode == '3D':
        style = {'display':'block'}
        val = 1
    return style, val



@app.callback([Output(module+'go', 'disabled'),
                Output(module+'store','data'),
                Output(module+'interval1','interval')
                ],
              Input(module+'go', 'n_clicks'),
              [State(module+'input_1','value'),
                State(module+'compute_sel','value'),
                State(module+'pairmode','value'),
                State(module+'startsection','value'),
                State(module+'endsection','value'),
                State(module+'store','data')]
              )                 
def tilepairs_execute_gobutton(click,slicedepth,comp_sel,pairmode,startsection,endsection,storage):   
    
    if click>0:
        
        # prepare parameters:
        importlib.reload(params)
    
        run_params = params.render_json.copy()
        run_params['render']['owner'] = storage['owner']
        run_params['render']['project'] = storage['project']
       
        run_params_generate = run_params.copy()
        
        
        #generate script call...
        
        tilepairdir = params.json_run_dir + '/tilepairs_' + params.run_prefix + '_'+ storage['stack'] + '_' + pairmode
        
        if not os.path.exists(tilepairdir): os.makedirs(tilepairdir)
        
        run_params_generate['output_dir'] = tilepairdir
        
        with open(os.path.join(params.json_template_dir,'tilepairs.json'),'r') as f:
                run_params_generate.update(json.load(f))
        
        run_params_generate['output_json'] = tilepairdir + '/tiles_'+ storage['stack'] + '_' + pairmode
        
        run_params_generate['minZ'] = startsection
        run_params_generate['maxZ'] = endsection
        
        run_params_generate['stack'] = storage['stack']
        
        if pairmode == '2D':
            run_params_generate['zNeighborDistance'] = 0
            run_params_generate['excludeSameLayerNeighbors'] = 'False'
            
        elif pairmode == '3D':
            run_params_generate['zNeighborDistance'] = slicedepth
            run_params_generate['excludeSameLayerNeighbors'] = 'True'
    
    
        param_file = params.json_run_dir + '/' + module + params.run_prefix + '_' + pairmode + '.json' 
    
               
        with open(param_file,'w') as f:
            json.dump(run_params_generate,f,indent=4)
    
        log_file = params.render_log_dir + '/' + module + params.run_prefix + '_' + pairmode
        err_file = log_file + '.err'
        log_file += '.log'
        
        tilepairs_generate_p = launch_jobs.run(target=comp_sel,pyscript='$rendermodules/rendermodules/pointmatch/create_tilepairs.py',
                            json=param_file,run_args=None,target_args=None,logfile=log_file,errfile=err_file)
            
        params.processes[module.strip('_')].extend(tilepairs_generate_p)
        
        storage['run_state'] = 'running'
        storage['log_file'] = log_file
        storage['tilepairdir'] = tilepairdir
        
        return True,storage,params.refresh_interval


# =============================================
# Processing status




@app.callback([Output(module+'interval2','interval'),
                Output(module+'store','data')],
              Input(module+'interval2','n_intervals'),
              State(module+'store','data'))
def tilepairs_update_status(n,storage):  
    if n>0:        
        status = storage['run_state']
        procs=params.processes[module.strip('_')]
        if not 'Error' in status:
            if procs==[]:
                if storage['run_state'] not in ['input','wait']:
                    storage['run_state'] = 'input'               
            
            if (type(procs) is subprocess.Popen or len(procs)>0): 
                status = launch_jobs.status(procs)   
                storage['run_state'] = status    
        
        if 'Error' in status: 
            if storage['log_file'].endswith('.log'):
                storage['log_file'] = storage['log_file'][:storage['log_file'].rfind('.log')]+'.err'
            
    return params.idle_interval,storage 
    

cancelbutton = html.Button('cancel cluster job(s)',id=module+"cancel")


@app.callback([Output(module+'get-status','children'),
              Output(module+'get-status','style'),
              Output(module+'interval1', 'interval'),
              Output(module+'go', 'disabled')],
              Input(module+'store','data'),
                [State(module+'compute_sel','value'),
                State(module+'input_1','value')])
def tilepairs_get_status(storage,comp_sel,mipmapdir):
    status_style = {"font-family":"Courier New",'color':'#000'} 
    log_refresh = params.idle_interval
    procs=params.processes[module.strip('_')]
    go_disabled = False     
    
    if storage['run_state'] == 'running':
        if procs == []:
            status = 'not running'
        else:
            go_disabled = True
            status = html.Div([html.Img(src='assets/gears.gif',height=72),html.Br(),'running'])
            log_refresh = params.refresh_interval
            if not type(procs) is subprocess.Popen:
                if  type(procs) is str:
                    status = html.Div([html.Img(src='assets/gears.gif',height=72),html.Br(),'running  -  ',cancelbutton])
                elif not type(procs[0]) is subprocess.Popen:
                    status = html.Div([html.Img(src='assets/gears.gif',height=72),html.Br(),'running  -  ',cancelbutton])
                   
    elif storage['run_state'] == 'input':
        status='process will start on click.'
    elif storage['run_state'] == 'done':        
        status='DONE'
        status_style = {'color':'#0E0'}
            
    elif storage['run_state'] == 'pending':
        status = ['Waiting for cluster resources to be allocated.',cancelbutton]
    elif storage['run_state'] == 'wait':
        status='not running'
    else:
        status=storage['run_state']
    
    
    return status,status_style,log_refresh,go_disabled




@app.callback([Output(module+'get-status','children'),
                Output(module+'store','data')],
              Input(module+'cancel', 'n_clicks'),
              State(module+'store','data'))
def tilepairs_cancel_jobs(click,storage):

    procs = params.processes[module.strip('_')]
    
    p_status = launch_jobs.canceljobs(procs)
    
    params.processes[module.strip('_')] = []    
    
    storage['run_state'] = p_status
    
    return p_status,storage
    

# # =============================================
# # PROGRESS OUTPUT


collapse_stdout = html.Div(children=[
                html.Br(),
                html.Div(id=module+'job-status',children=['Status of current processing run: ',html.Div(id=module+'get-status',style={"font-family":"Courier New"},children='not running')]),
                html.Br(),
                html.Details([
                    html.Summary('Console output:'),
                    html.Div(id=module+"collapse",                 
                      children=[
                          html.Div(id=module+'div-out',children=['Log file: ',html.Div(id=module+'outfile',style={"font-family":"Courier New"})]),
                          dcc.Textarea(id=module+'console-out',className="console_out",
                                      style={'width': '100%','height':200,"color":"#000"},disabled='True')                         
                          ])
                ])
            ],id=module+'consolebox')



@app.callback(Output(module+'console-out','value'),
    [Input(module+'interval1', 'n_intervals'),Input(module+'outfile','children')])
def tilepairs_update_output(n,outfile):
    data=''
    
    if outfile is not None:
        if os.path.exists(outfile):
            file = open(outfile, 'r')    
            lines = file.readlines()
            if lines.__len__()<=params.disp_lines:
                last_lines=lines
            else:
                last_lines = lines[-params.disp_lines:]
            for line in last_lines:
                data=data+line
            file.close()   
        
    return data



@app.callback(Output(module+'outfile', 'children'),
              [Input(module+'page1', 'children'),
                Input(module+'store', 'data')]
              )
def tilepairs_update_outfile(update,data):           
    return data['log_file']



# Full page layout:
    
page = [intervals,page1, page2, gobutton]
page.append(collapse_stdout)