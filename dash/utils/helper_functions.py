#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:24:32 2020

@author: schorb
"""

import dash
import json
import os
import numpy as np

import params

def trigger(key=None,debug=False):

    ctx = dash.callback_context
    if debug:print('propid: ' + ctx.triggered[0]['prop_id'])
        
    if ctx.triggered[0]['prop_id'] == '.' or not ctx.triggered[0]['prop_id'].startswith('{'):
        if debug:
            if ctx.triggered[0]['prop_id'] == '.':
                print('no trigger present')
            else:
                print('site-specific trigger')
                
        if key is None:
            trigger = ctx.triggered[0]['prop_id'].partition('.')[0]
        else:
            i=0
            while i<len(ctx.inputs.keys()) and not list(ctx.inputs.keys())[i].startswith('{'):
                i+=1            
            
            if not list(ctx.inputs.keys())[i].startswith('{'):
                trigger = None
            else:
                trigger = json.loads(list(ctx.inputs.keys())[i].split('}.')[0]+'}')[key]
    
    else:
        if key is None: key = 'component'
        
        if debug: print('global trigger - ' + ctx.triggered[0]['prop_id'].partition('}.')[0]+'}')
        
        trigger = json.loads(ctx.triggered[0]['prop_id'].partition('}.')[0]+'}')[key]
    
    if debug: print('Trigger out: ' + str(key) + ' - ' + trigger)
    
    return trigger

# def trigger_module():
#     ctx = dash.callback_context 
    
#     if ctx.triggered[0]['prop_id'] == '.':
#         i=0
#         while i<len(ctx.inputs.keys()) and not list(ctx.inputs.keys())[i].startswith('{'):
#             i+=1            
        
#         if not list(ctx.inputs.keys())[i].startswith('{'):
#             module=None
#         else:
#             module = json.loads(list(ctx.inputs.keys())[i].split('}.')[0]+'}')['module']
        
#     else:
#         if not ctx.triggered[0]['prop_id'].startswith('{'):
#             module = ctx.triggered[0]['prop_id'].partition('.')[0]
#         else:
#             module = json.loads(ctx.triggered[0]['prop_id'].partition('}.')[0]+'}')['module']
    
#     print('module')
#     print(module)
#     return module



def input_components():
    
    ctx = dash.callback_context 
    
    incomp = [indict['id']['component'] for indict in ctx.inputs_list]
    inval = [indict[indict['property']] for indict in ctx.inputs_list]
    
    return incomp, inval



def output_components():
    
    ol = dash.callback_context.outputs_list 
    
    outcomp = [indict['id']['component'] for indict in ol]
    outprop = [indict['property'] for indict in ol]
    
    return outcomp, outprop



def compset_radiobutton(c_options):
    outopt = list()   
    
    for opt in params.comp_options:
        if opt['value'] in c_options: outopt.append(opt)
    
    return outopt




def tilepair_numfromlog(tilepairdir,stack):
    
    tp_log = params.render_log_dir+'/'+''.join(os.path.basename(tilepairdir).partition(stack+'_')[slice(0,3,2)])+'.log' 
    
    tp_log_mipmaps = params.render_log_dir+'/'+''.join(os.path.basename(tilepairdir).partition(stack+'_mipmaps_')[slice(0,3,2)])+'.log' 
        
    
    if os.path.exists(tp_log):
        l_out = os.popen('tail -n 5 '+tp_log).read().partition('total pairs\n')
    elif os.path.exists(tp_log_mipmaps):
        l_out = os.popen('tail -n 5 '+tp_log_mipmaps).read().partition('total pairs\n')
    else:
        l_out = ''

    if l_out == '': return 'no tilepairs'
    tpairs = l_out[0].partition('NeighborPairs: exit, saved ')[2]

    if tpairs == '':
        return 'no tilepairs'
    else:
        return int(tpairs)

def neighbours_from_json(infiles,target_id):

    if type(infiles) is str:
        infiles=[infiles]
    elif type(infiles) is not list:
        TypeError('expecting file name or list thereof!')

    tile_entries = dict()

    for jsonfile in infiles:
        with open(jsonfile, 'r') as f:
            tile_entries.update(json.load(f))

    neighbours = list()
    slices = list()

    if 'neighborPairs' in tile_entries.keys():

        for pair in tile_entries['neighborPairs']:
            for a,b in zip(('p','q'),('q','p')):
                if target_id in pair[a]['id']:
                    neighbours.append(pair[b]['id'])
                    if pair[b]['groupId'] not in slices:
                        slices.append(pair[b]['groupId'])


    return neighbours,slices

def jsonfiles(dirname):
    tp_dir = os.path.join(params.json_run_dir, dirname)
    tp_json = os.listdir(tp_dir)

    return [os.path.join(params.json_run_dir, dirname, tpj) for tpj in tp_json]


def spark_nodes(n_cpu):
    nodes,cores1 = np.divmod(n_cpu,params.cpu_pernode_spark)
    
    nodes_out = nodes + (cores1>0)

    return nodes_out