#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 08:42:12 2020

@author: schorb
"""
import dash_core_components as dcc
import dash_html_components as html
import subprocess
import sys
import os
from dash.dependencies import Input,Output,State
import json
import requests
import importlib


from app import app
import params


# SELECT input directory

# get user name and main group to pre-polulate input directory

p=subprocess.Popen('id -gn',stdout=subprocess.PIPE,shell=True)
group = p.communicate()[0].decode(encoding='utf8').strip("\n")

directory_sel = html.Div(children=[html.H4("Select dataset root directory:"),
                          dcc.Input(id="conv_input1", type="text", debounce=True,placeholder="/g/"+group,persistence=True),
                          html.Button('Browse',id="conv_browse1"),' graphical browsing works on cluster login node ONLY!',
                          html.Div(id='warning-popup')])

# ============================
# set up render parameters

owner = "SBEM"
#------------------
# SET PROJECT

# get list of projects on render server
url = params.render_base_url + params.render_version + 'owner/' + owner + '/projects'
projects = requests.get(url).json()

orig_projdiv=html.Div(id='orig_proj',style={'display':'none'},children=projects)


# assemble dropdown
dd_options = [{'label':'Create new Project', 'value':'newproj'}]
for item in projects: 
    dd_options.append({'label':item, 'value':item})


project_dd = html.Div([html.H4("Select Render Project:"),
                       dcc.Dropdown(id='sbem_conv_project_dd',persistence=True,
                                    options=dd_options,clearable=False,value=projects[0]),
                       html.Br(),
                       html.Div(id='render_project',style={'display':'none'}),                               
                       html.Div([html.Br(),html.A('Browse Project',href=params.render_base_url+'view/stacks.html?renderStackOwner='+owner,
                                id='sbem_conv_browse_proj',target="_blank")]),
                       orig_projdiv
                       ])

                       
#dropdown callback
@app.callback([Output('sbem_conv_browse_proj','href'),
               Output('render_project','children'),
               Output('render_project','style')],
    Input('sbem_conv_project_dd', 'value'))
def proj_dd_sel(project_sel):     
    if project_sel=='newproj':       
        href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+owner+'&renderStackProject='+project_sel
        divstyle = {'display':'block'}                       
        div_out = ['Enter new project name: ',
                   dcc.Input(id="conv_proj_input", type="text", debounce=True,placeholder="new_project",persistence=False)
                   ]
    else:
        div_out = project_sel
        divstyle = {'display':'none'}
        href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+owner+'&renderStackProject='+project_sel
    return [href_out,div_out,divstyle]

# Create a new Project

@app.callback([Output('sbem_conv_project_dd', 'options'),Output('sbem_conv_project_dd', 'value')],
              [Input('conv_proj_input', 'value')],
              State('sbem_conv_project_dd', 'options'),)
def new_proj(project_name,dd_options): 
    dd_options.append({'label':project_name, 'value':project_name})
    return dd_options,project_name

#------------------
# SET STACK


stack_div = html.Div(id='sbem_conv_stack_div',children=[html.H4("Select Render Stack:"),
                                    dcc.Dropdown(id='sbem_conv_stack_dd',persistence=True,
                                    options=dd_options,clearable=False,style={'display':'none'}),
                                                         html.Div(id='stack_state',style={'display':'none'},children=''),
                                                         html.Br(),
                                                         html.Div(id='newstack'),                                                          
                                                         html.A('Browse Stack',href=params.render_base_url+'view/stacks.html?renderStackOwner='+owner,
                                id='sbem_conv_browse_stack',target="_blank"),
                                 html.Br(),]
                       )


@app.callback([Output('sbem_conv_stack_dd','options'),   
               Output('sbem_conv_stack_dd','style'), 
               Output('stack_state','children')],
    [Input('sbem_conv_project_dd', 'value'),
     Input('orig_proj','children')],
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
    
    
            
@app.callback(Output('stack_state','children'),
    Input('sbem_conv_stack_dd','value'))
def update_stack_state(stack_dd):        
    return stack_dd

    
@app.callback([Output('sbem_conv_browse_stack','href'),Output('sbem_conv_browse_stack','style')],
    Input('stack_state','children'),
    State('sbem_conv_project_dd', 'value'))
def update_stack_browse(stack_state,project_sel):      
    if stack_state == 'newstack':
        return params.render_base_url, {'display':'none'}
    else:
        return params.render_base_url+'view/stack-details.html?renderStackOwner='+owner+'&renderStackProject='+project_sel+'&renderStack='+stack_state, {'display':'block'}
                                
    
@app.callback(Output('newstack','children'),
    Input('stack_state','children'))
def new_stack_input(stack_value):
    if stack_value=='newstack':
        st_div_out = ['Enter new stack name: ',
                   dcc.Input(id="conv_stack_input", type="text", debounce=True,placeholder="new_stack",persistence=False)
                   ]
    else:
        st_div_out = ''
    
    return st_div_out



@app.callback([Output('sbem_conv_stack_dd', 'options'),Output('sbem_conv_stack_dd', 'value'),Output('sbem_conv_stack_dd','style')],
              [Input('conv_stack_input', 'value')],
              State('sbem_conv_stack_dd', 'options'),)
def new_stack(project_name,dd_options): 
    dd_options.append({'label':project_name, 'value':project_name})
    return dd_options,project_name,{'display':'block'}

 
# =============================================
# Start Button

gobutton = html.Div([html.Br(),
                     html.Button('Start conversion',id="conv_go",disabled=True),                     
            
    
            ])

@app.callback(Output('conv_go', 'disabled'),
              Input('stack_state', 'children'),
              State('sbem_conv_project_dd', 'value'))
def activate_gobutton(stack_state1,proj_dd_sel1):    
   
    if any([stack_state1=='newstack', proj_dd_sel1=='newproj']):
        return True
    else:
        return False
 


@app.callback(Output('conv_go', 'disabled'),
              Input('conv_go', 'n_clicks'),
              [State('sbem_conv_project_dd', 'value'),
               State('stack_state','children'),
               
              ])
                  
def execute_gobutton(stack_state1,proj_dd_sel1):    
    #prepare parameters:
    importlib.reload(params)
        
    param_file = params.json_run_dir + '/' + 'sbem_conv-' + params.run_prefix + '.json' 
    
    run_params = dict()
    run_params['render'] = params.render_json
    
    





# =============================================
# PROGRESS OUTPUT


consolefile = './out.txt'
    
f = open(consolefile, 'w')
f.close() 
    

# code block to insert the python/slurm console output:    

outfile=os.path.abspath(consolefile)
label = "-sbem_convert"

orig_stdout = sys.stdout
f = open(outfile, 'a')
sys.stdout = f

# CODE EXECUTION GOES HERE!!!

# print('Intervals Passed: ' + str(n))
sys.stdout = orig_stdout
f.close()



collapse_stdout = html.Div([
    html.Br(),
    html.Details([
                html.Summary('Console output:'),
                html.Div(id="collapse"+label,                 
                     children=[
                         dcc.Interval(id='interval1'+label, interval= params.refresh_interval,
                                      n_intervals=0),
                         html.Div(id='div-out'+label,children='Console output logged into: '+outfile),
                         dcc.Textarea(id='console-out'+label,
                                      style={'width': '100%','height':200},disabled='True'),
                         html.Div(id='outfile'+label,children=outfile,style={'display':'none'})
                         ])
                ])
            ])


@app.callback(Output('div-out'+label,'children'),
    [Input('interval1'+label, 'n_intervals'),Input('outfile'+label,'children')])
def update_interval(n,outfile):    
    return 'Console output logged into: '+outfile

@app.callback(Output('console-out'+label,'value'),
    [Input('interval1'+label, 'n_intervals'),Input('outfile'+label,'children')])
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