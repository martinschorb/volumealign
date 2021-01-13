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

from utils import launch_jobs

from sift import sift_pointmatch


module='pointmatch_'


main = html.Div(children=[html.Div(id=module+'main',children=[html.H4('Current active stack:'),
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
                                             ],style=dict(display='flex')),
                                             html.H4("Select Match Collection:"),
                                             html.Div([html.Div('Match Collection Owner:',style={'margin-right': '1em','margin-left': '2em'}),
                                                       dcc.Dropdown(id=module+'mc_owner_dd',persistence=True,clearable=False,className='dropdown_inline'),
                                                       html.Div(id=module+'new_mc_owner',style={'display':'none'}),
                                                       html.Br(),
                                                       html.Div([html.Div('Match Collection:',style={'margin-right': '1em','margin-left': '2em'}),
                                                                 dcc.Dropdown(id=module+'matchcoll_dd',persistence=True,
                                                                              clearable=False,className='dropdown_inline'),
                                                                 html.Br()],
                                                                id=module+'matchcoll',style={'display':'none'}),
                                                       html.Div(id=module+'new_matchcoll',style={'display':'none'}),
                                                       html.Br()
                                                       ],style=dict(display='flex'))
                                             ]),
                          
                          
                          
                          
                          html.H4("Choose type of PointMatch determination:",id='conv_head'),dcc.Dropdown(
                              id=module+'dropdown1',persistence=True,
                              options=[{'label': 'SIFT', 'value': 'SIFT'}],
                              value='SIFT'),                          
                          html.Div([html.H4("Select Tilepair source directory:"),
                           dcc.Dropdown(id=module+'tp_dd',persistence=True,
                                        clearable=False),
                           html.Br(),
                           html.Div(id=module+'tp_prefix',style={'display':'none'})                              
                           ])

                            ])


intervals = html.Div([dcc.Interval(id=module+'interval1', interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Interval(id=module+'interval2', interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Store(id=module+'tmpstore'),
                      dcc.Store(id=module+'stack')
                      ])

page1 = html.Div(id=module+'page1')

# # ===============================================

@app.callback([Output(module+'owner_dd','options'),
               Output(module+'owner_dd','value'),
               Output(module+'mc_owner_dd','options'),
               Output(module+'mc_owner_dd','value'),
               Output(module+'store','data')],
              Input(module+'page1','children'),
              State(module+'store','data'))
def pointmatch_init_page(page,storage):

    url = params.render_base_url + params.render_version + 'owners'
    owners = requests.get(url).json()
    
        # assemble dropdown
    owner_dd_options = list(dict())
    for item in owners: 
        owner_dd_options.append({'label':item, 'value':item})
    
    storage['all_owners']=owners     
    
    
    url = params.render_base_url + params.render_version + 'matchCollectionOwners'
    mc_owners = requests.get(url).json()
    
        # assemble dropdown
    mc_owner_dd_options = list(dict())
    mc_owner_dd_options.append({'label':'new Match Collection Owner', 'value':'new_mc_owner'})
    
    for item in mc_owners: 
        mc_owner_dd_options.append({'label':item, 'value':item})
    
    storage['all_mc_owners']=mc_owners
    
    return owner_dd_options,owners[0],mc_owner_dd_options,mc_owners[0], storage
    


@app.callback([Output(module+'owner_dd','options'),
                Output(module+'store','data'),               
                Output(module+'owner_dd','value'),
                Output(module+'project_dd','value'),
                Output(module+'stack_dd','value')
                ],
              [Input('tilepairs_'+'store','data'),
                Input('url', 'pathname')],
              [State(module+'store','data')])
def pointmatch_update_stack_state(prevstore,page,thisstore):  
    
    if 'all_owners' in thisstore.keys():
        
        for key in ['owner','project','stack','tilepairdir']: 
            if key in prevstore.keys() and not prevstore[key]=='-':
                # print(key)
                # print(prevstore[key])
                
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
def pointmatch_own_dd_sel(owner_sel,thisstore):
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
def pointmatch_proj_dd_sel(proj_sel,thisstore): 
        
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




@app.callback([Output(module+'tp_dd','options'),
               Output(module+'tp_dd','value')],
              Input(module+'stack_dd','value'))
def pointmatch_tp_dd_fill(stack):
   
    tp_dirlist = [d_item for d_item in glob.glob(params.json_run_dir+'/tilepairs_'+params.user+'*'+stack+'*') if os.path.isdir(d_item)]
    tpdir_dd_options=list(dict())
    
    
    if tp_dirlist == []:
        tpdir_dd_options.append({'label':'no tilepairs found for selected stack', 'value': ''})
    else:
        for tp_dir in tp_dirlist:
            tpdir_dd_options.append({'label':os.path.basename(tp_dir), 'value':tp_dir})
    
    

    return tpdir_dd_options,tpdir_dd_options[-1]['value']


# =========================================


                       
# #dropdown callback
@app.callback([Output(module+'new_mc_owner','children'),
                Output(module+'new_mc_owner','style'),
                Output(module+'matchcoll_dd', 'options'),
                Output(module+'matchcoll_dd', 'value'),
                Output(module+'matchcoll','style'),
                Output(module+'store','data')],
              Input(module+'mc_owner_dd', 'value'),
              State(module+'store','data'))
def pointmatch_mcown_dd_sel(mc_own_sel,storage):     
    if mc_own_sel=='new_mc_owner':       
        div1style = {}                       
        div1_out = [html.Div('Enter new Match Collection Owner:',style={'margin-right': '1em','margin-left': '2em'}),
                    dcc.Input(id=module+"mcown_input", type="text",
                              style={'margin-right': '1em','margin-left': '3em'},
                              debounce=True,placeholder="new_mc_owner",persistence=False)
                    ]
        
        mc_dd_opt = [{'label':'new Match Collection', 'value':'new_mc'}]
        mc_dd_val = 'new_mc'
        
        mc_style = {'display':'none'}
        
    else:
        div1_out = '' 
        div1style = {'display':'none'} 
        
        url = params.render_base_url + params.render_version + 'owner/' + mc_own_sel + '/matchCollections'
        mcolls = requests.get(url).json()
    
        # assemble dropdown
        mc_dd_opt = [{'label':'new Match Collection', 'value':'new_mcoll'}]
    
        for item in mcolls: 
            mc_dd_opt.append({'label':item['collectionId']['name'], 'value':item['collectionId']['name']})
        
        storage['all_mcolls']=mcolls            
        mc_dd_val = 'new_mcoll'
        
        mc_style = {'display':'flex'}
        
        
    return div1_out, div1style, mc_dd_opt, mc_dd_val, mc_style, storage



# Create a new MC owner

@app.callback([Output(module+'mc_owner_dd', 'options'),
               Output(module+'mc_owner_dd', 'value')],
              [Input(module+'mcown_input', 'value')],
              State(module+'mc_owner_dd', 'options'))
def pointmatch_new_mcown(new_owner,dd_options): 
    dd_options.append({'label':new_owner, 'value':new_owner})
    return dd_options,new_owner

#------------------
# SET STACK




# @app.callback([Output(module+'stack_dd','options'),   
#                Output(module+'stack_dd','style'), 
#                Output(module+'stack_state','children')],
#     [Input(module+'project_dd', 'value'),
#      Input(module+'orig_proj','children')],
#     )
# def pointmatch_proj_stack_activate(project_sel,orig_proj):    
    
#     dd_options = [{'label':'Create new Stack', 'value':'newstack'}]
    
#     if project_sel in orig_proj:
#         # get list of STACKS on render server
#         url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project_sel + '/stacks'
#         stacks = requests.get(url).json()  
        
#         # assemble dropdown
        
#         for item in stacks: dd_options.append({'label':item['stackId']['stack'], 'value':item['stackId']['stack']})
                
#         return dd_options, {'display':'block'}, stacks[0]['stackId']['stack']
        
#     else:    
#         return dd_options,{'display':'none'}, 'newstack'
    
    
            
# @app.callback(Output(module+'stack_state','children'),
#     Input(module+'stack_dd','value'))
# def pointmatch_update_stack_state(stack_dd):        
#     return stack_dd


# @app.callback(Output(parent+'store','data'),
#     [Input(module+'stack_state','children'),
#     Input(module+'project_dd', 'value')],
#     [State(parent+'store','data')]
#     )
# def pointmatch_update_active_project(stack,project,storage):
#     storage['owner']=owner
#     storage['project']=project
#     storage['stack']=stack    
#     # print('sbem -> store')
#     # print(storage)
#     return storage


    
# @app.callback([Output(module+'browse_stack','href'),Output(module+'browse_stack','style')],
#     Input(module+'stack_state','children'),
#     State(module+'project_dd', 'value'))
# def pointmatch_update_stack_browse(stack_state,project_sel):      
#     if stack_state == 'newstack':
#         return params.render_base_url, {'display':'none'}
#     else:
#         return params.render_base_url+'view/stack-details.html?renderStackOwner='+owner+'&renderStackProject='+project_sel+'&renderStack='+stack_state, {'display':'block'}
                                
    
# @app.callback(Output(module+'newstack','children'),
#     Input(module+'stack_state','children'))
# def pointmatch_new_stack_input(stack_value):
#     if stack_value=='newstack':
#         st_div_out = ['Enter new stack name: ',
#                    dcc.Input(id=module+"stack_input", type="text", debounce=True,placeholder="new_stack",persistence=False)
#                    ]
#     else:
#         st_div_out = ''
    
#     return st_div_out



# @app.callback([Output(module+'stack_dd', 'options'),
#                Output(module+'stack_dd', 'value'),
#                Output(module+'stack_dd','style')],
#               [Input(module+'stack_input', 'value')],
#               State(module+'stack_dd', 'options'))
# def pointmatch_new_stack(stack_name,dd_options): 
#     dd_options.append({'label':stack_name, 'value':stack_name})
#     return dd_options,stack_name,{'display':'block'}

 







# =============================================
# # Page content

@app.callback([Output(module+'page1', 'children'),
                Output(module+'store','data')],
                Input(module+'dropdown1', 'value'),
                State(module+'store','data'))
def pointmatch_output(value,thisstore):
    if value=='SIFT':
        return sift_pointmatch.page, thisstore
    
    else:
        return [html.Br(),'No method type selected.'],thisstore





# =============================================
# Processing status



@app.callback([Output(module+'interval2','interval'),
               Output(module+'store','data'),
               Output(module+'stack','data')],
              Input(module+'interval2','n_intervals'),
              State(module+'store','data'))
def pointmatch_update_status(n,storage):  
    if n>0:        
        status = storage['run_state']
        procs=params.processes[module.strip('_')]
        if procs==[]:
            if storage['run_state'] not in ['input','wait']:
                storage['run_state'] = 'input'               
        
        if (type(procs) is subprocess.Popen or len(procs)>0): 
            status = launch_jobs.status(procs)   
            storage['run_state'] = status    

        if 'Error' in status:
            if storage['log_file'].endswith('.log'):
                storage['log_file'] = storage['log_file'][:storage['log_file'].rfind('.log')]+'.err'
            
    return params.idle_interval,storage,storage['stack']
    

cancelbutton = html.Button('cancel cluster job(s)',id=module+"cancel")


@app.callback([Output(module+'get-status','children'),
              Output(module+'get-status','style'),
              Output(module+'interval1', 'interval')],
              Input(module+'store','data'))
def pointmatch_get_status(storage):
    status_style = {"font-family":"Courier New",'color':'#000'} 
    log_refresh = params.idle_interval
    procs=params.processes[module.strip('_')]    
    if storage['run_state'] == 'running':        
        if procs == []:
            status = 'not running'
        else:
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
    
    
    return status,status_style,log_refresh



@app.callback([Output(module+'get-status','children'),
               Output(module+'store','data')],
              Input(module+'cancel', 'n_clicks'),
              State(module+'store','data'))
def pointmatch_cancel_jobs(click,storage):

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
def pointmatch_update_output(n,outfile):
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
def pointmatch_update_outfile(update,data):           
    return data['log_file']



# Full page layout:
    
page = [intervals,page1]#, page2, gobutton]
page.append(collapse_stdout)