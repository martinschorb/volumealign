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

import os
import glob
# import numpy as np
# import requests
import importlib

from dashUI import params

from app import app

from utils import pages
from utils import helper_functions as hf

from callbacks import render_selector, substack_sel, match_selector, tile_view

module = 'pointmatch'

matchtypes = [{'label': 'SIFT', 'value': 'SIFT'}]

matchmodules = ['sift.sift_pointmatch']

storeinit = {}
store = pages.init_store(storeinit, module)

for storeitem in params.match_store.keys():
    store.append(dcc.Store(id={'component': 'store_' + storeitem, 'module': module}, storage_type='session',
                           data=params.match_store[storeitem]))

main = html.Div(id={'component': 'main', 'module': module},
                children=html.H3("Generate/Update PointMatchCollection for Render stack"))

page = [main]

# # ===============================================
#  RENDER STACK SELECTOR

page.append(pages.render_selector(module))

# Pre-fill render stack selection from previous module

us_out, us_in, us_state = render_selector.init_update_store(module, 'tilepairs')


@app.callback(us_out, us_in, us_state,
              prevent_initial_call=True)
def pointmatch_update_store(*args):
    thispage = args[-1]
    args = args[:-1]
    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    return render_selector.update_store(*args)


page1 = []

# ===============================================

page2 = html.Div([html.Div([html.H4("Select Tilepair source directory:"),
                            dcc.Dropdown(id={'component': 'tp_dd', 'module': module}, persistence=True,
                                         clearable=False),
                            html.Br(),
                            html.Div(id={'component': 'tp_prefix', 'module': module}, style={'display': 'none'})
                            ]),
                  html.H4("Choose type of PointMatch determination:"),
                  dcc.Dropdown(id={'component': 'pm_type_dd', 'module': module}, persistence=True,
                               options=matchtypes,
                               value='SIFT')
                  ])


@app.callback([Output({'component': 'tp_dd', 'module': module}, 'options'),
               Output({'component': 'tp_dd', 'module': module}, 'value')],
              Input({'component': 'stack_dd', 'module': module}, 'value'),
              State('url', 'pathname'),
              prevent_initial_call=True)
def pointmatch_tp_dd_fill(stack, thispage):
    """
    Fills the tilepair dropdown.

    :param str stack:
    :param str thispage: current page URL
    :return: options and value of tilepair dropdown "tp_dd"
    :rtype: (list of dict, str)
    """
    if stack in (None, ''):
        raise PreventUpdate

    thispage = thispage.lstrip('/')

    if thispage in (None, '') or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    tp_dirlist = [d_item for d_item in glob.glob(params.json_run_dir + '/tilepairs_' + params.user + '*' + stack + '*')
                  if os.path.isdir(d_item)]
    tpdir_dd_options = list(dict())

    if tp_dirlist == []:
        tpdir_dd_options.append({'label': 'no tilepairs found for selected stack', 'value': ''})
    else:
        for tp_dir in tp_dirlist:
            tpdir_dd_options.append({'label': os.path.basename(tp_dir), 'value': tp_dir})

    return tpdir_dd_options, tpdir_dd_options[-1]['value']


# ===============================================


page3 = pages.match_selector(module, newcoll=True)

# =============================================
# # Page content for specific pointmatch client


page4 = [pages.log_output(module, hidden=True)]

# # =============================================
# # # Page content

page4.append(html.Div([html.Br(), 'No output data type selected.'],
                      id=module + '_nullpage'))

switch_outputs = [Output(module + '_nullpage', 'style')]

status_inputs = []

for pmtypesel, impmod in zip(matchtypes, matchmodules):
    thismodule = importlib.import_module(impmod)

    page1.append(html.Div(getattr(thismodule, 'page1'),
                          id={'component': 'page1', 'module': pmtypesel['value']},
                          style={'display': 'none'}))
    switch_outputs.append(Output({'component': 'page1', 'module': pmtypesel['value']}, 'style'))

    page4.append(html.Div(getattr(thismodule, 'page2'),
                          id={'component': 'page2', 'module': pmtypesel['value']},
                          style={'display': 'none'}))
    switch_outputs.append(Output({'component': 'page2', 'module': pmtypesel['value']}, 'style'))

    status_inputs.append(Input({'component': 'status', 'module': pmtypesel['value']}, 'data'))


# Switch the visibility of elements for each selected sub-page based on the import type dropdown selection

@app.callback(switch_outputs,
              Input({'component': 'pm_type_dd', 'module': module}, 'value'),
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

    return outstyles


# collect Render selections from sub pages and make them available to following pages

c_in, c_out = render_selector.subpage_launch(module, matchtypes)


@app.callback(c_out, c_in)
def pointmatch_merge_launch_stores(*inputs):
    return hf.trigger_value()


page.append(html.Div(page1))
page.append(html.Div(page2))
page.append(html.Div(page3))
page.append(html.Div(page4))
