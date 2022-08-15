#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
import dash
from dash import dcc, html, callback
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

import importlib
import time

from dashUI.utils import pages
from dashUI.utils import helper_functions as hf

from dashUI.callbacks import runstate, render_selector

from dashUI.pages.side_bar import sidebar

module = 'finalize'
previous = 'export'

dash.register_page(__name__,
                   name='Final post-processing')


subpages = [{'label': 'BigDataViewer (BDV) XML', 'value': 'finalize_BDV'},
            {'label': 'Add to MoBIE project', 'value': 'finalize_MoBIE'}
            ]

submodules = [
    'dashUI.filetypes.BDV_finalize',
    'dashUI.filetypes.MoBIE_finalize'
]

main = html.Div(id={'component': 'main', 'module': module}, children=html.H3("Finalize output format."))

stores = [dcc.Store(id={'component': 'store_init_render', 'module': module}, storage_type='session', data=''),
          dcc.Store(id={'component': 'store_render_launch', 'module': module}, storage_type='session', data=''),
          dcc.Store(id={'component': 'store_launch_status', 'module': module}, storage_type='session', data='')]

page = [main]
page.extend(stores)

# ===============================================

page0 = html.Div([html.H4("Choose post-processing target format"),
                  dcc.Dropdown(id={'component': 'subpage_dd', 'module': module},  # persistence=True,
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
                      id=module + '_nullpage'))

switch_outputs = [Output(module + '_nullpage', 'style')]

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

@callback(switch_outputs,
          Input({'component': 'subpage_dd', 'module': module}, 'value'),
          State('url', 'pathname'))
def finalize_output(dd_value, thispage):
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
    outstyles = [{'display': 'none'}] * len(outputs)

    modules = [m['id']['module'] for m in outputs[1:]]

    for ix, mod in enumerate(modules):
        if mod == dd_value:
            outstyles[ix + 1] = {}

    if dd_value not in modules:
        outstyles[0] = {}

    return outstyles


# collect variables from subpages and make them available to following pages

c_in, c_out = render_selector.subpage_launch(module, subpages)

@callback(c_out, c_in)
def finalize_merge_launch_stores(*inputs):
    return hf.trigger_value()


page.append(html.Div(page1))
page.append(html.Div(page2))


def layout():
    return [sidebar(), html.Div(page, className='main')]
