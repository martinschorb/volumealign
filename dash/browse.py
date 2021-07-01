#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 08:42:12 2020

@author: schorb
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
from dash.exceptions import PreventUpdate


import os
#for file browsing dialogs
# import json
# import requests
# import importlib


from app import app
import params
from utils import launch_jobs, pages
from utils import helper_functions as hf


# element prefix
label = "browse"
parent = "convert"


# SELECT input directory

# get user name and main group to pre-polulate input directory

group = params.group

# ============================
# set up render parameters

owner = "SBEM"


# =============================================
# # Page content



# Pick source directory


directory_sel = html.Div(children=[html.H4("Select dataset root directory:"),
                                   html.Script(type="text/javascript",children="alert('test')"),                                   
                                   dcc.Input(id={'component': 'path_input', 'module': label}, type="text", debounce=True,value="/g/"+group,persistence=True,className='dir_textinput')
                                   ])
        
        
filebrowse = pages.filebrowse(label)

startpath = os.getcwd()
show_files = False
show_hidden = False


@app.callback(Output({'component': 'path_input', 'module': label},'value'),              
              Input({'component': 'path_store', 'module': label},'data')
              )
def update_store(inpath):
    if os.path.exists(str(inpath)):
        path = inpath
    else:
        path = startpath
        
    return path


@app.callback([Output({'component': 'browse_dd', 'module': label},'options'),
               Output({'component': 'path_store', 'module': label},'data')],
              [Input({'component': 'browse_dd', 'module': label},'value'),
               Input({'component': 'path_input', 'module': label},'n_blur')],
              [State({'component': 'path_input', 'module': label},'value'),
               State({'component': 'path_store', 'module': label},'data')]
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
    

page = [filebrowse,directory_sel]

        