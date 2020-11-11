#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 08:42:12 2020

@author: schorb
"""
import dash_core_components as dcc
import dash_html_components as html
import subprocess
# import sys
import os
import socket
#for file browsing dialogs
import tkinter
from tkinter import filedialog

from dash.dependencies import Input,Output,State
import json
import requests
import importlib


from app import app
import params
from utils import launch_jobs


# element prefix
label = "sbem_conv_"


# SELECT input directory

# get user name and main group to pre-polulate input directory

p=subprocess.Popen('id -gn',stdout=subprocess.PIPE,shell=True)
group = p.communicate()[0].decode(encoding='utf8').strip("\n")

directory_sel = html.Div(children=[html.H4("Select dataset root directory:"),
                                   html.Script(type="text/javascript",children="alert('test')"),                                   
                          dcc.Input(id=label+"input1", type="text", debounce=True,placeholder="/g/"+group,persistence=True),
                          html.Button('Browse',id=label+"browse1"),' graphical browsing works on cluster login node ONLY!',
                          html.Div(id=label+'warning-popup')])




@app.callback([Output(label+'input1', 'value'),Output(label+'warning-popup','children')],
    [Input(label+'browse1', 'n_clicks')])
def convert_filebrowse1(click):
    
    hostname = socket.gethostname()
    
    if hostname=='login-gui.cluster.embl.de':    
        root = tkinter.Tk()
        root.withdraw()
        conv_inputdir = filedialog.askdirectory()
        root.destroy()
        outpage=''
    else:
        outpage=dcc.ConfirmDialog(        
        id=label+'danger-wrong_host',displayed=True,
        message='This functionality only works when accessing this page from the graphical login node.'
        )
        conv_inputdir = ''
    return conv_inputdir,outpage





# ============================
# set up render parameters

owner = "SBEM"
#------------------
# SET PROJECT

# get list of projects on render server
url = params.render_base_url + params.render_version + 'owner/' + owner + '/projects'
projects = requests.get(url).json()

orig_projdiv=html.Div(id=label+'orig_proj',style={'display':'none'},children=projects)


# assemble dropdown
dd_options = [{'label':'Create new Project', 'value':'newproj'}]
for item in projects: 
    dd_options.append({'label':item, 'value':item})


project_dd = html.Div([html.H4("Select Render Project:"),
                       dcc.Dropdown(id=label+'project_dd',persistence=True,
                                    options=dd_options,clearable=False,value=projects[0]),
                       html.Br(),
                       html.Div(id=label+'render_project',style={'display':'none'}),                               
                       html.Div([html.Br(),html.A('Browse Project',href=params.render_base_url+'view/stacks.html?renderStackOwner='+owner,
                                id=label+'browse_proj',target="_blank")]),
                       orig_projdiv
                       ])

                       
#dropdown callback
@app.callback([Output(label+'browse_proj','href'),
               Output(label+'render_project','children'),
               Output(label+'render_project','style')],
    Input(label+'project_dd', 'value'))
def proj_dd_sel(project_sel):     
    if project_sel=='newproj':       
        href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+owner+'&renderStackProject='+project_sel
        divstyle = {'display':'block'}                       
        div_out = ['Enter new project name: ',
                   dcc.Input(id=label+"proj_input", type="text", debounce=True,placeholder="new_project",persistence=False)
                   ]
    else:
        div_out = project_sel
        divstyle = {'display':'none'}
        href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+owner+'&renderStackProject='+project_sel
    return [href_out,div_out,divstyle]

# Create a new Project

@app.callback([Output(label+'project_dd', 'options'),Output(label+'project_dd', 'value')],
              [Input(label+'proj_input', 'value')],
              State(label+'project_dd', 'options'))
def new_proj(project_name,dd_options): 
    dd_options.append({'label':project_name, 'value':project_name})
    return dd_options,project_name

#------------------
# SET STACK


stack_div = html.Div(id=label+'sbem_conv_stack_div',children=[html.H4("Select Render Stack:"),
                                                              dcc.Dropdown(id=label+'stack_dd',persistence=True,
                                                                           options=dd_options,clearable=False,style={'display':'none'}),
                                                              html.Div(id=label+'stack_state',style={'display':'none'},children=''),
                                                              html.Br(),
                                                              html.Div(id=label+'newstack'),                                                          
                                                              html.A('Browse Stack',href=params.render_base_url+'view/stacks.html?renderStackOwner='+owner,
                                                                     id=label+'browse_stack',target="_blank"),
                                                              html.Br(),]
                       )


@app.callback([Output(label+'stack_dd','options'),   
               Output(label+'stack_dd','style'), 
               Output(label+'stack_state','children')],
    [Input(label+'project_dd', 'value'),
     Input(label+'orig_proj','children')],
    )
def proj_stack_activate(project_sel,orig_proj):    
    
    dd_options = [{'label':'Create new Stack', 'value':'newstack'}]
    
    if project_sel in orig_proj:
        # get list of STACKS on render server
        url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project_sel + '/stacks'
        stacks = requests.get(url).json()  
        
        # assemble dropdown
        
        for item in stacks: dd_options.append({'label':item['stackId']['stack'], 'value':item['stackId']['stack']})
                
        return dd_options, {'display':'block'}, stacks[0]['stackId']['stack']
        
    else:    
        return dd_options,{'display':'none'}, 'newstack'
    
    
            
@app.callback(Output(label+'stack_state','children'),
    Input(label+'stack_dd','value'))
def update_stack_state(stack_dd):        
    return stack_dd

    
@app.callback([Output(label+'browse_stack','href'),Output(label+'browse_stack','style')],
    Input(label+'stack_state','children'),
    State(label+'project_dd', 'value'))
def update_stack_browse(stack_state,project_sel):      
    if stack_state == 'newstack':
        return params.render_base_url, {'display':'none'}
    else:
        return params.render_base_url+'view/stack-details.html?renderStackOwner='+owner+'&renderStackProject='+project_sel+'&renderStack='+stack_state, {'display':'block'}
                                
    
@app.callback(Output(label+'newstack','children'),
    Input(label+'stack_state','children'))
def new_stack_input(stack_value):
    if stack_value=='newstack':
        st_div_out = ['Enter new stack name: ',
                   dcc.Input(id=label+"stack_input", type="text", debounce=True,placeholder="new_stack",persistence=False)
                   ]
    else:
        st_div_out = ''
    
    return st_div_out



@app.callback([Output(label+'stack_dd', 'options'),
               Output(label+'stack_dd', 'value'),
               Output(label+'stack_dd','style')],
              [Input(label+'stack_input', 'value')],
              State(label+'stack_dd', 'options'))
def new_stack(project_name,dd_options): 
    dd_options.append({'label':project_name, 'value':project_name})
    return dd_options,project_name,{'display':'block'}

 


# =============================================
# Start Button

gobutton = html.Div(children=[html.Br(),
                              html.Button('Start conversion',id=label+"go",disabled=True),
                              html.Div(id=label+'buttondiv'),
                              html.Div(id=label+'directory-popup')])


@app.callback([Output(label+'go', 'disabled'),
               Output(label+'directory-popup','children')],              
              [Input(label+'stack_state', 'children'),
               Input(label+'input1','value')],
              [State(label+'project_dd', 'value')],
               )
def activate_gobutton(stack_state1,in_dir,proj_dd_sel1):           
    out_pop=dcc.ConfirmDialog(        
        id=label+'danger-novaliddir',displayed=True,
        message='The selected directory does not exist or is not readable!'
        )

    if any([in_dir=='',in_dir==None]):
        return True,'No input directory chosen.'    
    elif os.path.isdir(in_dir):        
        if any([stack_state1=='newstack', proj_dd_sel1=='newproj']):
            return True,''
        else:
            return False,''
        
    else:
        return True, out_pop

@app.callback(Output(label+'input1','value'),
              [Input(label+'danger-novaliddir','submit_n_clicks'),
                Input(label+'danger-novaliddir','cancel_n_clicks')])
def dir_warning(sub_c,canc_c):
    return ''
        
    
    
# =============================================
   
#  LAUNCH CALLBACK FUNCTION

# =============================================
  
    

@app.callback([Output(label+'go', 'disabled'),
               Output(label+'outfile','children'),
               Output(label+'interval1','interval')],
              Input(label+'go', 'n_clicks'),
              [State(label+'input1','value'),               
               State(label+'project_dd', 'value'),
               State(label+'stack_state', 'children'),
               State(label+'outfile','children')]
              )                 

def execute_gobutton(click,sbemdir,proj_dd_sel,stack_sel,outfile):    
    # prepare parameters:
    
    importlib.reload(params)
        
    param_file = params.json_run_dir + '/' + 'sbem_conv-' + params.run_prefix + '.json' 
    
    run_params = params.render_json.copy()
    run_params['render']['owner'] = owner
    run_params['render']['project'] = proj_dd_sel
    
    with open(os.path.join(params.json_template_dir,'SBEMImage_importer.json'),'r') as f:
        run_params.update(json.load(f))
    
    run_params['image_directory'] = sbemdir
    run_params['stack'] = stack_sel
    
    with open(param_file,'w') as f:
        json.dump(run_params,f,indent=4)

    log_file = params.render_log_dir + '/' + 'sbem_conv-' + params.run_prefix + '.log'
    
    if os.path.isfile(log_file):
        out=log_file
    else:
        out=outfile
        
        
    #launch
    # -----------------------
    
    launch_jobs.run(target='standalone',pyscript='$rendermodules/rendermodules/dataimport/generate_EM_tilespecs_from_SBEMImage.py',
                    json=param_file,run_args=None,logfile=log_file)
    


    return True,out,params.refresh_interval



# =============================================
# PROGRESS OUTPUT


consolefile = './out.txt'
    
# f = open(consolefile, 'w')
# f.close() 
    

# code block to insert the python/slurm console output:    

outfile=os.path.abspath(consolefile)

# orig_stdout = sys.stdout
# f = open(outfile, 'a')
# sys.stdout = f
# f.close()
# CODE EXECUTION GOES HERE!!!


collapse_stdout = html.Div([
    html.Br(),
    html.Details([
                html.Summary('Console output:'),
                html.Div(id=label+"collapse",                 
                     children=[
                         dcc.Interval(id=label+'interval1', interval=10000,
                                      n_intervals=0),
                         html.Div(id=label+'div-out',children=['Log file: ',html.Div(id=label+'outfile',children=outfile,style={"font-family":"Courier New"})]),
                         dcc.Textarea(id=label+'console-out',
                                      style={'width': '100%','height':200},disabled='True')                         
                         ])
                ])
            ])



@app.callback(Output(label+'console-out','value'),
    [Input(label+'interval1', 'n_intervals'),Input(label+'outfile','children')])
def update_output(n,outfile):
    file = open(outfile, 'r')
    data=''
    lines = file.readlines()
    if lines.__len__()<=params.disp_lines:
        last_lines=lines
    else:
        last_lines = lines[-params.disp_lines:]
    for line in last_lines:
        data=data+line
    file.close()    
    
        
    return data





# ---- page layout

page = html.Div([directory_sel, project_dd, stack_div, gobutton, collapse_stdout])