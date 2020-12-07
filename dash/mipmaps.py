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
import importlib

from app import app



module='mipmaps_'


main=html.Div(id=module+'main',children=html.H3("Generate MipMaps for Render stack"))


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
     


page2 = html.Div(id=module+'page2',children=[html.H3('Mipmap output directory (subdirectory "mipmaps")'),
                                             dcc.Input(id=module+"input1", type="text",debounce=True,persistence=True,className='dir_textinput'),
                                             html.Button('Browse',id=module+"browse1"),' graphical browsing works on cluster login node ONLY!'
                                             ])



@app.callback([Output(module+'store','data'),
               Output(module+'owner_dd','options'),
               Output(module+'owner_dd','value'),
               Output(module+'project_dd','value'),
               Output(module+'stack_dd','value')],
              [Input('convert_'+'store','data'),
               Input(module+'page1','children')],
              State(module+'store','data'))
def update_stack_state(prevstore,page,thisstore):   

    for key in ['owner','project','stack']: thisstore[key] = prevstore[key]
    # print('mipmaps-store')
    # print(thisstore)
    
    # get list of projects on render server
    url = params.render_base_url + params.render_version + 'owners'
    owners = requests.get(url).json()
    # print(owners)    
    
    # assemble dropdown
    dd_options = list(dict())
    for item in owners: 
        dd_options.append({'label':item, 'value':item})
        
                 
    return thisstore,dd_options,thisstore['owner'],thisstore['project'],thisstore['stack']



###  SELECT STACK TO WORK....
##============================================================
#dropdown callback
@app.callback([Output(module+'browse_proj','href'),
               Output(module+'project_dd','options'),
               Output(module+'store','data')],
    Input(module+'owner_dd', 'value'),
    State(module+'store','data'))
def own_dd_sel(owner_sel,thisstore):         
    href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+owner_sel
    
   # get list of projects on render server
    url = params.render_base_url + params.render_version + 'owner/' + owner_sel + '/projects'
    projects = requests.get(url).json()
    
    # assemble dropdown
    dd_options = list(dict())
    for item in projects: 
        dd_options.append({'label':item, 'value':item})
    
    thisstore['owner'] = owner_sel
    
    return href_out, dd_options, thisstore


#dropdown callback
@app.callback([Output(module+'browse_stack','href'),
               Output(module+'stack_dd','options'),
               Output(module+'store','data')],
              Input(module+'project_dd', 'value'),
              State(module+'store','data'))
def proj_dd_sel(proj_sel,thisstore):         
    href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+thisstore['owner']+'&renderStackProject='+proj_sel
    
   # get list of projects on render server
    url = params.render_base_url + params.render_version + 'owner/' + thisstore['owner'] + '/project/' + proj_sel + '/stacks'
    stacks = requests.get(url).json()
     
    # assemble dropdown
    dd_options = list(dict())
    for item in stacks: dd_options.append({'label':item['stackId']['stack'], 'value':item['stackId']['stack']})

    
    thisstore['project'] = proj_sel
    
    return href_out, dd_options, thisstore


# ===============================================

@app.callback([Output(module+'input1','value'),
               Output(module+'store','data')],
              Input(module+'stack_dd', 'value'),
              State(module+'store','data')
              )
def stacktodir(stack_sel,thisstore):

    if stack_sel=='-':
        dir_out=''
    else:
        
        thisstore['stack'] = stack_sel
        # get list of projects on render server
        url = params.render_base_url + params.render_version + 'owner/' + thisstore['owner'] + '/project/' + thisstore['project'] + '/stack/' +thisstore['stack'] + '/zValues'
        stackslices = requests.get(url).json()
        
        url = params.render_base_url + params.render_version + 'owner/' + thisstore['owner'] + '/project/' + thisstore['project'] + '/stack/' +thisstore['stack'] + '/z/'+ str(stackslices[0]) +'/render-parameters'
        tiles0 = requests.get(url).json()
        
        tilefile0 = os.path.abspath(tiles0['tileSpecs'][0]['mipmapLevels']['0']['imageUrl'].strip('file:'))
        
        basedirsep = params.datasubdirs[thisstore['owner']]
        dir_out = tilefile0[:tilefile0.find(basedirsep)]

    
    return dir_out, thisstore


# =============================================
# Start Button

gobutton = html.Div(children=[html.Br(),
                              html.Button('Start MipMap generation & apply to current stack',id=module+"go",disabled=True),
                              html.Div(id=module+'buttondiv'),
                              html.Div(id=module+'directory-popup')])


@app.callback([Output(module+'go', 'disabled'),
               Output(module+'directory-popup','children'),
               Output(module+'store','data')],              
              Input(module+'input1','value'),
              State(module+'store','data'),
               )
def activate_gobutton(in_dir,storage):   
           
    out_pop=dcc.ConfirmDialog(        
        id=module+'danger-novaliddir',displayed=True,
        message='The selected directory does not exist or is not readable!'
        )
    if any([in_dir=='',in_dir==None]):
        if not (storage['run_state'] == 'running'): 
                storage['run_state'] = 'wait'
        return True,'No input directory chosen.',storage
    
    elif os.path.isdir(in_dir):
            if os.path.exists(os.path.join(in_dir,params.mipmapdir)):
                storage['run_state'] = 'wait'
                out_pop.message = 'Warning: there already exists a MipMap directory. Will overwrite it.'
                return False,out_pop,storage

            if not (storage['run_state'] == 'running'): 
                storage['run_state'] = 'input'
            
            return False,'',storage       
    else:
        if not (storage['run_state'] == 'running'): 
            storage['run_state'] = 'wait'
        return True, out_pop,storage
    


@app.callback([Output(module+'go', 'disabled'),
               Output(module+'store','data'),
               Output(module+'interval1','interval')
               ],
              Input(module+'go', 'n_clicks'),
              [State(module+'input1','value'),
               State(module+'store','data')]
              )                 

def execute_gobutton(click,mipmapdir,storage):    
    # prepare parameters:
    
    importlib.reload(params)
        
    param_file = params.json_run_dir + '/' + 'generate_' + module + params.run_prefix + '.json' 
    
    run_params = params.render_json.copy()
    run_params['render']['owner'] = storage['owner']
    run_params['render']['project'] = storage['project']
   
    run_params_generate = run_params.copy()
    
    
    #generate mipmaps script call...
    
    run_params_generate['input_stack'] = storage['stack']
    run_params_generate['output_dir'] = mipmapdir
    
    with open(os.path.join(params.json_template_dir,'generate_mipmaps.json'),'r') as f:
        run_params_generate.update(json.load(f))
    
    
    
    
    with open(param_file,'w') as f:
        json.dump(run_params_generate,f,indent=4)

    log_file = params.render_log_dir + '/' + 'generate_' + module + params.run_prefix
    err_file = log_file + '.err'
    log_file += '.log'
    

        
        
    #launch
    # -----------------------
    
    mipmap_generate_p = launch_jobs.run(target='slurm',pyscript='$rendermodules/rendermodules/dataimport/generate_mipmaps.py',
                    json=param_file,run_args=None,logfile=log_file,errfile=err_file)
    
    storage['log_file'] = log_file
    storage['run_state'] = 'running'
    

    return True,storage,params.refresh_interval





# =============================================
# PROGRESS OUTPUT


collapse_stdout = html.Div(children=[
                html.Br(),
                html.Div(id=module+'job-status',children=['Status of current processing run: ',html.Div(id=module+'get-status',style={"font-family":"Courier New"},children='not running')]),
                html.Br(),
                html.Details([
                    html.Summary('Console output:'),
                    html.Div(id=module+"collapse",                 
                     children=[
                         dcc.Interval(id=module+'interval1', interval=10000,
                                      n_intervals=0),
                         html.Div(id=module+'div-out',children=['Log file: ',html.Div(id=module+'outfile',style={"font-family":"Courier New"})]),
                         dcc.Textarea(id=module+'console-out',className="console_out",
                                      style={'width': '100%','height':200,"color":"#000"},disabled='True')                         
                         ])
                ])
            ],id=module+'consolebox')



@app.callback(Output(module+'console-out','value'),
    [Input(module+'interval1', 'n_intervals'),Input(module+'outfile','children')])
def update_output(n,outfile):
    data=''
    
    if outfile is not None:
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
def update_outfile(update,data):           
    return data['log_file']



@app.callback([Output(module+'get-status','children'),
              Output(module+'get-status','style')],
              Input(module+'store','data'))
def get_status(storage):
    status_style = {"font-family":"Courier New",'color':'#000'} 
    
    if storage['run_state'] == 'running':        
        status = html.Div([html.Img(src='assets/gears.gif',height=72),html.Br(),'running'])        
    elif storage['run_state'] == 'input':
        status='process will start on click.'
    else:
        status='not running'
    
    return status,status_style



# Full page layout:
    
page = [page1, page2, gobutton]
page.append(collapse_stdout)