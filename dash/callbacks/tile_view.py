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


for idx in range(params.max_tileviews):
    idx_str = '_'+str(idx)
            
    
    # init slice selector
    @app.callback([Output({'component':'tileim_section_in'+idx_str,'module': MATCH},'value'),
                   Output({'component':'tileim_section_in'+idx_str,'module': MATCH},'min'),
                   Output({'component':'tileim_section_in'+idx_str,'module': MATCH},'max')],
                  Input({'component': 'stack_dd','module': MATCH},'value'),
                  State({'component': 'store_allstacks', 'module': MATCH}, 'data'))
    def stacktoslice(stack_sel,allstacks):
        stacklist=[]
        if (not stack_sel=='-' ) and (not allstacks is None):   
             stacklist = [stack for stack in allstacks if stack['stackId']['stack'] == stack_sel]        
             # stack = stack_sel
        
        if not stacklist == []:
            stackparams = stacklist[0]        
            o_min = stackparams['stats']['stackBounds']['minZ']
            o_max = stackparams['stats']['stackBounds']['maxZ']
            
            o_val = int((o_max-o_min)/2)  
        
        return o_val,o_min,o_max
    
    
    
    
    # init tile selector
    @app.callback([Output({'component':'tile_dd'+idx_str,'module': MATCH},'options'),
                   Output({'component':'tile_dd'+idx_str,'module': MATCH},'value')],
                  Input({'component':'tileim_section_in'+idx_str,'module': MATCH},'value'),
                  [State({'component': 'owner_dd','module': MATCH},'value'),
                   State({'component': 'project_dd','module': MATCH},'value'),
                   State({'component': 'stack_dd','module': MATCH},'value')])
    def slicetotiles(slicenum,owner,project,stack):
        url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack
        url += '/tileIds?matchPattern='
        
        if owner == 'SBEM':
            url += '.%05i' %slicenum
        
        tiles = requests.get(url).json()
        t_labels = tiles.copy()
        if owner == 'SBEM':
            for t_idx,t_label in enumerate(tiles): t_labels[t_idx] = t_label.partition('.')[2].partition('.')[0]
        
        # assemble dropdown
        dd_options = list(dict())
        for t_idx,item in enumerate(tiles):        
            dd_options.append({'label':t_labels[t_idx], 'value':item})  
        
        tile = tiles[int(len(tiles)/2)]
        
        return dd_options, tile
    
    
    
    
    # init image display
    @app.callback(Output({'component': 'image'+idx_str, 'module': MATCH},'src'),
                  Input({'component':'tile_dd'+idx_str,'module': MATCH},'value'),
                  [State({'component': 'owner_dd','module': MATCH},'value'),
                   State({'component': 'project_dd','module': MATCH},'value'),
                   State({'component': 'stack_dd','module': MATCH},'value')])           
    def im_view(tile,owner,project,stack):
        url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack
        url += '/tile/' + tile 
        
        url1 = url + '/render-parameters'

        tilespec = requests.get(url1).json()
        
        scale = float(params.im_width) / float(tilespec['width'])
        
        out_scale = '%0.2f' %scale
        
        imurl = url +'/jpeg-image?scale='+out_scale
        
        return imurl
    


