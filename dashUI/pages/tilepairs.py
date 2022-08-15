#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 16:15:27 2020

@author: schorb
"""
import dash
from dash import dcc, callback
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import json
import os

from dashUI.pages.side_bar import sidebar

from dashUI import params
from dashUI.utils import launch_jobs, pages
from dashUI.utils import helper_functions as hf
from dashUI.callbacks import render_selector

module = 'tilepairs'
dash.register_page(__name__,
                   name='Find Tile Pairs')


storeinit = {}
store = pages.init_store(storeinit, module)

store.append(dcc.Store(id={'component': 'runstep', 'module': module}, data='generate'))

main = html.Div(id={'component': 'main', 'module': module}, children=html.H3("Generate TilePairs for Render stack"))

page = [main]

# # ===============================================
#  RENDER STACK SELECTOR

# Pre-fill render stack selection from previous module

us_out, us_in, us_state = render_selector.init_update_store(module, 'convert')


@callback(us_out, us_in, us_state,
          prevent_initial_call=True)
def tilepairs_update_store(*args):
    thispage = args[-1]
    args = args[:-1]
    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    return render_selector.update_store(*args)


page1 = pages.render_selector(module)

page.append(page1)

# # # ===============================================


page2 = html.Div(id={'component': 'page2', 'module': module},
                 children=[html.H4('Pair assignment mode'),
                           html.Div([dcc.RadioItems(options=[
                               {'label': '2D (tiles in montage/mosaic)', 'value': '2D'},
                               {'label': '3D (across sections)', 'value': '3D'}],
                               value='2D',
                               id={'component': 'pairmode', 'module': module}),
                           ],
                               style={'display': 'inline,block'}),
                           html.Br(),
                           pages.substack_sel(module)
                           ])

page.append(page2)


# # ===============================================

@callback([Output({'component': 'page2', 'module': module}, 'style'),
           Output({'component': 'multi-run', 'module': module}, 'style'),
           Output({'component': 'pairmode', 'module': module}, 'value')],
          Input({'component': 'owner_dd', 'module': module}, 'value'),
          prevent_initial_call=True)
def stack2Donly(owner):
    """
    Toggles visibility of the slice selectors.

    :param str owner: The Render owner
    :return: CSS display mode, '2D
    :rtype: dict
    """
    style1 = {}
    style2 = {'display': 'none'}
    val = '2D'
    if owner in ['SerialEM']:
        style1 = {'display': 'none'}
        style2 = {}

    return style1, style2, val


@callback([Output({'component': '3Dslices', 'module': module}, 'style'),
           Output({'component': 'sec_input1', 'module': module}, 'value')],
          Input({'component': 'pairmode', 'module': module}, 'value'),
          prevent_initial_call=True)
def tilepairs_3D_status(pairmode):
    """
    Toggles visibility of the 3D parameter selectors.

    :param str pairmode: The choice of mode dimensionality. "sec_input1"
    :return: CSS display mode
    :rtype: dict
    """

    if pairmode == '2D':
        style = {'display': 'none'}
        val = 0
    elif pairmode == '3D':
        style = {'display': 'block'}
        val = 1
    return style, val


# optional bundle multi-stack import from SerialEM


page3 = html.Div(id={'component': 'multi-run', 'module': module},
                 children=[html.H4('Process all stacks from this data import (multiple nav items)?'),
                           html.Div([dcc.Checklist(options=[
                               {'label': 'process all nav items', 'value': 'multi'}],
                               id={'component': 'multi-nav', 'module': module}),
                           ],
                               style={'display': 'inline,block'}),
                           html.Br()
                           ])

page.append(page3)

# =============================================
# Start Button


gobutton = html.Div(children=[html.Br(),
                              html.Button('Start TilePair generation',
                                          id={'component': 'go', 'module': module}),
                              html.Br(),
                              pages.compute_loc(module),
                              html.Br(),
                              html.Div(id={'component': 'run_state', 'module': module}, style={'display': 'none'},
                                       children='wait')])

page.append(gobutton)


@callback([Output({'component': 'go', 'module': module}, 'disabled'),
           Output({'component': 'store_launch_status', 'module': module}, 'data'),
           Output({'component': 'store_render_launch', 'module': module}, 'data')],
          [Input({'component': 'go', 'module': module}, 'n_clicks'),
           Input({'component': 'pairmode', 'module': module}, 'value'),
           Input({'component': 'stack_dd', 'module': module}, 'value')],
          [State({'component': 'sec_input1', 'module': module}, 'value'),
           State({'component': 'compute_sel', 'module': module}, 'value'),
           State({'component': 'startsection', 'module': module}, 'value'),
           State({'component': 'endsection', 'module': module}, 'value'),
           State({'component': 'store_owner', 'module': module}, 'data'),
           State({'component': 'store_project', 'module': module}, 'data'),
           State({'component': 'multi-nav', 'module': module}, 'value'),
           State({'component': 'stack_dd', 'module': module}, 'options')],
          prevent_initial_call=True)
def tilepairs_execute_gobutton(click, pairmode, stack, slicedepth, comp_sel, startsection, endsection, owner, project,
                               multi, stacklist):
    if click is None:
        return dash.no_update

    trigger = hf.trigger()

    if 'go' not in trigger:
        return False, dash.no_update, dash.no_update

    # prepare parameters:
    run_prefix = launch_jobs.run_prefix()

    run_params = params.render_json.copy()
    run_params['render']['owner'] = owner
    run_params['render']['project'] = project

    with open(os.path.join(params.json_template_dir, 'tilepairs.json'), 'r') as f:
        run_params.update(json.load(f))

    run_params['minZ'] = startsection
    run_params['maxZ'] = endsection

    tilepairdir = params.json_run_dir + '/tilepairs_' + run_prefix + '_' + stack + '_' + pairmode

    if multi in [None, []]:
        param_file = generate_run_params(run_params, owner, stack,
                                         run_prefix, pairmode, slicedepth)
    else:
        #     prepare multiple runs
        param_file = []
        stackprefix = stack.split('_nav_')[0]

        for stackoption in stacklist:
            if stackprefix in stackoption['value'] and stackoption['value'][-1].isnumeric():
                currentstack = stackoption['value']

                param_file_current = generate_run_params(run_params, owner, currentstack,
                                                         run_prefix, pairmode, slicedepth)

                param_file.append(param_file_current)

    log_file = params.render_log_dir + '/' + module + '_' + run_prefix + '_' + pairmode
    err_file = log_file + '.err'
    log_file += '.log'

    tilepairs_generate_p = launch_jobs.run(target=comp_sel,
                                           pyscript=params.asap_dir + '/pointmatch/create_tilepairs.py',
                                           jsonfile=param_file,
                                           run_args=None, target_args=None,
                                           logfile=log_file, errfile=err_file)

    launch_store = dict()
    launch_store['logfile'] = log_file
    launch_store['status'] = 'launch'
    launch_store['id'] = tilepairs_generate_p
    launch_store['type'] = launch_jobs.runtype(comp_sel)

    outstore = dict()
    outstore['owner'] = owner
    outstore['project'] = project
    outstore['stack'] = stack
    outstore['tilepairdir'] = tilepairdir

    return True, launch_store, outstore


def generate_run_params(run_params, owner, stack, run_prefix, pairmode, slicedepth):
    run_params_generate = run_params.copy()

    # generate script call...

    tilepairdir = params.json_run_dir + '/tilepairs_' + run_prefix + '_' + stack + '_' + pairmode

    if not os.path.exists(tilepairdir):
        os.makedirs(tilepairdir)

    if pairmode == '2D':
        run_params_generate['zNeighborDistance'] = 0
        run_params_generate['excludeSameLayerNeighbors'] = 'False'

    elif pairmode == '3D':
        run_params_generate['zNeighborDistance'] = slicedepth
        run_params_generate['excludeSameLayerNeighbors'] = 'True'

        if owner == 'SBEM':
            run_params_generate["xyNeighborFactor"] = 0.2

    run_params_generate['stack'] = stack
    run_params_generate['output_dir'] = tilepairdir
    run_params_generate['output_json'] = tilepairdir + '/tiles_' + pairmode

    param_file = params.json_run_dir + '/' + module + '_' + run_prefix + '_' + stack + '_' + pairmode + '.json'

    with open(param_file, 'w') as f:
        json.dump(run_params_generate, f, indent=4)

    return param_file


# =============================================
# Processing status

# initialized with store
# embedded from callbacks import runstate

# # =============================================
# # PROGRESS OUTPUT


collapse_stdout = pages.log_output(module)

# ----------------

# Full page layout:


page.append(collapse_stdout)
page.extend(store)


def layout():
    return [sidebar(),html.Div(page, className='main')]