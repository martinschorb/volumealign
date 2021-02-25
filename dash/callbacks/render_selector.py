#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 14:52:17 2021

@author: schorb
"""


import dash

from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

import requests


from app import app

import params
from utils import helper_functions as hf



# Update init parameters from previous module


def init_update_store(thismodule,prevmodule,comp_in='store_render_launch',comp_out='store_init_render'):

    dash_out = Output({'component': comp_out, 'module': thismodule},'data')
    dash_in =  Input({'component': comp_in, 'module': prevmodule},'data')
    dash_state = State({'component': 'store_init_render', 'module': thismodule},'data')
                   
    return dash_out,dash_in,dash_state

def update_store(prevstore,thisstore):
    if not dash.callback_context.triggered: 
        raise PreventUpdate  
    
    # print(thisstore,prevstore)
    # for key in thisstore.keys():
        # if not (not key in prevstore.keys() or prevstore[key] == '' or prevstore[key] == None):                  
        #     thisstore[key] = prevstore[key]
    thisstore.update(prevstore)

    return thisstore



# Update owner dropdown:
 

@app.callback([Output({'component': 'owner_dd', 'module': MATCH},'options'),
                Output({'component': 'owner_dd', 'module': MATCH},'value')
                ],
              [Input({'component': 'store_init_render', 'module': MATCH},'data'),
               Input('url', 'pathname')]
              )
def update_owner_dd(init_in,thispage):
    
    thispage = thispage.lstrip('/')        
    
    if not hf.trigger_module() == thispage:
        return dash.no_update
    
    print(thispage)
        
    dd_options = list(dict())
    
    allowners = params.render_owners
    
    for item in allowners: 
        dd_options.append({'label':item, 'value':item})
    
    init_owner = init_in['owner']
    
    if init_owner == '':
        init_owner = allowners[0]
    return dd_options, init_owner




#  SELECT STACK TO WORK....
#============================================================

# Update projects dropdown and browse link

@app.callback([Output({'component': 'browse_proj', 'module': MATCH}, 'href'),
                Output({'component': 'project_dd', 'module': MATCH}, 'options'),
                Output({'component': 'project_dd', 'module': MATCH}, 'value'),
                ],
              [Input({'component': 'owner_dd', 'module': MATCH}, 'value'),
               Input({'component': 'store_init_render', 'module': MATCH},'data')],
              [State({'component': 'store_project', 'module': MATCH},'data'),
               State('url', 'pathname')],
              prevent_initial_call=True)
def update_proj_dd(owner_sel,init_store,store_proj,thispage):
    
    if not dash.callback_context.triggered: 
        raise PreventUpdate
    
    thispage = thispage.lstrip('/')        
    
    if not hf.trigger_module() == thispage:
        return dash.no_update
          
    trigger = hf.trigger_component()    
    
    out_project = ''
    
    href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+owner_sel
    
    # get list of projects on render server
    url = params.render_base_url + params.render_version + 'owner/' + owner_sel + '/projects'
    projects = requests.get(url).json()

    # assemble dropdown
    dd_options = list(dict())
    for item in projects:
        if item == store_proj:out_project=item
        dd_options.append({'label':item, 'value':item})  
        
    if 'store_init_render' in trigger:
       out_project=init_store['project']
      
    if out_project == '':
        out_project=projects[0]
        
    return href_out, dd_options, out_project



# Update stack dropdown and browse link


@app.callback([Output({'component': 'browse_stack', 'module': MATCH},'href'),
                Output({'component': 'stack_dd', 'module': MATCH},'options'),
                Output({'component': 'stack_dd', 'module': MATCH},'value'),
                Output({'component': 'store_allstacks', 'module': MATCH},'data')],
              [Input({'component': 'store_init_render', 'module': MATCH},'data'),
                Input({'component': 'owner_dd', 'module': MATCH}, 'value'),
                Input({'component': 'project_dd', 'module': MATCH}, 'value')],
              [State({'component': 'store_stack', 'module': MATCH},'data'),
               State('url', 'pathname')]
              )
def update_stack_dd(init_store,own_sel,proj_sel,store_stack,thispage):
    
    if not dash.callback_context.triggered: 
        raise PreventUpdate
    
    thispage = thispage.lstrip('/')        
    
    if not hf.trigger_module() == thispage:
        return dash.no_update
        
    trigger = hf.trigger_component()        
    
          
    if not (proj_sel in [None,'']):
        href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+own_sel+'&renderStackProject='+proj_sel
        # get list of projects on render server
        url = params.render_base_url + params.render_version + 'owner/' + own_sel + '/project/' + proj_sel + '/stacks'
        
        stacks = requests.get(url).json()        
        out_stack = ''
        
        # assemble dropdown
        dd_options = list(dict())
        for item in stacks:

            if item['stackId']['stack'] == init_store['stack']:out_stack=item['stackId']['stack']
            
            dd_options.append({'label':item['stackId']['stack'], 'value':item['stackId']['stack']})
            
            
        if 'store_init_render' in trigger:
            out_stack=init_store['stack']
            
        if out_stack == '':
            out_stack=stacks[0]['stackId']['stack']        

        
        return href_out, dd_options, out_stack, stacks
    
        
        
    else: 
        return [dash.no_update] * 4


# Update render store fields:
 

@app.callback([Output({'component': 'store_owner', 'module': MATCH},'data'),
               Output({'component': 'store_project', 'module': MATCH},'data'),
                ],
              Input({'component': 'project_dd', 'module': MATCH}, 'value'),
              State({'component': 'owner_dd', 'module': MATCH}, 'value'),
               )
def update_render_store(proj_sel,own_sel):
    if not dash.callback_context.triggered: 
        raise PreventUpdate
        
    return own_sel,proj_sel#,stack_sel