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

# import sys
import glob
import numpy as np
import os
import json
import requests

from dashUI import params

from dashUI.utils import pages, launch_jobs
from dashUI.utils import helper_functions as hf

# element prefix
label = "finalize_BDV"
parent = "finalize"

store = pages.init_store({}, label)

page1 = [html.Br(), html.Div(store), html.Div(pages.render_selector(label, show=False))]

page2 = []

# select output volume


page3 = html.Div([html.H4("Choose exported volume"),
                  dcc.Dropdown(id=label + '_input_dd')
                  ])

page1.append(page3)

# =============================================
# Start Button

gobutton = html.Div(children=[html.Br(),
                              html.Button('Start Format conversion',
                                          id={'component': 'go', 'module': label}, disabled=True),
                              html.Div(id={'component': 'buttondiv', 'module': label}),
                              html.Br(),
                              pages.compute_loc(label, c_options=['standalone'], c_default='standalone')
                              ]
                    )

page2.append(gobutton)

# # =============================================
# # PROGRESS OUTPUT


collapse_stdout = pages.log_output(label)

# ----------------

# Full page layout:


page2.append(collapse_stdout)


# Volume selection list callback

# =============================================


@callback([Output(label + '_input_dd', 'options'),
           Output(label + '_input_dd', 'value')],
          [Input({'component': 'subpage_dd', 'module': parent}, 'value'),
           Input('url', 'pathname')],
          prevent_initial_call=True)
def bdv_finalize_volume_dd(dd_in, thispage):
    thispage = thispage.lstrip('/')

    if thispage not in label:
        raise PreventUpdate

    # if not dash.callback_context.triggered: 
    #     raise PreventUpdate

    expjson_list = glob.glob(os.path.join(params.json_run_dir, '*export_' + params.user + '*'))

    if expjson_list == []:
        raise PreventUpdate

    dts = []

    dd_options = list(dict())

    for jsonfile in expjson_list:
        with open(jsonfile, 'r') as f:
            export_json = json.load(f)

        datetime = jsonfile.split(params.user + '_')[1].strip('.json')

        if '--n5Path' not in export_json.keys():
            continue

        dts.append(datetime)
        vfile = export_json['--n5Path']
        vdescr = ' - '.join([export_json['--project'],
                             export_json['--stack'],
                             datetime,
                             vfile.split('_')[-1].split('.')[0]])

        dd_options.append({'label': vdescr, 'value': jsonfile})

    if dts == []:
        raise PreventUpdate

    latest = dd_options[np.argsort(dts)[-1]]['value']

    return dd_options, latest


# =============================================

#  LAUNCH CALLBACK FUNCTION

# =============================================


@callback([Output({'component': 'go', 'module': label}, 'disabled'),
           Output({'component': 'buttondiv', 'module': label}, 'children'),
           Output({'component': 'store_launch_status', 'module': label}, 'data')
           # Output({'component': 'store_render_launch', 'module': label},'data'),
           ],
          [Input({'component': 'go', 'module': label}, 'n_clicks'),
           Input(label + '_input_dd', 'value')],
          State({'component': 'store_launch_status', 'module': parent}, 'data'),
          )
def bdv_finalize_execute_gobutton(click, jsonfile, launch_store):
    if not dash.callback_context.triggered:
        raise PreventUpdate

    if jsonfile is None:
        raise PreventUpdate

    if launch_store in [None, '']:
        launch_store = dict()

    run_prefix = launch_jobs.run_prefix()

    with open(jsonfile, 'r') as f:
        export_json = json.load(f)

    n5file = export_json['--n5Path']
    owner = export_json['--owner']
    project = export_json['--project']
    stack = export_json['--stack']

    if not os.path.exists(n5file):
        return True, 'Input data file does not exist.', dash.no_update

    if not os.access(n5file, os.W_OK | os.X_OK):
        return True, 'Output directory not writable!', dash.no_update

    trigger = hf.trigger()

    if 'input' in trigger:
        return False, '', dash.no_update

    # get stack parameters from render server
    url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack

    stackparams = requests.get(url).json()

    res = [stackparams['currentVersion']['stackResolutionZ'], stackparams['currentVersion']['stackResolutionX'],
           stackparams['currentVersion']['stackResolutionY']]

    run_params = dict()

    run_params['path'] = n5file
    # run_params["scale_factors"] = 3 * [[2, 2, 2]],
    run_params["resolution"] = res
    run_params["unit"] = 'nanometer'

    param_file = params.json_run_dir + '/' + label + '_' + run_prefix + '.json'

    with open(param_file, 'w') as f:
        json.dump(run_params, f, indent=4)

    log_file = params.render_log_dir + '/' + label + '_' + run_prefix
    err_file = log_file + '.err'
    log_file += '.log'

    mkxml_p = launch_jobs.run(target='standalone', pyscript=params.rendermodules_dir + '/materialize/make_xml.py',
                              jsonfile=param_file,
                              logfile=log_file, errfile=err_file)

    launch_store['status'] = 'launch'
    launch_store['id'] = mkxml_p
    launch_store['type'] = 'standalone'
    launch_store['logfile'] = log_file

    return True, '', launch_store
