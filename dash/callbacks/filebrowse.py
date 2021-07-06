#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 15:42:18 2021

@author: schorb
"""
import os

import dash

from app import app


from dash.dependencies import Input, Output, State, MATCH, ALL
from utils import helper_functions as hf


startpath = os.getcwd()
show_files = False
show_hidden = False


@app.callback(Output({'component': 'path_input', 'module': MATCH},'value'),              
              Input({'component': 'path_store', 'module': MATCH},'data')
              )
def update_store(inpath):
    if os.path.exists(str(inpath)):
        path = inpath
    else:
        path = startpath
        
    return path


@app.callback([Output({'component': 'browse_dd', 'module': MATCH},'options'),
               Output({'component': 'path_store', 'module': MATCH},'data')],
              [Input({'component': 'browse_dd', 'module': MATCH},'value'),
               Input({'component': 'path_input', 'module': MATCH},'n_blur')],
              [State({'component': 'path_input', 'module': MATCH},'value'),
               State({'component': 'path_store', 'module': MATCH},'data')]
              )
def update_owner_dd(filesel,intrig,inpath,path):
    if dash.callback_context.triggered: 
        trigger = hf.trigger_component()
    else:
        trigger='-'
    
    
    if os.path.isdir(str(inpath)):
        inpath = inpath
    elif os.path.exists(str(inpath)):
        inpath = os.path.dirname(inpath)
    else:
        path = startpath
    
    if not os.path.isdir(str(path)):        
        if os.path.isdir(str(inpath)):
            path = inpath
        else:
            path = startpath
                
    if trigger == 'path_input':
            
        if os.path.isdir(str(inpath)):
            path = inpath
            filesel = None
    
    
    
    if filesel is None or filesel[0:2] ==  '> ' or filesel == '..' :
        
        if not filesel is None:
            if filesel[0:2] ==  '> ':
                path = os.path.join(path,filesel[2:])
            elif filesel == '..':
                path = os.path.abspath(os.path.join(path,filesel))

        files = os.listdir(path)
        
        dd_options = list(dict())
    
        dd_options.append({'label':'..', 'value':'..'})
        
        f_list=list(dict())      
        
        files.sort()
    
        for item in files:        
            # print(item)
            # print(os.path.isdir(os.path.join(path,item)))
            if os.path.isdir(os.path.join(path,item)):
                dd_options.append({'label':'\u21AA '+item, 'value':'> '+item})
            else:
                if item.startswith('.') and show_hidden or not item.startswith('.'):
                    f_list.append({'label':item, 'value':item})
            
            
            
        if show_files:
            dd_options.extend(f_list)
                
        return dd_options,path
    
    else:
        path = os.path.join(path,filesel)

        return dash.no_update,path