#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:24:32 2020

@author: schorb
"""

import dash
import json

def trigger_component():
    ctx = dash.callback_context
        
    trigger = json.loads(ctx.triggered[0]['prop_id'].partition('}.')[0]+'}')['component']

    return trigger

def input_components():
    
    ctx = dash.callback_context 
    
    incomp = [indict['id']['component'] for indict in ctx.inputs_list]
    inval = [indict[indict['property']] for indict in ctx.inputs_list]
    
    return incomp, inval