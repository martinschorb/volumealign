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

import os
#for file browsing dialogs
import json
import requests
import importlib


from app import app
import params
from utils import launch_jobs


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
                                   dcc.Input(id="input1", type="text", debounce=True,value="/g/"+group,persistence=True,className='dir_textinput')
                                   ])



        
        
filebrowse = html.Details([html.Summary('Browse')])

fbdd = dcc.Dropdown(id='dd',clearable=True,searchable=False)

fbstore = dcc.Store(id='path')

startpath = os.getcwd()
show_files = True
show_hidden = False

@app.callback(Output('path','data'),
              Input('input1','value')
              )
def update_store(inpath):
    if os.path.isdir(str(inpath)):
        path = inpath
    else:
        path = startpath
        
    return path


@app.callback([Output('dd','options'),
               Output('path','data')],
              [Input('dd','value'),
               Input('input1','value')]
              )
def update_owner_dd(filesel,inpath):
    dd_options = list(dict())
    
    if os.path.isdir(str(inpath)):
        path = inpath
    else:
        path = startpath
        
    return path
    
    
    
    if filesel is None or filesel[0:2] ==  '> ' or filesel == '..' :

        
        if not filesel is None:
            if filesel[0:2] ==  '> ':
                path = os.path.join(path,filesel[2:])
            elif filesel == '..':
                path = os.path.abspath(os.path.join(path,filesel))
        
        files = os.listdir(path)        
    
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
    

page = [filebrowse,fbdd,directory_sel]

        