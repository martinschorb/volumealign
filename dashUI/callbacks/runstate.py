#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 14:50:48 2021

@author: schorb
"""
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash
from dash import html, callback
from dash.exceptions import PreventUpdate

import subprocess
import os

from dashUI import params
from dashUI.utils import launch_jobs
from dashUI.utils import helper_functions as hf

static_states = ['done', 'cancelled', 'error', 'input', 'wait', 'timeout']


#  =================================================


@callback([Output({'component': 'store_r_status', 'module': MATCH}, 'data'),
           Output({'component': 'statuspage_div', 'module': MATCH}, 'style'),
           Output({'component': 'statuspage_link', 'module': MATCH}, 'href')],
          [Input('interval1', 'n_intervals'),
           Input({'component': 'cancel', 'module': MATCH}, 'n_clicks')],
          [State({'component': 'store_run_status', 'module': MATCH}, 'data'),
           State({'component': 'outfile', 'module': MATCH}, 'children'),
           State({'component': 'name', 'module': MATCH}, 'data'),
           State('url', 'pathname')],
          prevent_initial_call=True)
def update_status(n, click, run_state, logfile, module, thispage):
    if not dash.callback_context.triggered:
        raise PreventUpdate
    #
    # print('status update initiated')

    if None in [n, run_state, logfile, module, thispage]:
        raise PreventUpdate
    #
    # if run_state['status'] in static_states:
    #     raise PreventUpdate

    status_href = ''
    status_style = {'display': 'none'}

    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    trigger = hf.trigger()

    r_status = run_state.copy()

    r_status['logfile'] = logfile

    if 'interval1' in trigger:
        link = ''

        if run_state['id'] is None:
            if run_state['status'] not in ['input', 'wait']:
                r_status['status'] = 'input'
            return r_status, status_style, status_href

        if run_state['type'] is not None:
            (r_status['status'], link, run_state1) = launch_jobs.status(run_state)
            r_status['logfile'] = run_state1['logfile']

        if not link == '':

            status_href = link.split('__')[-1]
            # r_status['status'] = r_status['status'].split('__')[0]
            status_href = 'http://' + status_href

            if 'Problem' not in r_status['status']:
                if 'Startup' in r_status['status']:
                    status_href += ':' + params.spark_port
                else:
                    status_href += ':' + params.spark_job_port

                status_style = {}

        if 'Error' in r_status['status']:
            if logfile.endswith('.log'):
                r_status['logfile'] = logfile[:logfile.rfind('.log')] + '.err'

        # print('update_status:', r_status)

        return r_status, status_style, status_href

    elif 'cancel' in trigger:

        r_status['status'] = launch_jobs.canceljobs(run_state)

        return r_status, status_style, status_href

    else:
        return dash.no_update


#  =================================================


@callback([Output({'component': 'get-status', 'module': MATCH}, 'children'),
           Output({'component': 'get-status', 'module': MATCH}, 'style'),
           Output({'component': 'cancel', 'module': MATCH}, 'style')],
          Input({'component': 'store_run_status', 'module': MATCH}, 'data'),
          [State({'component': 'name', 'module': MATCH}, 'data'),
           State('url', 'pathname')],
          prevent_initial_call=True)
def get_status(run_state, module, thispage):
    if not dash.callback_context.triggered:
        raise PreventUpdate

    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    status_style = {"font-family": "Courier New", 'color': '#000'}
    # procs=params.processes[module.strip('_')] 

    c_button_style = {'display': 'none'}
    if 'running' in run_state['status']:
        status = html.Div([html.Img(src='assets/gears.gif', height=72), html.Br(), 'running'])
        if run_state['type'] not in ['standalone', 'generic']:
            c_button_style = {}
        status_style = {'color': '#07E'}
    elif run_state['status'] == 'input':
        status = 'process will start on click.'
    elif run_state['status'] == 'done':
        status = 'DONE'
        status_style = {'color': '#0D0'}
    elif run_state['status'] == 'pending':
        c_button_style = {}
        status = ['Waiting for cluster resources to be allocated.']
    elif run_state['status'] == 'wait':
        status = 'not running'
    else:
        status = run_state['status']

    # print('display status:  '+str(status))

    return status, status_style, c_button_style


# #  =================================================


@callback(Output({'component': 'console-out', 'module': MATCH}, 'value'),
          [Input('interval1', 'n_intervals'),
           Input({'component': 'outfile', 'module': MATCH}, 'children')],
          State('url', 'pathname')
          )
def update_output(n, outfile, thispage):
    if not dash.callback_context.triggered:
        raise PreventUpdate

    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    data = ''

    if outfile is not None:
        if os.path.exists(outfile):
            file = open(outfile, 'r')
            lines = file.readlines()
            if lines.__len__() <= params.disp_lines:
                last_lines = lines
            else:
                last_lines = lines[-params.disp_lines:]
            for line in last_lines:
                data = data + line
            file.close()

    return data


# #  =================================================


@callback([Output({'component': 'store_run_status', 'module': MATCH}, 'data'),
           Output({'component': 'outfile', 'module': MATCH}, 'children')],
          [Input({'component': 'store_launch_status', 'module': MATCH}, 'modified_timestamp'),
           Input({'component': 'store_r_status', 'module': MATCH}, 'modified_timestamp')],
          [State({'component': 'store_launch_status', 'module': MATCH}, 'data'),
           State({'component': 'store_r_status', 'module': MATCH}, 'data')],
          prevent_initial_call=True)
def merge_run_state(launch_trigger, status_trigger, launch_in, status_in):
    trigger = hf.trigger()

    # print('-- merge status --')
    # print(trigger)

    if 'launch' in trigger:
        # print('launch triggered state:')
        # print(launch_in)
        out = launch_in

    else:
        # print('status triggered state:')
        # print(status_in)
        out = status_in.copy()

    if out == {}:
        raise PreventUpdate

    return out, out['logfile']


@callback(Output({'component': 'donelink', 'module': MATCH}, 'style'),
          Input({'component': 'get-status', 'module': MATCH}, 'children'),
          State({'component': 'donelink_status', 'module': MATCH}, 'children'))
def show_donelink(status, expected_status):

    style = {'display': 'none'}
    if status == expected_status or status == [expected_status]:
        style = {}

    return style