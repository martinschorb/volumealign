#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import importlib

# import params
from app import app
# from utils import pages
from utils import helper_functions as hf

from callbacks import runstate, render_selector

# from inputtypes import sbem_conv, serialem_conv

module = 'convert'

inputtypes = [
    {'label': 'SBEMImage', 'value': 'SBEM'},
    {'label': 'SerialEM Montage', 'value': 'SerialEM'},
    {'label': 'Image stack - FIB/SEM', 'value': 'tifstack'},
]

inputmodules = [
    'inputtypes.sbem_conv',
    'inputtypes.serialem_conv',
    'inputtypes.tifstack_conv'
]

main = html.Div(children=[html.H3("Import volume EM datasets - Choose type:", id='conv_head'),
                          dcc.Dropdown(id={'component': 'import_type_dd', 'module': module},
                                       options=inputtypes, value='')
                          ])

stores = [dcc.Store(id={'component': 'store_render_init', 'module': module}, storage_type='session', data=''),
          dcc.Store(id={'component': 'store_render_launch', 'module': module}, storage_type='session', data='')]
# pages.init_store({}, module)

page = [main]
page.extend(stores)

page1 = []

# # =============================================
# # # Page content

page1.append(html.Div([html.Br(), 'No data type selected.'],
                      id=module + '_nullpage'))

switch_outputs = [Output(module + '_nullpage', 'style')]

status_inputs = []

page2 = []

for inputsel, impmod in zip(inputtypes, inputmodules):
    thismodule = importlib.import_module(impmod)

    page1.append(html.Div(getattr(thismodule, 'page1'),
                          id={'component': 'page1', 'module': inputsel['value']},
                          style={'display': 'none'}))
    switch_outputs.append(Output({'component': 'page1', 'module': inputsel['value']}, 'style'))

    page2.append(html.Div(getattr(thismodule, 'page2'),
                          id={'component': 'page2', 'module': inputsel['value']},
                          style={'display': 'none'}))
    switch_outputs.append(Output({'component': 'page2', 'module': inputsel['value']}, 'style'))

    status_inputs.append(Input({'component': 'status', 'module': inputsel['value']}, 'data'))

switch_outputs.append(Output({'component': 'store_render_init', 'module': module}, 'data'))


# Switch the visibility of elements for each selected sub-page based on the import type dropdown selection

@app.callback(switch_outputs,
              Input({'component': 'import_type_dd', 'module': module}, 'value'),
              State('url', 'pathname'))
def convert_output(dd_value, thispage):
    """
    Populates the page with subpages.

    :param str dd_value: value of the "import_type_dd" dropdown.
    :param str thispage: current page URL
    :return: List of style dictionaries to determine which subpage content to display.<Br>
             Additionally: the page's "store_render_init" store (setting owner).
    :rtype: (list of dict, dict)
    """
    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    outputs = dash.callback_context.outputs_list
    outstyles = [{'display': 'none'}] * (len(outputs) - 1)

    modules = [m['id']['module'] for m in outputs[1:]]

    for ix, mod in enumerate(modules):

        if mod == dd_value:
            outstyles[ix + 1] = {}

    if dd_value not in modules:
        outstyles[0] = {}

    # if dd_value in (None,''):
    #     dd_value = 'SBEM'
    outstore = dict()
    outstore['owner'] = dd_value

    out = outstyles
    out.append(outstore)

    return out


# collect Render selections from sub pages and make them available to following pages

c_in, c_out = render_selector.subpage_launch(module, inputtypes)


@app.callback(c_out, c_in)
def convert_merge_launch_stores(*inputs):
    return hf.trigger_value()


page.append(html.Div(page1))
page.append(html.Div(page2))
