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


from app import app

import params




# Update init parameters from previous module


def init_update_store(thismodule,prevmodule,comp_in='store_render',comp_out='store_init_render'):
    
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
    
    allowners = init_in['allowners']
    
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
              Input({'component': 'owner_dd', 'module': MATCH}, 'value'),
              State({'component': 'store_render', 'module': MATCH},'data'),
              prevent_initial_call=True)
def update_proj_dd(owner_sel,thisstore):    
    href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+owner_sel
    
    # get list of projects on render server
    url = params.render_base_url + params.render_version + 'owner/' + owner_sel + '/projects'
    projects = requests.get(url).json()
    
    out_project=projects[0]

    # assemble dropdown
    dd_options = list(dict())
    for item in projects:
        if item == thisstore['project']:out_project=item
        dd_options.append({'label':item, 'value':item})  

    return href_out, dd_options, out_project



# Update stack dropdown and browse link


@app.callback([Output({'component': 'browse_stack', 'module': MATCH},'href'),
                Output({'component': 'stack_dd', 'module': MATCH},'options'),
                Output({'component': 'stack_dd', 'module': MATCH},'value')],
              Input({'component': 'project_dd', 'module': MATCH}, 'value'),
              State({'component': 'store_render', 'module': MATCH},'data'))
def update_stack_dd(proj_sel,thisstore):

    if not (proj_sel is None or '' in [thisstore['owner'],thisstore['project']]):
        href_out=params.render_base_url+'view/stacks.html?renderStackOwner='+thisstore['owner']+'&renderStackProject='+proj_sel
        # get list of projects on render server
        url = params.render_base_url + params.render_version + 'owner/' + thisstore['owner'] + '/project/' + proj_sel + '/stacks'
        
        stacks = requests.get(url).json()
        
        out_stack=stacks[0]['stackId']['stack']        

        # assemble dropdown
        dd_options = list(dict())
        for item in stacks:

            if item['stackId']['stack'] == thisstore['stack']:out_stack=item['stackId']['stack']
            
            dd_options.append({'label':item['stackId']['stack'], 'value':item['stackId']['stack']})
        
        return href_out, dd_options, out_stack
        
    else: 
        return [dash.no_update] * 3





# Update render store


@app.callback(Output({'component': 'store_render', 'module': MATCH},'data'),                
              [Input({'component': 'store_init_render', 'module': MATCH},'data'),
               Input({'component': 'owner_dd', 'module': MATCH}, 'value'),
               Input({'component': 'project_dd', 'module': MATCH}, 'value'),
               Input({'component': 'stack_dd', 'module': MATCH}, 'value')],
              State({'component': 'store_render', 'module': MATCH},'data'))
def update_render_store(init_store,own_sel,proj_sel,stacksel,thisstore):
    outstore = thisstore.copy()
    
    for key in init_store.keys():
        if not init_store[key] == '' or init_store[key] == None:
            outstore[key] = init_store[key]
        
    dd=['owner','project','stack']
    sel=[own_sel,proj_sel,stacksel]
    for idx in range(len(sel)):
        outstore[dd[idx]] = sel[idx]
        
    return outstore