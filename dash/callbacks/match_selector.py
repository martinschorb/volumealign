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
import json

from app import app

import params
from utils import helper_functions as hf





# Update mc_owner dropdown:
 
@app.callback([Output({'component': 'mc_owner_dd', 'module': MATCH},'options'),
                Output({'component': 'mc_owner_dd', 'module': MATCH},'value')
                ],
              [Input({'component': 'store_init_match', 'module': MATCH},'data'), 
               Input({'component': 'mcown_input', 'module': MATCH}, 'value')],
              State({'component': 'mc_owner_dd', 'module': MATCH},'options'))
def update_mc_owner_dd(init_in, new_owner, dd_own_in):
    if not dash.callback_context.triggered: 
        trigger =  'init_match'
    else:    
        trigger = hf.trigger_component()
    
    dd_options = list()    
    if 'init_match' in trigger:
        if len(dd_own_in)>0:
            if dd_own_in[0]['value']== 'new_mc_owner':
                dd_options.extend(dd_own_in)       
    
        
        if 'all_mc_owners' in init_in.keys():
            dd_options.append(init_in['all_mc_owners'])
    
        else:
            
            url = params.render_base_url + params.render_version + 'matchCollectionOwners'    
            
            mc_owners = requests.get(url).json()
            
            for item in mc_owners: 
                dd_options.append({'label':item, 'value':item})
    
        
        if 'mc_owner' in init_in.keys():
            mc_owner = init_in['mc_owner']
        else:
            mc_owner = dd_options[0]['value']
            
    elif 'input' in trigger:
        dd_options = dd_own_in.copy()
        dd_options.append({'label':new_owner, 'value':new_owner})
        mc_owner = new_owner
                
        
    return dd_options, mc_owner
  
    
# Update match collection dropdown 
@app.callback([Output({'component':'new_mc_owner','module': MATCH},'style'),
                Output({'component':'matchcoll_dd','module': MATCH},'options'),
                Output({'component':'matchcoll_dd','module': MATCH},'value'),
                Output({'component':'matchcoll','module': MATCH},'style'),
                Output({'component':'store_all_matchcolls','module': MATCH},'data')],
              [Input({'component': 'mc_owner_dd','module': MATCH},'value'),
               Input({'component': 'mc_input', 'module': MATCH}, 'value')],
              [State({'component':'matchcoll_dd','module': MATCH},'options'),
               State({'component': 'store_init_match', 'module': MATCH},'data')]
              )
def pointmatch_mcown_dd_sel(mc_own_sel,new_mc,mc_dd_opt,init_match):
    trigger = hf.trigger_component()
    all_mcs = dash.no_update

    if 'mc_owner_dd'in trigger:
        if mc_own_sel=='new_mc_owner':       
            div1style = {}
            
            mc_dd_opt = [{'label':'new Match Collection', 'value':'new_mc'}]
            mc_dd_val = 'new_mc'
            
            mc_style = {'display':'none'}
            
        else:
            div1style = {'display':'none'} 
            
            url = params.render_base_url + params.render_version + 'owner/' + mc_own_sel + '/matchCollections'
            mcolls = requests.get(url).json()
            
            all_mcs=list()
            
            # assemble dropdown
            mc_dd_opt = [{'label':'new Match Collection', 'value':'new_mcoll'}]
            mc_dd_val = 'new_mcoll'
            
            init_mc = None
            
            if 'matchcoll' in init_match.keys():
                init_mc = init_match['mc_owner']
                
            for item in mcolls: 
                all_mcs.append(item['collectionId']['name'])
                mc_dd_opt.append({'label':item['collectionId']['name'], 'value':item['collectionId']['name']})
                if init_mc == item['collectionId']['name']:
                    mc_dd_val = init_mc
            
            mc_style = {'display':'flex'}
            
    elif 'mc_input' in trigger:
        div1style = {'display':'none'} 
        mc_dd_opt.append({'label':new_mc, 'value':new_mc})
        mc_dd_val = new_mc
        mc_style = {'display':'flex'}           
                
    return div1style, mc_dd_opt, mc_dd_val, mc_style, all_mcs


# initiate new mc input
@app.callback([Output({'component':'new_matchcoll','module': MATCH},'style'),
               Output({'component':'browse_mc_div','module': MATCH},'style'),
               Output({'component':'browse_mc','module': MATCH},'href')],
              Input({'component': 'matchcoll_dd','module': MATCH},'value'),
              [State({'component': 'mc_owner_dd','module': MATCH},'value'),
               State({'component':'store_owner','module' : MATCH},'data'),
               State({'component':'store_project','module' : MATCH},'data'),
               State({'component':'stack_dd','module' : MATCH},'value'),
               State({'component':'store_all_matchcolls','module': MATCH},'data')])
def new_matchcoll(mc_sel,mc_owner,owner,project,stack,all_mcs):
        
    if mc_sel == 'new_mcoll':
        return {'display':'flex'}, {'display':'none'}, ''
    else:
        if mc_sel in all_mcs:
            
            mc_url = params.render_base_url + 'view/point-match-explorer.html?'
            mc_url += 'matchCollection=' + mc_sel
            mc_url += '&matchOwner=' + mc_owner
            mc_url += '&renderStack=' + stack
            mc_url += '&renderStackOwner=' + owner 
            mc_url += '&renderStackProject=' + project
            mc_url += '&startZ=100'
            mc_url += '&endZ=200'
            
            return {'display':'none'}, {}, mc_url
        else:
            return {'display':'none'}, {'display':'none'}, ''



