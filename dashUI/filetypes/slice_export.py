#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""

import dash
from dash import dcc
from dash import html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

# import sys
import numpy as np
import os
import json
import requests
import importlib

from app import app
import params

from utils import pages, launch_jobs
from utils import helper_functions as hf
from utils.checks import is_bad_filename

# element prefix
label = "export_slices"
parent = "export"

store = pages.init_store({}, label)

status_table_cols = ['stack',
                     'slices',
                     'Gigapixels']

compute_table_cols = [#'Num_CPUs',
                      'Num_parallel_jobs',
                      'runtime_minutes']

page1 = [html.Br(), pages.render_selector(label, show=False), html.Div(children=store)]

# =============================================
# select file type

filetypesel = html.Div([html.H4("Choose output file type."),
                  dcc.Dropdown(id={'component': 'filetype_dd', 'module': label},
                               persistence=True,
                               className='dropdown_inline',
                               options=['jpg','png','tif'],
                               value='jpg'),
                  html.Br()
                  ])

page1.append(filetypesel)

# =============================================
# select file type

scalesel = html.Div([html.H4("Choose output scale."),
                  dcc.Input(id={'component': 'scale_input', 'module': label},
                            persistence=True,
                            className='dropdown_inline',
                            type='number',
                            step=0.001,
                            min=0,max=1,
                            value='0.5'),
                  html.Br(),
                  html.Br()
                  ])

page1.append(scalesel)





# # ===============================================
# Compute Settings

compute_settings = html.Details(children=[html.Summary('Compute settings:'),
                                             html.Table([html.Tr([html.Th(col) for col in status_table_cols]),
                                                  html.Tr([html.Td('',id={'component': 't_'+col, 'module': label}) for col in status_table_cols])
                                             ],className='table'),
                                             html.Br(),
                                             html.Table([html.Tr([html.Th(col) for col in compute_table_cols]),
                                                  html.Tr([html.Td(dcc.Input(id={'component': 'input_'+col, 'module': label},type='number',min=1)) for col in compute_table_cols])
                                             ],className='table'),
                                             dcc.Store(id={'component': 'factors', 'module': label},data={}),
                                             dcc.Store(id={'component':'store_compset','module':label})
                                             ],id={'component':'computesettings','module':label})
page1.append(compute_settings)


# callbacks

@app.callback([Output({'component': 'input_' + col, 'module': label}, 'value') for col in compute_table_cols],
              [Output({'component': 'factors', 'module': label}, 'modified_timestamp'),
               Output({'component': 'computesettings', 'module': label}, 'style')],
              [Input({'component': 'input_' + col, 'module': label}, 'value') for col in compute_table_cols],
              [Input({'component': 'factors', 'module': label}, 'modified_timestamp'),
               Input({'component': 'compute_sel', 'module': label}, 'value')],
              [State({'component': 'factors', 'module': label}, 'data'),
               State('url', 'pathname')]
    , prevent_initial_call=True)
def slice_export_update_compute_settings(*inputs):
    thispage = inputs[-1]
    inputs = inputs[:-1]
    compsel = inputs[-2]

    thispage = thispage.lstrip('/')

    if thispage == '' or not thispage in hf.trigger(key='module'):
        raise PreventUpdate

    idx_offset = len(compute_table_cols)

    trigger = hf.trigger()



    out = list(inputs[:idx_offset])
    out.append(dash.no_update)
    out.append({})

    if compsel=='standalone':
        out[0] = 1
        out[-1] = {'display':'none'}
        return out

    if not trigger in ('factors', 'input_' + compute_table_cols[0]):
        out[0] = params.n_jobs_default
        return out

    if inputs[0] is None:
        out[0] = params.n_jobs_default
    else:
        out[0] = inputs[0]



    if type(inputs[1]) in (str, type(None)) or inputs[1] == {}:
        out[1] = 120
    else:
        if None in inputs[-1].values():
            out[1] = dash.no_update
        else:
            out[1] = np.ceil(inputs[-1][compute_table_cols[-1]] / out[0] * (1 + params.time_add_buffer)) + 1

    return out


@app.callback(Output({'component': 'store_compset', 'module': label}, 'data'),
              [Input({'component': 'input_' + col, 'module': label}, 'value') for col in compute_table_cols],
              prevent_initial_call=True)
def slice_export_store_compute_settings(*inputs):
    storage = dict()

    in_labels, in_values = hf.input_components()

    for input_idx, label in enumerate(in_labels):
        storage[label] = in_values[input_idx]

    return storage


# Update directory and compute settings from stack selection


bbox0 = []

for dim in ['X', 'Y', 'Z']:
    bbox0.append(Input({'component': 'start' + dim, 'module': parent}, 'value'))
    bbox0.append(Input({'component': 'end' + dim, 'module': parent}, 'value'))

stackinput = []  # Input({'component': 'stack_dd', 'module': parent},'value')]
stackinput.extend(bbox0)
stackinput.append(Input({'component': "path_input", 'module': parent}, 'n_blur'))
stackinput.append(Input({'component': "scale_input", 'module': label}, 'value'))
stackoutput = [  # Output({'component': 'path_ext', 'module': parent},'data'),
    # Output({'component': 'store_stackparams', 'module': module}, 'data')
]
tablefields = [Output({'component': 't_' + col, 'module': label}, 'children') for col in status_table_cols]
compute_tablefields = [Output({'component': 'factors', 'module': label}, 'data')]

stackoutput.extend(tablefields)

stackoutput.extend(compute_tablefields)


@app.callback(stackoutput,
              stackinput,
              [State({'component': 'store_owner', 'module': parent}, 'data'),
               State({'component': 'store_project', 'module': parent}, 'data'),
               State({'component': 'stack_dd', 'module': parent}, 'value'),
               State({'component': 'store_allstacks', 'module': parent}, 'data'),
               State({'component': "path_input", 'module': parent}, 'value'),
               State('url', 'pathname')]
    , prevent_initial_call=True)
def slice_export_stacktoparams(  # stack_sel,
        xmin, xmax, ymin, ymax, zmin, zmax,
        browsetrig,
        scale,
        owner, project, stack_sel, allstacks,
        browsedir,
        thispage):
    thispage = thispage.lstrip('/')

    if thispage == '' or not thispage in hf.trigger(key='module'):
        raise PreventUpdate

    out = dict()
    factors = dict()

    t_fields = [''] * len(status_table_cols)
    # ct_fields = [1]*len(compute_table_cols)

    if (not stack_sel == '-') and (not allstacks is None):
        stacklist = [stack for stack in allstacks if stack['stackId']['stack'] == stack_sel]
        stack = stack_sel

        if not stacklist == []:
            stackparams = stacklist[0]

            if 'None' in (stackparams['stackId']['owner'], stackparams['stackId']['project']):
                return dash.no_update

            out['zmin'] = zmin
            out['zmax'] = zmax
            out['numsections'] = zmax - zmin + 1

            url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack + '/z/' + str(
                out['zmin']) + '/render-parameters'

            tiles0 = requests.get(url).json()

            tilefile0 = os.path.abspath(tiles0['tileSpecs'][0]['mipmapLevels']['0']['imageUrl'].strip('file:'))
            #
            # basedirsep = params.datasubdirs[owner]
            # dir_out = tilefile0[:tilefile0.find(basedirsep)]

            out['Gigapixels'] = out['numsections'] * (xmax - xmin) * (ymax - ymin) / (10 ** 9)

            t_fields = [stack, str(out['numsections']), '%0.2f' % int(out['Gigapixels'])]

            timelim = np.ceil(out['Gigapixels'] * float(scale) * params.export['min/GPix/CPU_slice'] / params.n_cpu_script * (1 + params.time_add_buffer)) + 1

            factors = {'runtime_minutes': timelim}

    outlist = []  # dir_out] #,out]
    outlist.extend(t_fields)
    outlist.append(factors)

    return outlist


# =============================================
# Start Button

gobutton = html.Div(children=[html.Br(),
                              html.Button('Start Export',
                                          id={'component': 'go', 'module': label}, disabled=True),
                              html.Div(id={'component': 'buttondiv', 'module': label}),
                              html.Br(),
                              pages.compute_loc(label, c_default='slurm'),
                              html.Br(),
                              html.Div(id={'component': 'run_state', 'module': label}, style={'display': 'none'},
                                       children='wait')])

page1.append(gobutton)

# =============================================

#  LAUNCH CALLBACK FUNCTION

# =============================================


bbox = []

for dim in ['X', 'Y', 'Z']:
    bbox.append(State({'component': 'start' + dim, 'module': parent}, 'value'))
    bbox.append(State({'component': 'end' + dim, 'module': parent}, 'value'))

states = [State({'component': 'compute_sel', 'module': label}, 'value'),
          State({'component': 'store_owner', 'module': parent}, 'data'),
          State({'component': 'store_project', 'module': parent}, 'data')]

states.extend(bbox)
states.append(State({'component': 'store_stackparams', 'module': parent}, 'data'))
states.append(State({'component': 'sliceim_section_in_0', 'module': parent}, 'value'))
states.append(State({'component': 'sliceim_contrastslider_0', 'module': parent}, 'value'))
states.append(State({'component': 'scale_input', 'module': label}, 'value'))

@app.callback([Output({'component': 'go', 'module': label}, 'disabled'),
               Output({'component': 'buttondiv', 'module': label}, 'children'),
               Output({'component': 'store_launch_status', 'module': label}, 'data'),
               Output({'component': 'store_render_launch', 'module': label}, 'data')],
              [Input({'component': 'go', 'module': label}, 'n_clicks'),
               Input({'component': "path_input", 'module': parent}, 'value'),
               Input({'component': 'stack_dd', 'module': parent}, 'value'),
               Input({'component': 'input_Num_parallel_jobs', 'module': label},'value'),
               Input({'component': 'input_runtime_minutes', 'module': label},'value')],
              states
    , prevent_initial_call=True)
def sliceexport_execute_gobutton(click, outdir, stack,
                                 numjobs,timelim,
                                 comp_sel, owner, project,
                                 Xmin, Xmax, Ymin, Ymax, Zmin, Zmax,
                                 sp_store, slice_in, c_limits,scale):
    if not dash.callback_context.triggered:
        raise PreventUpdate

    if None in [outdir, stack, comp_sel, owner, project, Xmin, Xmax, Ymin, Ymax, Zmin, Zmax,
                sp_store, slice_in]:
        raise PreventUpdate

    trigger = hf.trigger()

    # stackparams = sp_store['stackparams']

    outstore = dict()
    outstore['owner'] = owner
    outstore['project'] = project
    outstore['stack'] = stack

    if 'go' in trigger:
        if click is None: return dash.no_update

        # prepare parameters:
        run_prefix = launch_jobs.run_prefix()

        run_params = params.render_json.copy()
        run_params['render']['owner'] = owner
        run_params['render']['project'] = project

        run_params_generate = run_params.copy()

        param_file = params.json_run_dir + '/' + parent + '_' + run_prefix


        # create output directory
        aldir = os.path.join(outdir, params.outdirbase)

        if not os.path.isdir(aldir):
            os.makedirs(aldir)

        slicerun_p = dict()

        bounds = dict()

        for dim in ['X', 'Y']:
            bounds['min' + dim] = eval(dim + 'min')
            bounds['max' + dim] = eval(dim + 'max') + 1

        slicerun_p['minZ'] = Zmin
        slicerun_p['maxZ'] = Zmax

        # contrast limits

        slicerun_p['minInt'] = c_limits[0]
        slicerun_p['maxInt'] = c_limits[1]

        slicerun_p['scale'] = scale

        if comp_sel == 'standalone':
            run_params = slicerun_p.copy()
            run_args = None

            pfile = param_file + '.json'

            with open(param_file, 'w') as f:
                json.dump(run_params, f, indent=4)

        else:
            run_args=dict()
            slicerun_p['pool_size'] = params.n_cpu_script

            # compute memory req.

            mem = np.ceil((bounds['maxX']-bounds['minX'])*(bounds['maxY']-bounds['minY']) * 3 / 1e9) # in GB

            # parallelize calls

            steps = range(Zmin-1,Zmax,int(np.ceil((Zmax-Zmin)/numjobs+1)))
            pfile=[]

            for idx,step in enumerate(steps[:-1]):
                thisrun = slicerun_p.copy()
                thisrun['minZ'] = step
                thisrun['maxZ'] = steps[idx+1]

                thispfile = param_file + '_' + str(idx) + '.json'

                with open(thispfile, 'w') as f:
                    json.dump(run_params, f, indent=4)

                pfile.append(thispfile)

            if comp_sel =='slurm':
                target_args['--mem'] = str(mem) +'G'
                target_args_args['--time'] = '00:' + str(timelim) + ':00'
                target_args_args['--nodes'] = 1
                target_args_args['--tasks-per-node'] = 1
                target_args_args['--cpus-per-task'] = params.n_cpu_script


        # generate script call...


        run_prefix = launch_jobs.run_prefix()

        log_file = params.render_log_dir + '/' + parent + '_' + run_prefix
        err_file = log_file + '.err'
        log_file += '.log'

        sliceexport_p = launch_jobs.run(target=comp_sel,
                                     pyscript=params.rendermodules_dir+'/materialize/render_export_sections.py',
                                     jsonfile=pfile,
                                     target_args_args=target_args_args,
                                     logfile=log_file, errfile=err_file)

        launch_store = dict()
        launch_store['logfile'] = log_file
        launch_store['status'] = 'running'
        launch_store['id'] = sliceexport_p
        launch_store['type'] = comp_sel

        return True, '', launch_store, outstore

    else:
        if outdir == '':
            return True, 'No output directory selected!', dash.no_update, outstore

        elif is_bad_filename(outdir):
            return True, 'Wrong characters in input directory path. Please fix!', dash.no_update, outstore

        if not os.access(outdir, os.W_OK | os.X_OK):
            return True, 'Output directory not writable!', dash.no_update, outstore

        else:
            return False, '', dash.no_update, outstore








# =============================================
# Processing status

# initialized with store
# embedded from callbacks import runstate

# # =============================================
# # PROGRESS OUTPUT
page2 = []

collapse_stdout = pages.log_output(label)

# ----------------

# Full page layout:


page2.append(collapse_stdout)