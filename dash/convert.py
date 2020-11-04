#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
import dash_core_components as dcc
import dash_html_components as html

from sbem import sbem_conv


base = html.Div([html.H4("Import volume EM datasets - Choose type:"),dcc.Dropdown(
        id='conv_dropdown1',persistence=True,
        options=[
            {'label': 'SBEMImage', 'value': 'SBEMImage'}            
        ],
        value='SBEMImage'
    )])



sbem = sbem_conv.page

