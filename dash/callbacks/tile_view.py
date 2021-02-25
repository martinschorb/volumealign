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
    for imtype in ['sliceim','tileim']:
        
        @app.callback([Output({'component':imtype+'_section_in'+idx_str,'module': MATCH},'value'),
                       Output({'component':imtype+'_section_in'+idx_str,'module': MATCH},'min'),
                       Output({'component':imtype+'_section_in'+idx_str,'module': MATCH},'max')],
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
                
                o_val = int((o_max-o_min)/2) + o_min 
            
                return o_val,o_min,o_max
            
            else:
                return dash.no_update
            
    
    
    
    
    # init tile selector
    @app.callback([Output({'component':'tile_dd'+idx_str,'module': MATCH},'options'),
                   Output({'component':'tile_dd'+idx_str,'module': MATCH},'value')],
                  Input({'component':'tileim_section_in'+idx_str,'module': MATCH},'value'),
                  [State({'component': 'owner_dd','module': MATCH},'value'),
                   State({'component': 'project_dd','module': MATCH},'value'),
                   State({'component': 'stack_dd','module': MATCH},'value'),
                   State({'component':'tile_dd'+idx_str,'module': MATCH},'value')])
    def slicetotiles(slicenum,owner,project,stack,prev_tile):

        if None in (slicenum,owner,project,stack):
            return dash.no_update
        
        url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack
        url += '/tileIds?matchPattern='
        
        if owner == 'SBEM':
            url += '.%05i' %slicenum
        
        tiles = requests.get(url).json()
        
        if tiles == []:
            return dash.no_update        
        
        t_labels = tiles.copy()
        tile = tiles[int(len(tiles)/2)]
        
        if owner == 'SBEM':
            for t_idx,t_label in enumerate(tiles): 
                t_labels[t_idx] = t_label.partition('.')[2].partition('.')[0]
                
                if (not prev_tile is None) and t_labels[t_idx] in prev_tile:
                    tile = t_label.partition('.')[0]+'.'+ t_labels[t_idx] + '.%05i' %slicenum

        # assemble dropdown
        dd_options = list(dict())
        for t_idx,item in enumerate(tiles):
            dd_options.append({'label':t_labels[t_idx], 'value':item})        
   
        return dd_options, tile
    
    
    
    
    # init image display    # update tilespec link
    @app.callback([Output({'component': 'image'+idx_str, 'module': MATCH},'src'),
                   Output({'component': 'ts_link'+idx_str, 'module': MATCH},'children')],
                  [Input({'component':'tile_dd'+idx_str,'module': MATCH},'value'),
                   Input({'component': 'store_render_launch', 'module': MATCH},'data')],
                  [State({'component': 'owner_dd','module': MATCH},'value'),
                   State({'component': 'project_dd','module': MATCH},'value'),
                   State({'component': 'stack_dd','module': MATCH},'value'),
                   State('url', 'pathname')
                   ])           
    def im_view(tile,runstore,owner,project,stack,thispage):        
        if not dash.callback_context.triggered: 
            raise PreventUpdate
        # print('tile is now: '+ tile)
        
        thispage = thispage.lstrip('/')        
                
        if not hf.trigger(key='module') == thispage:
            return dash.no_update
            
        if None in (tile,runstore,owner,project,stack):
            return dash.no_update
        
        url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack
        url += '/tile/' + tile 
        
        url1 = url + '/render-parameters'
        
        tilespec = requests.get(url1).json()
        
        scale = float(params.im_width) / float(tilespec['width'])
        
        out_scale = '%0.2f' %scale
        
        imurl = url +'/jpeg-image?scale=' + out_scale
        
        
        if runstore is None or not 'mt_params' in runstore.keys():
            scale1 = params.default_tile_scale
        else:
            scale1 = runstore['mt_params']['scale']

        
        url1 += '?filter=true&scale=' + str(scale1)
                
        return imurl, url1
    

    # init image display    # update tilespec link
    @app.callback(Output({'component': 'slice_image'+idx_str, 'module': MATCH},'src'),
                  [Input({'component':'sliceim_section_in'+idx_str,'module': MATCH},'value'),
                   Input({'component': 'store_render_launch', 'module': MATCH},'data')],
                  [State({'component': 'owner_dd','module': MATCH},'value'),
                   State({'component': 'project_dd','module': MATCH},'value'),
                   State({'component': 'stack_dd','module': MATCH},'value'),
                   State('url', 'pathname')
                   ])           
    def slice_view(section,runstore,owner,project,stack,thispage):
        if not dash.callback_context.triggered: 
            raise PreventUpdate
        
        thispage = thispage.lstrip('/')        
        
        if not hf.trigger(key='module') == thispage:
            return dash.no_update
    
        if None in (section,runstore,owner,project,stack):
            return dash.no_update
        
        url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack
        
        url += '/z/'+ str(section)
        
        url1 = url + '/bounds'
                
        bounds = requests.get(url1).json()
        
        imwidth = bounds['maxX'] - bounds['minX']
        
        scale = float(params.im_width) / float(imwidth)
        
        out_scale = '%0.2f' %scale
        
        imurl = url +'/jpeg-image?scale=' + out_scale   
        
        return imurl
    

