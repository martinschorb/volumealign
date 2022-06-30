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
    params = [[Output({'component': 'input_' + col, 'module': module}, 'value') for col in compute_table_cols],
              [Output({'component': 'factors', 'module': module}, 'modified_timestamp')],
              [Input({'component': 'input_' + col, 'module': module}, 'value') for col in compute_table_cols],
              [Input({'component': 'factors', 'module': module}, 'modified_timestamp')],
              [State({'component': 'factors', 'module': module}, 'data'),
               State({'component': 'compute_table_cols', 'module': module}, 'data'),
               State('url', 'pathname')]
              ]

    return params


def update_compute_settings(*inputs):
    """
    Calculates the dynamic fields of `compute_table_cols` when changes of its input parameters occur.

    :param (list, dict, str) inputs: [:-4] Input values from "compute_table_cols"<Br>
                                     [-4] trigger timestamp <Br>
                                     [-3] compute_table_cols: column names<Br>
                                     [-2] factors: factors to multiply the input values with.<Br>
                                     [-1] thispage: current page URL
    :return: factors that update compute_table_cols values when they are changed themselves.
    :rtype: (list, int)
    """

    thispage = inputs[-1]
    inputs = inputs[:-1]
    thispage = thispage.lstrip('/')
    compute_table_cols = inputs[-3]

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
    :rtype: dict
    """
    storage = dict()

    in_labels, in_values = hf.input_components()

    for input_idx, label in enumerate(in_labels):
        storage[label] = in_values[input_idx]

    return storage


def compset_params(module, tp_dd_module, status_table_cols):
    # Update directory and compute settings from stack selection

    stackoutput = []

    tablefields = [Output({'component': 't_' + col, 'module': module}, 'children') for col in status_table_cols]
    compute_tablefields = [Output({'component': 'factors', 'module': module}, 'data')]

    stackoutput.extend(tablefields)
    stackoutput.extend(compute_tablefields)

    outparams = [stackoutput,
                 [Input({'component': 'tp_dd', 'module': tp_dd_module}, 'value'),
                  Input({'component': 'store_tpmatchtime', 'module': module}, 'data'),
                  Input({'component': 'input_Num_CPUs', 'module': module}, 'value')],
                 [State({'component': 'stack_dd', 'module': module}, 'value'),
                  State({'component': 'store_allstacks', 'module': module}, 'data'),
                  State({'component': 'status_table_cols', 'module': module}, 'data'),
                  State('url', 'pathname')]
                 ]
    return outparams


def comp_set(tilepairdir, matchtime, n_cpu, stack_sel, allstacks, status_table_cols, thispage):
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


def all_compset_callbacks(label, tp_dd_module, compute_table_cols, status_table_cols):
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
        hf.is_url_active(args[-1])
        return store_compute_settings(*args)

    # comp_settings callback

    cs_params = compset_params(label, tp_dd_module, status_table_cols)

    @app.callback(cs_params,
                  prevent_initial_call=True)
    def sift_pointmatch_comp_settings(*args):
        hf.is_url_active(args[-1])
        return comp_set(*args)
