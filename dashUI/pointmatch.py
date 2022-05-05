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
import numpy as np
import requests

import params

from app import app

from utils import pages
from utils import helper_functions as hf

from callbacks import runstate, render_selector, substack_sel, match_selector, tile_view

from sift import sift_pointmatch

module = 'pointmatch'

matchtypes = [{'label': 'SIFT', 'value': 'SIFT'}]

status_table_cols = ['stack',
                     'slices',
                     'tiles',
                     'tilepairs']

compute_table_cols = ['Num_CPUs',
                      # 'MemGB_perCPU',
                      'runtime_minutes']

storeinit = {'tpmatchtime': 1000}
store = pages.init_store(storeinit, module)

for storeitem in params.match_store.keys():
    store.append(dcc.Store(id={'component': 'store_' + storeitem, 'module': module}, storage_type='session',
                           data=params.match_store[storeitem]))

main = html.Div(id={'component': 'main', 'module': module},
                children=html.H3("Generate/Update PointMatchCollection for Render stack"))

page = [main]

# # ===============================================
#  RENDER STACK SELECTOR

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


page1 = pages.render_selector(module)

page.append(page1)

# ===============================================

page2 = html.Div([html.Div([html.H4("Select Tilepair source directory:"),
                            dcc.Dropdown(id={'component': 'tp_dd', 'module': module}, persistence=True,
                                         clearable=False),
                            html.Br(),
                            html.Div(id={'component': 'tp_prefix', 'module': module}, style={'display': 'none'})
                            ]),
                  html.H4("Choose type of PointMatch determination:"),
                  dcc.Dropdown(id=module + 'dropdown1', persistence=True,
                               options=matchtypes,
                               value='SIFT')
                  ])

page.append(page2)


@app.callback([Output({'component': 'tp_dd', 'module': module}, 'options'),
               Output({'component': 'tp_dd', 'module': module}, 'value')],
              Input({'component': 'stack_dd', 'module': module}, 'value'),
              State('url', 'pathname'),
              prevent_initial_call=True)
def pointmatch_tp_dd_fill(stack, thispage):
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

page.append(page3)

# # ===============================================
# Compute Settings

compute_settings = html.Details(children=[html.Summary('Compute settings:'),
                                          html.Table([html.Tr([html.Th(col) for col in status_table_cols]),
                                                      html.Tr(
                                                          [html.Td('', id={'component': 't_' + col, 'module': module})
                                                           for col in status_table_cols])
                                                      ], className='table'),
                                          html.Br(),
                                          html.Table([html.Tr([html.Th(col) for col in compute_table_cols]),
                                                      html.Tr([html.Td(
                                                          dcc.Input(id={'component': 'input_' + col, 'module': module},
                                                                    type='number', min=1)) for col in
                                                               compute_table_cols])
                                                      ], className='table'),
                                          dcc.Store(id={'component': 'factors', 'module': module}, data={}),
                                          dcc.Store(id={'component': 'store_compset', 'module': module})
                                          ])


# callbacks

@app.callback([Output({'component': 'input_' + col, 'module': module}, 'value') for col in compute_table_cols],
              [Output({'component': 'factors', 'module': module}, 'modified_timestamp')],
              [Input({'component': 'input_' + col, 'module': module}, 'value') for col in compute_table_cols],
              [Input({'component': 'factors', 'module': module}, 'modified_timestamp')],
              [State({'component': 'factors', 'module': module}, 'data'),
               State('url', 'pathname')],
              prevent_initial_call=True)
def pointmatch_update_compute_settings(*inputs):
    thispage = inputs[-1]
    inputs = inputs[:-1]
    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    idx_offset = len(compute_table_cols)

    trigger = hf.trigger()

    if trigger not in ('factors', 'input_' + compute_table_cols[0]):
        return dash.no_update

    out = list(inputs[:idx_offset])
    out.append(dash.no_update)

    if inputs[0] is None:
        out[0] = params.n_cpu_spark
    else:
        out[0] = inputs[0]

    if type(inputs[1]) in (str, type(None)):
        out[1] = 1
    else:
        if None in inputs[-1].values():
            out[1] = dash.no_update
        else:
            out[1] = np.ceil(inputs[-1][compute_table_cols[-1]] / 60000 / out[0] * (1 + params.time_add_buffer)) + 1

    return out


@app.callback(Output({'component': 'store_compset', 'module': module}, 'data'),
              [Input({'component': 'input_' + col, 'module': module}, 'value') for col in compute_table_cols],
              prevent_initial_call=True)
def pointmatch_store_compute_settings(*inputs):
    storage = dict()

    in_labels, in_values = hf.input_components()

    for input_idx, label in enumerate(in_labels):
        storage[label] = in_values[input_idx]

    return storage


# Update directory and compute settings from stack selection

stackoutput = []

tablefields = [Output({'component': 't_' + col, 'module': module}, 'children') for col in status_table_cols]
compute_tablefields = [Output({'component': 'factors', 'module': module}, 'data')]

stackoutput.extend(tablefields)
stackoutput.extend(compute_tablefields)


@app.callback(stackoutput,
              [Input({'component': 'tp_dd', 'module': module}, 'value'),
               Input({'component': 'store_tpmatchtime', 'module': module}, 'data'),
               Input({'component': 'input_Num_CPUs', 'module': module}, 'value')],
              [State({'component': 'stack_dd', 'module': module}, 'value'),
               State({'component': 'store_allstacks', 'module': module}, 'data'),
               State('url', 'pathname')],
              prevent_initial_call=True)
def pointmatch_comp_set(tilepairdir, matchtime, n_cpu, stack_sel, allstacks, thispage):
    if n_cpu is None:
        n_cpu = params.n_cpu_spark

    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    # n_cpu = int(n_cpu)

    out = dict()
    factors = dict()
    t_fields = [''] * len(status_table_cols)

    # numtp = 1

    if (not stack_sel == '-') and (allstacks is not None):
        stacklist = [stack for stack in allstacks if stack['stackId']['stack'] == stack_sel]
        stack = stack_sel

        if not stacklist == []:
            stackparams = stacklist[0]

            if 'None' in (stackparams['stackId']['owner'], stackparams['stackId']['project']):
                return dash.no_update

            out['zmin'] = stackparams['stats']['stackBounds']['minZ']
            out['zmax'] = stackparams['stats']['stackBounds']['maxZ']
            out['numtiles'] = stackparams['stats']['tileCount']
            out['numsections'] = stackparams['stats']['sectionCount']

            if tilepairdir is None or tilepairdir == '':
                numtp_out = 'no tilepairs'
                totaltime = None
            else:
                numtp = hf.tilepair_numfromlog(tilepairdir, stack_sel)

                if type(numtp) is int:
                    numtp_out = str(numtp)
                    totaltime = numtp * matchtime * params.n_cpu_standalone
                else:
                    numtp_out = 'no tilepairs'
                    totaltime = None

            t_fields = [stack, str(stackparams['stats']['sectionCount']), str(stackparams['stats']['tileCount']),
                        numtp_out]

            factors = {'runtime_minutes': totaltime}

    outlist = []  # ,out]
    outlist.extend(t_fields)
    outlist.append(factors)

    return outlist


# =============================================
# # Page content for specific pointmatch client


page4 = html.Div(id=module + 'page1')

page.append(page4)


@app.callback([Output(module + 'page1', 'children')],
              Input(module + 'dropdown1', 'value'))
def pointmatch_output(value):
    if value == 'SIFT':
        return [sift_pointmatch.page]

    else:
        return [[html.Br(), 'No method type selected.']]


# collect Render selections from sub pages and make them available to following pages

# c_in, c_out = render_selector.subpage_launch(module, matchtypes)
#
# @app.callback(c_out,c_in)
# def pointmatch_merge_launch_stores(*inputs):
#     return hf.trigger_value()
#


# =============================================
# Processing status

# initialized with store
# embedded from callbacks import runstate

page.append(compute_settings)

# # =============================================
# # PROGRESS OUTPUT


collapse_stdout = pages.log_output(module)

# ----------------

# Full page layout:


page.append(collapse_stdout)
