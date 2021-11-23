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
                       Output({'component':imtype+'_section_in'+idx_str,'module': MATCH},'max'),
                       Output({'component':imtype+'section_in'+idx_str,'module': MATCH},'style'),
                       Output({'component':imtype+'_contrastslider'+idx_str, 'module': MATCH},'max'),
                       Output({'component':imtype+'_contrastslider'+idx_str, 'module': MATCH},'value')],
                      Input({'component': 'stack_dd','module': MATCH},'value'),
                      [State({'component': 'store_allstacks', 'module': MATCH}, 'data'),
                       State({'component': 'owner_dd','module': MATCH},'value'),
                       State({'component': 'project_dd','module': MATCH},'value')])
        def stacktoslice(stack_sel,allstacks,owner,project):
            stacklist=[]            
            slicestyle = {}
            
            if (not stack_sel=='-' ) and (not allstacks is None):   
                 stacklist = [stack for stack in allstacks if stack['stackId']['stack'] == stack_sel]        
                 # stack = stack_sel          
            
            
            if not stacklist == []:
                stackparams = stacklist[0]
                                               
                if 'None' in (stackparams['stackId']['owner'],stackparams['stackId']['project']):
                    return dash.no_update
                
                                
                o_min = stackparams['stats']['stackBounds']['minZ']
                o_max = stackparams['stats']['stackBounds']['maxZ']
                
                if o_min == o_max: slicestyle = {'display':'none'}
                
                o_val = int((o_max-o_min)/2) + o_min 
                
                
                url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack_sel
                url1 = url + '/tileIds'
                
                tile = requests.get(url1).json()[0]
                
                url2 = url +'/tile/' + tile                 
                url2 +=  '/render-parameters'

                
                tilespec = requests.get(url2).json()
                                
                max_int = tilespec['tileSpecs'][0]['maxIntensity']     
            
                return o_val,o_min,o_max,slicestyle,max_int,[0,max_int]
            
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
        
        if 'None' in (owner,project,stack):
            return dash.no_update        
        
        url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack
        url += '/tileIds?matchPattern='
        
        if owner in params.slicenumformat.keys():            
            url += params.slicenumformat[owner] %slicenum
        
        tiles = requests.get(url).json()
        
        if tiles == []:
            return dash.no_update        
        
        t_labels = tiles.copy()
        tile = tiles[int(len(tiles)/2)]
        
        if prev_tile is None:
            prev_tile = tile
        
        if owner in params.tile_display.keys():
            t_labels, tile = params.tile_display[owner](tiles,prev_tile,slicenum)
        
        if None in (t_labels,tile):
            return dash.no_update
        
        # assemble dropdown
        dd_options = list(dict())
        for t_idx,item in enumerate(tiles):
            dd_options.append({'label':t_labels[t_idx], 'value':item})        
   
        return dd_options, tile
    
    
    @app.callback([Output({'component': 'tileim_imurl'+idx_str, 'module': MATCH},'children'),
                   Output({'component': 'tileim_link'+idx_str, 'module': MATCH},'children')],
                  [Input({'component':'tile_dd'+idx_str,'module': MATCH},'value'),
                   Input({'component': 'store_render_launch', 'module': MATCH},'data')],
                  [State({'component': 'owner_dd','module': MATCH},'value'),
                   State({'component': 'project_dd','module': MATCH},'value'),
                   State({'component': 'stack_dd','module': MATCH},'value'),
                   State('url', 'pathname')
                   ])           
    def im_view_url(tile,runstore,owner,project,stack,thispage):        
        if not dash.callback_context.triggered: 
            raise PreventUpdate
        # print('tile is now: '+ tile)
        
        thispage = thispage.lstrip('/')        
                
        if not hf.trigger(key='module') == thispage:
            return dash.no_update
            
        if None in (tile,runstore,owner,project,stack):
            return dash.no_update
        
        if 'None' in (owner,project,stack):
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
    
    
    # init image display
    @app.callback(Output({'component': 'tileim_image'+idx_str, 'module': MATCH},'src'),
                  [Input({'component': 'tileim_contrastslider'+idx_str, 'module': MATCH},'value'),
                   Input({'component': 'tileim_imurl'+idx_str, 'module': MATCH},'children')]
                  )
    def im_view(c_limits,imurl):
        if not dash.callback_context.triggered: 
            raise PreventUpdate     
            
        if None in (c_limits,imurl):
            return dash.no_update
        
        if 'None' in (c_limits,imurl):
            return dash.no_update
        
        imurl += '&minIntensity=' + str(c_limits[0]) + '&maxIntensity=' + str(c_limits[1])
        
        return imurl
    

    # init image display
    @app.callback(Output({'component': 'sliceim_image'+idx_str, 'module': MATCH},'src'),
                  [Input({'component':'sliceim_section_in'+idx_str,'module': MATCH},'value'),
                   Input({'component': 'store_render_launch', 'module': MATCH},'data'),
                   Input({'component': 'sliceim_contrastslider'+idx_str, 'module': MATCH},'value')],
                  [State({'component': 'owner_dd','module': MATCH},'value'),
                   State({'component': 'project_dd','module': MATCH},'value'),
                   State({'component': 'stack_dd','module': MATCH},'value'),
                   State('url', 'pathname')
                   ])           
    def slice_view(section,runstore,c_limits,owner,project,stack,thispage):
        if not dash.callback_context.triggered: 
            raise PreventUpdate
        
        thispage = thispage.lstrip('/')        
        
        if not hf.trigger(key='module') == thispage:
            return dash.no_update

        if None in (section,runstore,owner,project,stack):
            return dash.no_update
        
        if 'None' in (owner,project,stack):
            return dash.no_update
        
        
        url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack
        
        url += '/z/'+ str(section)
        
        url1 = url + '/bounds'
                
        bounds = requests.get(url1).json()
        
        imwidth = bounds['maxX'] - bounds['minX']
        
        scale = float(params.im_width) / float(imwidth)
        
        out_scale = '%0.2f' %scale
        
        imurl = url +'/jpeg-image?scale=' + out_scale   
        
        imurl += '&minIntensity=' + str(c_limits[0]) + '&maxIntensity=' + str(c_limits[1])
        
        return imurl
    

