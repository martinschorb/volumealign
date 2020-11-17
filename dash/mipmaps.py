#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 16:15:27 2020

@author: schorb
"""
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
import params

from app import app


main=html.Div(html.Div(id='mipmaps')
              )


            
@app.callback(Output('mipmaps','children'),
    Input('active_project','data'))
def update_stack_state(indict):

    proj_status = html.Div([html.H4('Current active stack:'),
                            'Owner: '+indict['owner']+' ;   Project: '+indict['project']+' ;  Stack: '+indict['stack']
                            ])
            
    return proj_status

# Full page layout:
    
page = []