#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State

from app import app

from sbem import sbem_conv


base = html.Div([html.H4("Import volume EM datasets - Choose type:"),dcc.Dropdown(
        id='conv_dropdown1',persistence=True,
        options=[
            {'label': 'SBEMImage', 'value': 'SBEMImage'}            
        ],
        value='SBEMImage'
    )])



@app.callback(Output('convert-page1', 'children'),
    [Input('conv_dropdown1', 'value')])
def convert_output(value):
    if value=='SBEMImage':
        return sbem_conv.page
    else:
        return [html.Br(),'No data type selected.']


# sbem = sbem_conv.page

# Final page layout defined in callback: convert_output