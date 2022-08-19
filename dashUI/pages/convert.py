#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
import dash
from dash import dcc, html, callback, ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import importlib

from dashUI.utils import helper_functions as hf
from dashUI.pages.side_bar import sidebar
from dashUI.callbacks import runstate, render_selector
from dashUI.callbacks.pages_cb import cb_convert as cb

# from inputtypes import sbem_conv, serialem_conv

module = 'convert'
dash.register_page(__name__,
                   name='Convert & upload')
inputtypes = [
    {'label': 'SBEMImage', 'value': 'SBEM'},
    {'label': 'SerialEM Montage', 'value': 'SerialEM'},
    {'label': 'Image stack - FIB/SEM', 'value': 'FIBSEM'},
]

inputmodules = [
    'dashUI.inputtypes.sbem_conv',
    'dashUI.inputtypes.serialem_conv',
    'dashUI.inputtypes.fibsem_conv'
]

main = html.Div(children=[html.H3("Import volume EM datasets - Choose type:", id='conv_head'),
                          dcc.Dropdown(id={'component': 'import_type_dd', 'module': module},
                                       options=inputtypes, value='', className='dropdown_inline')
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

@callback(switch_outputs,
          Input({'component': 'import_type_dd', 'module': module}, 'value'),
          State('url', 'pathname'))
def convert_output(*args):
    """
    Populates the page with subpages.

    :param str dd_value: value of the "import_type_dd" dropdown.
    :param str thispage: current page URL
    :return: List of style dictionaries to determine which subpage content to display.<Br>
             Additionally: the page's "store_render_init" store (setting owner).
    :rtype: (list of dict, dict)
    """
    return cb.convert_output(*args)



# collect Render selections from sub pages and make them available to following pages

c_in, c_out = render_selector.subpage_launch(module, inputtypes)


@callback(c_out, c_in)
def convert_merge_launch_stores(*inputs):
    return hf.trigger_value()


page.append(html.Div(page1, className='subpage'))
page.append(html.Div(page2))


def layout():
    return [sidebar(), html.Div(page, className='main')]
