#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 14:52:17 2021

@author: schorb
"""


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL

import requests
import json

from app import app

import params




# Update init parameters from previous module


def init_update_store(thismodule,prevmodule,comp_in='store_render_launch',comp_out='store_init_render'):
    
    dash_out = Output({'component': comp_out, 'module': thismodule},'data')
    dash_in =  Input({'component': comp_in, 'module': prevmodule},'data')
    dash_state = State({'component': 'store_init_render', 'module': thismodule},'data'),
                   
    return dash_out,dash_in,dash_state

def update_store(prevstore,thisstore): 
    for key in thisstore.keys():        
        if not prevstore[key] == '' or prevstore[key] == None:
            thisstore[key] = prevstore[key]
    
    return thisstore



# Update owner dropdown:
 

@app.callback([Output({'component': 'owner_dd', 'module': MATCH},'options'),
                Output({'component': 'owner_dd', 'module': MATCH},'value')
                ],
              Input({'component': 'store_init_render', 'module': MATCH},'data')
              )
def update_owner_dd(init_in):
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
              State({'component': 'store_project', 'module': MATCH},'data'),
              prevent_initial_call=True)
def update_proj_dd(owner_sel,init_store,store_proj):
    ctx = dash.callback_context
    trigger = json.loads(ctx.triggered[0]['prop_id'].partition('.value')[0])
    
    href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+owner_sel
    
    # get list of projects on render server
    url = params.render_base_url + params.render_version + 'owner/' + owner_sel + '/projects'
    projects = requests.get(url).json()
    
    out_project=projects[0]
    

    # assemble dropdown
    dd_options = list(dict())
    for item in projects:
        if item == store_proj:out_project=item
        dd_options.append({'label':item, 'value':item})  
        
    if 'store_init_render' in trigger['component']:
       out_project=init_store['project']
       
       
    return href_out, dd_options, out_project



# Update stack dropdown, render store and browse link


@app.callback([Output({'component': 'browse_stack', 'module': MATCH},'href'),
                Output({'component': 'stack_dd', 'module': MATCH},'options'),
                Output({'component': 'stack_dd', 'module': MATCH},'value'),
                Output({'component': 'store_allstacks', 'module': MATCH},'data')],
              [Input({'component': 'store_init_render', 'module': MATCH},'data'),
                Input({'component': 'owner_dd', 'module': MATCH}, 'value'),
                Input({'component': 'project_dd', 'module': MATCH}, 'value')],
              State({'component': 'store_stack', 'module': MATCH},'data')
              )
def update_stack_store(init_store,own_sel,proj_sel,store_stack):
    ctx = dash.callback_context
    trigger = json.loads(ctx.triggered[0]['prop_id'].partition('.value')[0])
    
    
          
    if not (proj_sel in [None,'']):
        href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+own_sel+'&renderStackProject='+proj_sel
        # get list of projects on render server
        url = params.render_base_url + params.render_version + 'owner/' + own_sel + '/project/' + proj_sel + '/stacks'
        
        stacks = requests.get(url).json()
        
        out_stack=stacks[0]['stackId']['stack']        

        # assemble dropdown
        dd_options = list(dict())
        for item in stacks:

            if item['stackId']['stack'] == store_stack:out_stack=item['stackId']['stack']
            
            dd_options.append({'label':item['stackId']['stack'], 'value':item['stackId']['stack']})
            
            
        if 'store_init_render' in trigger['component']:
            out_stack=init_store['stack']
        
        return href_out, dd_options, out_stack, stacks
        
    else: 
        return [dash.no_update] * 4

