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
import os
import json

from app import app

import params
from utils import helper_functions as hf

for idx in range(params.max_tileviews):
    idx_str = '_'+str(idx)
            
    
    # init slice selector
    for imtype in ['sliceim','tileim']:

        inputs = [Input({'component': 'stack_dd','module': MATCH},'value')]
        states = [State({'component': 'store_allstacks', 'module': MATCH}, 'data'),
                  State({'component': 'owner_dd','module': MATCH},'value'),
                  State({'component': 'project_dd','module': MATCH},'value'),
                  State({'component': imtype+'_section_in'+idx_str,'module': MATCH},'value')]

        if imtype == 'tileim':
            inputs.append(Input({'component': 'lead_tile', 'module': MATCH},'modified_timestamp'))
            inputs.append(Input({'component': 'tp_dd', 'module': MATCH}, 'value'))
            states.extend([
                State({'component': 'neighbours', 'module': MATCH}, 'children'),
                State({'component': 'lead_tile', 'module': MATCH},'data')
                ])
        else:
            inputs.extend([Input({'component': 'dummystore', 'module': MATCH}, 'modified_timestamp')]*2)
            states.extend([State({'component': 'dummystore', 'module': MATCH}, 'modified_timestamp')]*2)

        states.append(State('url', 'pathname'))

        @app.callback([Output({'component':imtype+'_section_in'+idx_str,'module': MATCH},'value'),
                       Output({'component':imtype+'_section_in'+idx_str,'module': MATCH},'min'),
                       Output({'component':imtype+'_section_in'+idx_str,'module': MATCH},'max'),
                       Output({'component':imtype+'_section_div'+idx_str,'module': MATCH},'style'),
                       Output({'component':imtype+'_contrastslider'+idx_str, 'module': MATCH},'max'),
                       Output({'component':imtype+'_contrastslider'+idx_str, 'module': MATCH},'value')],
                      inputs,
                      states,
                      prevent_initial_call=True)
        def stacktoslice(stack_sel,lead_trigger,tilepairdir,allstacks,owner,project,orig_sec,neighbours,lead_tile,thispage):
            stacklist=[]            
            slicestyle = {}

            thispage = thispage.lstrip('/')

            if thispage=='' or not thispage in hf.trigger(key='module'):
                raise PreventUpdate

            trigger = hf.trigger()

            ol = dash.callback_context.outputs_list

            tileim_idx = ol[0]['id']['component'].split('_')[-1]

            if (not stack_sel=='-' ) and (not allstacks is None):   
                 stacklist = [stack for stack in allstacks if stack['stackId']['stack'] == stack_sel]        
                 # stack = stack_sel          

            if not stacklist == []:
                stackparams = stacklist[0]
                                               
                if 'None' in (stackparams['stackId']['owner'],stackparams['stackId']['project']):
                    raise PreventUpdate

                if not 'stats' in stackparams.keys():
                    raise PreventUpdate

                o_min = stackparams['stats']['stackBounds']['minZ']
                o_max = stackparams['stats']['stackBounds']['maxZ']

                if orig_sec < o_min : orig_sec = o_min
                if orig_sec > o_max : orig_sec = o_max

                if neighbours == 'True' and tileim_idx != '0' and tilepairdir not in ('', None) and lead_tile != {} :

                    tp_jsonfiles = hf.jsonfiles(tilepairdir)

                    tiles,slices,positions = hf.neighbours_from_json(tp_jsonfiles,lead_tile['tile'])

                    if tiles in (None,[]): raise PreventUpdate

                    slices = list(map(int,slices))

                    o_val = min(slices)

                    slicestyle = {'display': 'none'}

                if trigger in ('stack_dd','dummystore'):
                    o_val = int((o_max - o_min) / 2) + o_min
                else:
                    o_val = orig_sec

                if o_min == o_max: slicestyle = {'display':'none'}
                
                url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack_sel
                url1 = url + '/tileIds'
                
                tile = requests.get(url1).json()[0]
                
                url2 = url +'/tile/' + tile                 
                url2 +=  '/render-parameters'
                
                tilespec = requests.get(url2).json()
                                
                max_int = tilespec['tileSpecs'][0]['maxIntensity']     

                return o_val,o_min,o_max,slicestyle,max_int,[0,max_int]
            
            else:
                raise PreventUpdate
            
                
                

    
    # init tile selector
    @app.callback([Output({'component':'tile_dd'+idx_str,'module': MATCH},'options'),
                   Output({'component':'tile_dd'+idx_str,'module': MATCH},'value')],
                  Input({'component':'tileim_section_in'+idx_str,'module': MATCH},'value'),
                  [State({'component': 'owner_dd','module': MATCH},'value'),
                   State({'component': 'project_dd','module': MATCH},'value'),
                   State({'component': 'stack_dd','module': MATCH},'value'),
                   State({'component':'tile_dd'+idx_str,'module': MATCH},'value'),
                   State({'component': 'tp_dd', 'module': MATCH},'value'),
                   State({'component': 'neighbours', 'module': MATCH},'children'),
                   State({'component': 'lead_tile', 'module': MATCH},'data'),
                   State('url', 'pathname')]
                  ,prevent_initial_call=True)
    def slicetotiles(slicenum,owner,project,stack,prev_tile,tilepairdir,neighbours,lead_tile,thispage):

        if None in (slicenum,owner,project,stack,neighbours,lead_tile):
            raise PreventUpdate
        
        if 'None' in (owner,project,stack):
            raise PreventUpdate

        thispage = thispage.lstrip('/')

        if not thispage in hf.trigger(key='module'):
            raise PreventUpdate

        trigger = hf.trigger()
        tileim_index = trigger.split('_')[-1]

        url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack
        url += '/tileIds?matchPattern='
        
        if owner in params.slicenumformat.keys():            
            url += params.slicenumformat[owner] %slicenum
        
        tiles = requests.get(url).json()

        if tiles == []:
            raise PreventUpdate
        
        t_labels = tiles.copy()
        tile = tiles[int(len(tiles)/2)]

        if prev_tile is None:
            prev_tile = tile

        if lead_tile in (None,{},''):
            lead_tile=dict(tile=prev_tile)

        if not 'stack' in lead_tile.keys() or lead_tile['stack'] != stack:
            lead_tile = dict(tile=prev_tile,stack=stack)

        lead_tile['slice'] = slicenum

        if neighbours == 'True' and tileim_index != '0' and tilepairdir not in ('', None):

            tp_jsonfiles = hf.jsonfiles(tilepairdir)
            if 'tile' in lead_tile.keys():
                tiles,slices,positions = hf.neighbours_from_json(tp_jsonfiles,lead_tile['tile'])
                t_labels = tiles.copy()

                if tiles==[]:
                    raise PreventUpdate

                tile = tiles[-1]

            if owner in params.tile_display.keys() and len(slices)==len(t_labels):
                t_labels, tile0 = params.tile_display[owner](tiles, prev_tile, slicenum)

                for t_idx,label in enumerate(t_labels):
                    if len(slices)>1 :
                        slicestr = 'Slice '+str(slices[t_idx])+' - '
                    else:
                        slicestr = ''

                    t_labels[t_idx] = slicestr+label

            for t_idx,label in enumerate(t_labels):
                t_labels[t_idx] = t_labels[t_idx]+' '+positions[t_idx]

        elif owner in params.tile_display.keys():
            t_labels, tile = params.tile_display[owner](tiles, prev_tile, slicenum)

        if None in (t_labels, tile):
            raise PreventUpdate

        # assemble dropdown
        dd_options = list(dict())
        for t_idx,item in enumerate(tiles):
            dd_options.append({'label':t_labels[t_idx], 'value':item})

        if tileim_index == '0' and lead_tile['tile'] in tiles:
            tile = lead_tile['tile']

        return dd_options, tile
    
    
    @app.callback([Output({'component': 'tileim_imurl'+idx_str, 'module': MATCH},'children'),
                   Output({'component': 'tileim_link'+idx_str, 'module': MATCH},'children'),
                   Output({'component': 'lead_tile'+idx_str, 'module': MATCH},'data')],
                  [Input({'component':'tile_dd'+idx_str,'module': MATCH},'value'),
                   Input({'component': 'store_render_launch', 'module': MATCH},'data')],
                  [State({'component': 'owner_dd','module': MATCH},'value'),
                   State({'component': 'project_dd','module': MATCH},'value'),
                   State({'component': 'stack_dd','module': MATCH},'value'),
                   State({'component': 'tileim_section_in' + idx_str, 'module': MATCH}, 'value'),
                   State('url', 'pathname')
                   ],prevent_initial_call=True)
    def im_view_url(tile,runstore,owner,project,stack,section,thispage):
        if not dash.callback_context.triggered: 
            raise PreventUpdate
        # print('tile is now: '+ tile)
        # print('stack is now: '+ stack)

        thispage = thispage.lstrip('/')

        if not thispage in hf.trigger(key='module'):
            raise PreventUpdate
            
        if None in (tile,runstore,owner,project,stack):
            raise PreventUpdate
        
        if 'None' in (owner,project,stack):
            raise PreventUpdate
        
        
        url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack
        url += '/tile/' + tile 
        
        url1 = url + '/render-parameters'
        
        try:
            tilespec = requests.get(url1).json()
        except:
            raise PreventUpdate
        
        scale = float(params.im_width) / float(tilespec['width'])  
        
        out_scale = '%0.2f' %scale
        
        imurl = url +'/jpeg-image?scale=' + out_scale      
        
        if runstore is None or not 'mt_params' in runstore.keys():
            scale1 = params.default_tile_scale
        else:
            scale1 = runstore['mt_params']['scale']

        
        url1 += '?filter=true&scale=' + str(scale1)

        leadtile = dict(tile=tile,section=section,stack=stack)

        return imurl, url1, leadtile
    
    
    # init tile image display
    @app.callback(Output({'component': 'tileim_image'+idx_str, 'module': MATCH},'src'),
                  [Input({'component': 'tileim_contrastslider'+idx_str, 'module': MATCH},'value'),
                   Input({'component': 'tileim_imurl'+idx_str, 'module': MATCH},'children')],
                  State('url','pathname')
                  )
    def im_view(c_limits,imurl,thispage):
        if not dash.callback_context.triggered: 
            raise PreventUpdate     

        thispage = thispage.lstrip('/')

        if not thispage in hf.trigger(key='module'):
            raise PreventUpdate

        if None in (c_limits,imurl):
            raise PreventUpdate
        
        if 'None' in (c_limits,imurl):
            raise PreventUpdate
        
        imurl += '&minIntensity=' + str(c_limits[0]) + '&maxIntensity=' + str(c_limits[1])
        
        return imurl
    

    # init slice image display
    @app.callback(Output({'component': 'sliceim_image'+idx_str, 'module': MATCH},'src'),
                  [Input({'component':'sliceim_section_in'+idx_str,'module': MATCH},'value'),
                   Input({'component': 'store_render_launch', 'module': MATCH},'data'),
                   Input({'component': 'sliceim_contrastslider'+idx_str, 'module': MATCH},'value')],
                  [State({'component': 'owner_dd','module': MATCH},'value'),
                   State({'component': 'project_dd','module': MATCH},'value'),
                   State({'component': 'stack_dd','module': MATCH},'value'),
                   State('url', 'pathname')
                   ],prevent_initial_call=True)
    def slice_view(section,runstore,c_limits,owner,project,stack,thispage):
        if not dash.callback_context.triggered: 
            raise PreventUpdate
        
        thispage = thispage.lstrip('/')        
        
        if not hf.trigger(key='module') == thispage:
            raise PreventUpdate

        if None in (section,runstore,owner,project,stack):
            raise PreventUpdate
        
        if 'None' in (owner,project,stack):
            raise PreventUpdate
        
        
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


@app.callback(Output({'component': 'lead_tile', 'module': MATCH},'data'),
              Input({'component': 'lead_tile_0', 'module': MATCH},'data'))
def collect_leadtiles(lead_in):
    # print(lead_in)
    return lead_in
