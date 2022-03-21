#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
import dash
from dash import dcc
from dash import html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input,Output,State

import importlib

from app import app

from utils import pages
from utils import helper_functions as hf

from callbacks import render_selector

from filetypes import BDV_finalize,MoBIE_finalize


module='finalize'
previous = 'export'


subpages = [{'label': 'BigDataViewer (BDV) XML', 'value': 'BDV'},
            {'label': 'Add to MoBIE project', 'value': 'MoBIE'}]

submodules = [
    'filetypes.BDV_finalize',
    'filetypes.MoBIE_finalize'
    ]


main=html.Div(id={'component': 'main', 'module': module},children=html.H3("Finalize output format."))


stores = [dcc.Store(id={'component': 'store_init_render', 'module': module}, storage_type='session',data=''),
          dcc.Store(id={'component': 'store_render_launch', 'module': module}, storage_type='session',data='')]


page = [main]
page.extend(stores)


# ===============================================
       
page0 = html.Div([html.H4("Choose post-processing target format"),
                  dcc.Dropdown(id={'component': 'subpage_dd', 'module': module},persistence=True,
                                options=subpages,
                                value='')
                  ])                                

page.append(page0)


# =============================================
# # Page content for specific export call



page1 = []

# # =============================================
# # # Page content

page1.append(html.Div([html.Br(), 'No data type selected.'],
                      id=module+'_nullpage'))

switch_outputs = [Output(module+'_nullpage', 'style')]

status_inputs = []

page2 = []


for subsel, impmod in zip(subpages, submodules):
    thismodule = importlib.import_module(impmod)

    page1.append(html.Div(getattr(thismodule, 'page1'),
                          id={'component': 'page1', 'module': subsel['value']},
                          style={'display': 'none'}))
    switch_outputs.append(Output({'component': 'page1', 'module': subsel['value']}, 'style'))

    page2.append(html.Div(getattr(thismodule, 'page2'),
                          id={'component': 'page2', 'module': subsel['value']},
                          style={'display': 'none'}))
    switch_outputs.append(Output({'component': 'page2', 'module': subsel['value']}, 'style'))

    status_inputs.append(Input({'component': 'status', 'module': subsel['value']}, 'data'))


# Switch the visibility of elements for each selected sub-page based on the import type dropdown selection

@app.callback(switch_outputs,
              Input({'component': 'subpage_dd', 'module': module}, 'value'),
              State('url', 'pathname'))
def convert_output(dd_value, thispage):
    thispage = thispage.lstrip('/')

    if thispage == '' or not thispage in hf.trigger(key='module'):
        raise PreventUpdate

    outputs = dash.callback_context.outputs_list
    outstyles = [{'display': 'none'}] * len(outputs)

    modules = [m['id']['module'] for m in outputs[1:]]

    for ix, mod in enumerate(modules):

        if mod == dd_value:
            outstyles[ix + 1] = {}

    if dd_value not in modules:
        outstyles[0] = {}

    return outstyles


# collect variables from sub pages and make them available to following pages

c_in, c_out = render_selector.subpage_launch(module, subpages)

@app.callback(c_out,c_in)
def convert_merge_launch_stores(*inputs):
    return hf.trigger_value()

page.append(html.Div(page1))
page.append(html.Div(page2))
