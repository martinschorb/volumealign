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


from app import app
import params
from utils import launch_jobs, pages
from utils import helper_functions as hf


from callbacks import filebrowse


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

    

page = [filebrowse,directory_sel]

        