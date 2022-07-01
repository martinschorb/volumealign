#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 15:42:18 2022

@author: schorb
"""

import dash
import numpy as np

from dash.exceptions import PreventUpdate

from dash.dependencies import Input, Output, State, MATCH, ALL
from utils import helper_functions as hf

from app import app

import params


# callbacks

def update_compset_params(module, compute_table_cols):
    params = [*[Output({'component': 'input_' + col, 'module': module}, 'value') for col in compute_table_cols],
              *[Output({'component': 'factors', 'module': module}, 'modified_timestamp')],
              *[Input({'component': 'input_' + col, 'module': module}, 'value') for col in compute_table_cols],
              *[Input({'component': 'factors', 'module': module}, 'modified_timestamp')],
              *[State({'component': 'factors', 'module': module}, 'data'),
                State({'component': 'compute_table_cols', 'module': module}, 'data')],
              State('url', 'pathname')
              ]

    return params


def update_compute_settings(*inputs):
    """
    Calculates the dynamic fields of `compute_table_cols` when changes of its input parameters occur.

    :param (list, dict, str) inputs: [:-4] Input values from "compute_table_cols"<Br>
                                     [-4] trigger timestamp <Br>
                                     [-3] list compute_table_cols: column names<Br>
                                     [-2] dict factors: factors to multiply the input values with.<Br>
                                     [-1] str thispage: current page URL
    :return: factors that update compute_table_cols values when they are changed themselves.
    :rtype: (list, int)
    """

    thispage = inputs[-1]
    thispage = thispage.lstrip('/')

    compute_table_cols = inputs[-2]
    inputs = inputs[:-2]

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
            out[1] = np.ceil(inputs[-1][compute_table_cols[-1]] / out[0] * (1 + params.time_add_buffer)) + 1

    return out


def store_compset_params(module, compute_table_cols):
    storeparams = [Output({'component': 'store_compset', 'module': module}, 'data'),
                   [Input({'component': 'input_' + col, 'module': module}, 'value') for col in compute_table_cols]
                   ]
    return storeparams


def store_compute_settings(*inputs):
    """
    Updates the store of  `compute_table_cols` values when changes of input parameters occur.

    :param list inputs: Input values from "compute_table_cols"
    :return: Store of all values in "compute_table_cols"
    :rtype: list
    """
    storage = dict()

    in_labels, in_values = hf.input_components()

    for input_idx, label in enumerate(in_labels):
        storage[label] = in_values[input_idx]

    return [storage]


def compset_params(module, tp_dd_module, status_table_cols):
    # Update directory and compute settings from stack selection

    stackoutput = []

    tablefields = [Output({'component': 't_' + col, 'module': module}, 'children') for col in status_table_cols]
    compute_tablefields = [Output({'component': 'factors', 'module': module}, 'data')]

    stackoutput.extend(tablefields)
    stackoutput.extend(compute_tablefields)

    outparams = [*stackoutput,
                 Input({'component': 'tp_dd', 'module': tp_dd_module}, 'value'),
                 Input({'component': 'store_tpmatchtime', 'module': module}, 'data'),
                 Input({'component': 'input_Num_CPUs', 'module': module}, 'value'),
                 State({'component': 'stack_dd', 'module': tp_dd_module}, 'value'),
                 State({'component': 'store_allstacks', 'module': tp_dd_module}, 'data'),
                 State({'component': 'status_table_cols', 'module': module}, 'data'),
                 State('url', 'pathname')
                 ]
    return outparams


def all_compset_callbacks(label, compute_table_cols):
    # update callback

    u_cs_params = update_compset_params(label, compute_table_cols)

    @app.callback(u_cs_params,
                  prevent_initial_call=True)
    def sift_pointmatch_update_comp_settings(*args):
        hf.is_url_active(args[-1])
        return update_compute_settings(*args)

    # store callback

    st_cs_params = store_compset_params(label, compute_table_cols)

    @app.callback(st_cs_params,
                  prevent_initial_call=True)
    def sift_pointmatch_store_comp_settings(*args):
        return store_compute_settings(*args)

    # hide compute settings if local execution is chosen

    @app.callback(Output({'component': 'comp_set_detail', 'module': label}, 'style'),
                  Input({'component': 'compute_sel', 'module': label}, 'value'))
    def compset_switch(compsel):

        if 'local' in compsel:
            return {'display': 'none'}
        else:
            return {}
