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
import numpy as np
import os
import json
import requests
import importlib

from dashUI import params

from dashUI.utils import pages, launch_jobs
from dashUI.utils import helper_functions as hf
from dashUI.utils.checks import is_bad_filename

from dashUI.callbacks import runstate, comp_settings

# element prefix
label = "export_N5"
parent = "export"

store = pages.init_store({}, label)

status_table_cols = ['stack',
                     'slices',
                     'Gigapixels']

compute_table_cols = ['Num_CPUs',
                      # 'MemGB_perCPU',
                      'runtime_minutes']

compute_locations = ['sparkslurm', 'localspark', 'spark::render.embl.de']

compute_default = 'sparkslurm'

page1 = [html.Br(), pages.render_selector(label, show=False), html.Div(children=store)]

# Update directory and compute settings from stack selection

bbox0 = []

for dim in ['X', 'Y', 'Z']:
    bbox0.append(Input({'component': 'start' + dim, 'module': parent}, 'value'))
    bbox0.append(Input({'component': 'end' + dim, 'module': parent}, 'value'))

stackinput = []  # Input({'component': 'stack_dd', 'module': parent},'value')]
stackinput.extend(bbox0)
stackinput.append(Input({'component': "path_input", 'module': parent}, 'n_blur'))
stackoutput = [  # Output({'component': 'path_ext', 'module': parent},'data'),
    # Output({'component': 'store_stackparams', 'module': module}, 'data')
]
tablefields = [Output({'component': 't_' + col, 'module': label}, 'children') for col in status_table_cols]
compute_tablefields = [Output({'component': 'factors', 'module': label}, 'data')]

stackoutput.extend(tablefields)
stackoutput.extend(compute_tablefields)


@callback(stackoutput,
          stackinput,
          [State({'component': 'store_owner', 'module': parent}, 'data'),
           State({'component': 'store_project', 'module': parent}, 'data'),
           State({'component': 'stack_dd', 'module': parent}, 'value'),
           State({'component': 'store_allstacks', 'module': parent}, 'data'),
           State({'component': "path_input", 'module': parent}, 'value'),
           State('url', 'pathname')],
          prevent_initial_call=True)
def n5export_stacktoparams(  # stack_sel,
        xmin, xmax, ymin, ymax, zmin, zmax,
        browsetrig,
        owner, project, stack_sel, allstacks,
        browsedir,
        thispage):
    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    if None in [xmin, xmax, ymin, ymax, zmin, zmax]:
        raise PreventUpdate

    out = dict()
    factors = dict()

    t_fields = [''] * len(status_table_cols)
    # ct_fields = [1]*len(compute_table_cols)

    if (not stack_sel == '-') and (allstacks is not None):
        stacklist = [stack for stack in allstacks if stack['stackId']['stack'] == stack_sel]
        stack = stack_sel

        if not stacklist == []:
            stackparams = stacklist[0]

            if 'None' in (stackparams['stackId']['owner'], stackparams['stackId']['project']):
                return dash.no_update

            out['zmin'] = zmin
            out['zmax'] = zmax
            out['numsections'] = zmax - zmin + 1

            url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project \
                  + '/stack/' + stack + '/z/' + str(out['zmin']) + '/render-parameters'

            # tiles0 = requests.get(url).json()
            #
            # tilefile0 = os.path.abspath(tiles0['tileSpecs'][0]['mipmapLevels']['0']['imageUrl'].strip('file:'))
            #
            # basedirsep = params.datasubdirs[owner]
            # dir_out = tilefile0[:tilefile0.find(basedirsep)]

            out['Gigapixels'] = out['numsections'] * (xmax - xmin) * (ymax - ymin) / (10 ** 9)

            t_fields = [stack, str(out['numsections']), '%0.2f' % int(out['Gigapixels'])]

            timelim = np.ceil(out['Gigapixels'] * params.export['min/GPix/CPU_N5'] * (1 + params.time_add_buffer)) + 1

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
                              pages.compute_loc(label, c_options=compute_locations, c_default=compute_default),
                              html.Br(),
                              html.Div(id={'component': 'run_state', 'module': label}, style={'display': 'none'},
                                       children='wait')])

page1.append(gobutton)

# # ===============================================
# Compute Settings

page1.append(pages.compute_settings(label, status_table_cols, compute_table_cols))

# comp_settings callbacks

comp_settings.all_compset_callbacks(label, compute_table_cols)

# =============================================

#  LAUNCH CALLBACK FUNCTION

# =============================================

# TODO! (#1) Fix store  outputs to enable additional modules

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
states.append(State({'component': 'newdir_sel', 'module': parent}, 'value'))


@callback([Output({'component': 'go', 'module': label}, 'disabled'),
           Output({'component': 'buttondiv', 'module': label}, 'children'),
           Output({'component': 'store_launch_status', 'module': label}, 'data'),
           Output({'component': 'store_render_launch', 'module': label}, 'data')],
          [Input({'component': 'go', 'module': label}, 'n_clicks'),
           Input({'component': "path_input", 'module': parent}, 'value'),
           Input({'component': 'stack_dd', 'module': parent}, 'value'),
           Input({'component': 'input_Num_CPUs', 'module': label}, 'value'),
           Input({'component': 'input_runtime_minutes', 'module': label}, 'value')],
          states,
          prevent_initial_call=True)
def n5export_execute_gobutton(click, outdir, stack, n_cpu, timelim, comp_sel, owner, project,
                              Xmin, Xmax, Ymin, Ymax, Zmin, Zmax,
                              sp_store, slice_in, c_limits, newdir):
    if not dash.callback_context.triggered:
        raise PreventUpdate

    if None in [outdir, stack, n_cpu, timelim, comp_sel, owner, project, Xmin, Xmax, Ymin, Ymax, Zmin, Zmax,
                sp_store, slice_in]:
        raise PreventUpdate

    trigger = hf.trigger()

    # stackparams = sp_store['stackparams']

    outstore = dict()
    outstore['owner'] = owner
    outstore['project'] = project
    outstore['stack'] = stack

    if 'go' in trigger:
        if click is None:
            raise PreventUpdate

        # prepare parameters:
        run_prefix = launch_jobs.run_prefix()

        run_params = params.render_json.copy()
        run_params['render']['owner'] = owner
        run_params['render']['project'] = project

        run_params_generate = run_params.copy()

        param_file = params.json_run_dir + '/' + parent + '_' + run_prefix + '.json'

        if comp_sel == 'standalone':
            # =============================

            # TODO - STANDALONE PROCEDURE NOT TESTED !!!!

            # =============================

            return dash.no_update

        elif 'spark' in comp_sel:
            spsl_p = dict()

            spsl_p['--baseDataUrl'] = params.render_base_url + params.render_version.rstrip('/')
            spsl_p['--owner'] = owner
            spsl_p['--stack'] = stack
            spsl_p['--project'] = project

            # create output directory 
            aldir = os.path.join(outdir, params.outdirbase)

            if not os.path.isdir(aldir):
                os.makedirs(aldir)

            n5dir = launch_jobs.run_prefix(nouser=True)

            n5dir = os.path.join(aldir, n5dir)

            slices = ''

            if Zmin == sp_store['zmin'] and Zmax == sp_store['zmax']:
                slices = '_full'
            else:
                slices = '_Z' + str(Zmin) + '-' + str(Zmax)

            n5dir += '/' + stack + slices + '.n5'

            n5run_p = dict()

            with open(os.path.join(params.json_template_dir, 'n5export.json'), 'r') as f:
                n5run_p.update(json.load(f))

            n5run_p['--n5Path'] = n5dir

            # get tile size from single tile

            url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project \
                  + '/stack/' + stack
            url += '/z/' + str(slice_in) + '/tile-specs'

            tilespecs = requests.get(url).json()

            blocksize = list(map(int, n5run_p['--blockSize'].split(',')))
            factors = list(map(int, n5run_p['--factors'].split(',')))

            for idx, dim in enumerate(['X', 'Y', 'Z']):
                n5run_p['--min' + dim] = eval(dim + 'min')
                n5run_p['--max' + dim] = eval(dim + 'max') + 1

                # make sure blocksize and factors are not bigger than data

                extent = n5run_p['--max' + dim] - n5run_p['--min' + dim]

                blocksize[idx] = min(blocksize[idx], extent)
                factors[idx] = min(blocksize[idx], factors[idx])


            # contrast limits

            n5run_p['--minIntensity'] = c_limits[0]
            n5run_p['--maxIntensity'] = c_limits[1]

            # optimize block size

            while np.prod(blocksize) < params.min_chunksize:
                blocksize[0] *= 2
                blocksize[1] *= 2

            tw = np.ceil(tilespecs[0]['width'] / blocksize[0]) * blocksize[0]
            th = np.ceil(tilespecs[0]['height'] / blocksize[1]) * blocksize[1]

            n5run_p['--tileWidth'] = '{:.0f}'.format(tw)
            n5run_p['--tileHeight'] = '{:.0f}'.format(th)

            n5run_p['--blockSize'] = ','.join(map(str, blocksize))
            n5run_p['--factors'] = ','.join(map(str, factors))

            # fill parameters

            spark_args = {'--jarfile': params.render_sparkjar}

            spark_p = dict()

            if comp_sel == 'sparkslurm':
                spark_p['--time'] = '00:' + str(timelim + params.spark_setupmargin) + ':00'

                spark_p['--worker_cpu'] = params.cpu_pernode_spark
                spark_p['--worker_nodes'] = hf.spark_nodes(n_cpu)

            else:
                spark_args['--cpu'] = launch_jobs.remote_params(comp_sel.split('::')[-1])['cpu']
                spark_args['--mem'] = launch_jobs.remote_params(comp_sel.split('::')[-1])['mem']

            run_params_generate = spsl_p.copy()

            run_params_generate.update(n5run_p)

            target_args = spark_p.copy()
            run_args = run_params_generate.copy()

            script = 'org.janelia.render.client.spark.n5.N5Client'

            # #   This is how to enforce custom jar files

            # script = 'org.janelia.saalfeldlab.hotknife.SparkConvertRenderStackToN5'
            # script  += " --jarfile=" + params.hotknife_dir + "/target/hot-knife-0.0.4-SNAPSHOT.jar"

        # generate script call...

        with open(param_file, 'w') as f:
            json.dump(run_params_generate, f, indent=4)

        run_prefix = launch_jobs.run_prefix()

        log_file = params.render_log_dir + '/' + label + '_' + run_prefix
        err_file = log_file + '.err'
        log_file += '.log'

        n5export_p = launch_jobs.run(target=comp_sel,
                                     pyscript=script,
                                     jsonfile=param_file,
                                     run_args=run_args,
                                     target_args=target_args,
                                     special_args=spark_args,
                                     logfile=log_file, errfile=err_file)

        launch_store = dict()
        launch_store['logfile'] = log_file
        launch_store['status'] = 'launch'
        launch_store['id'] = n5export_p
        launch_store['type'] = comp_sel

        return True, '', launch_store, outstore

    else:
        if outdir == '':
            return True, 'No output directory selected!', dash.no_update, dash.no_update

        elif is_bad_filename(outdir):
            return True, 'Wrong characters in input directory path. Please fix!', dash.no_update, dash.no_update

        if not os.access(outdir, os.W_OK | os.X_OK) and not newdir:
            return True, 'Output directory not writable!', dash.no_update, dash.no_update

        else:
            return False, '', dash.no_update, dash.no_update


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
