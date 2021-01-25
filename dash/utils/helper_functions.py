#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:24:32 2020

@author: schorb
"""

import dash
import json
import os

import params

def trigger_component():
    ctx = dash.callback_context
        
    trigger = json.loads(ctx.triggered[0]['prop_id'].partition('}.')[0]+'}')['component']

    return trigger

def input_components():
    
    ctx = dash.callback_context 
    
    incomp = [indict['id']['component'] for indict in ctx.inputs_list]
    inval = [indict[indict['property']] for indict in ctx.inputs_list]
    
    return incomp, inval


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
               
    
    tpairs = l_out[0].partition('NeighborPairs: exit, saved ')[2]
    
    if tpairs == '': return 'no tilepairs'
    
    print(tpairs)
    
    return int(tpairs)
    
