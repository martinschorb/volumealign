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
                                   dcc.Input(id="input1", type="text", debounce=True,placeholder="/g/"+group,persistence=True,className='dir_textinput')
                                   ])



        
        
filebrowse = html.Details([html.Summary('Browse')])

fbdd = dcc.Dropdown(id='dd')

startpath = os.getcwd()


@app.callback([Output('dd','options'),
               Output('input1','value')],
              Input('dd','value')
              )
def update_owner_dd(filesel):
    dd_options = list(dict())
    path = startpath
    
    if filesel is None or filesel[0:2] ==  '> ' :
        
        if not filesel is None:
            path = os.path.join(path,filesel[2:])
        
        files = os.listdir(path)        
    
        dd_options.append({'label':'..', 'value':'..'})
    
        for item in files:        
      
            if os.path.isdir(item):
                dd_options.append({'label':'> '+item, 'value':'> '+item})
            else:
                dd_options.append({'label':item, 'value':item})
            
        return dd_options,dash.no_update
    
    else:
        path = os.path.join(path,filesel)
        return dash.no_update,path
    

page = [filebrowse,fbdd,directory_sel]

        