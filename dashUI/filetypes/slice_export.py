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

compute_table_cols = ['Num_CPUs',
                      # 'MemGB_perCPU',
                      'runtime_minutes']

page1 = [html.Br(), pages.render_selector(label, show=False), html.Div(children=store)]

# =============================================
# select file type

filetypesel = html.Div([html.H4("Choose output file type."),
                  dcc.Dropdown(id={'component': 'filetype_dd', 'module': label},
                               persistence=True,
                               options=['jpg','png','tif'],
                               value='jpg'),
                  html.Br()
                  ])

page1.append(filetypesel)


# =============================================
# Start Button

gobutton = html.Div(children=[html.Br(),
                              html.Button('Start Export',
                                          id={'component': 'go', 'module': label}, disabled=True),
                              html.Div(id={'component': 'buttondiv', 'module': label}),
                              html.Br(),
                              pages.compute_loc(label, c_options=['sparkslurm'], c_default='sparkslurm'),
                              html.Br(),
                              html.Div(id={'component': 'run_state', 'module': label}, style={'display': 'none'},
                                       children='wait')])

page1.append(gobutton)

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


@app.callback([Output({'component': 'go', 'module': label}, 'disabled'),
               Output({'component': 'buttondiv', 'module': label}, 'children'),
               Output({'component': 'store_launch_status', 'module': label}, 'data'),
               Output({'component': 'store_render_launch', 'module': label}, 'data')],
              [Input({'component': 'go', 'module': label}, 'n_clicks'),
               Input({'component': "path_input", 'module': parent}, 'value'),
               Input({'component': 'stack_dd', 'module': parent}, 'value')],
              states
    , prevent_initial_call=True)
def sliceexport_execute_gobutton(click, outdir, stack, comp_sel, owner, project,
                              Xmin, Xmax, Ymin, Ymax, Zmin, Zmax,
                              sp_store, slice_in, c_limits):
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

        param_file = params.json_run_dir + '/' + parent + '_' + run_prefix + '.json'

        if comp_sel == 'standalone':

            # create output directory
            aldir = os.path.join(outdir, params.outdirbase)

            if not os.path.isdir(aldir):
                os.makedirs(aldir)

            slicedir = launch_jobs.run_prefix(nouser=True)

            slicedir = os.path.join(aldir, slicedir)

            slices = ''

            if Zmin == sp_store['zmin'] and Zmax == sp_store['zmax']:
                slices = '_full'
            else:
                slices = '_Z' + str(Zmin) + '-' + str(Zmax)


            slicerun_p = dict()

            with open(os.path.join(params.json_template_dir, 'n5export.json'), 'r') as f:
                slicerun_p.update(json.load(f))

            # slicerun_p['--n5Path'] = n5dir

            # get tile size from single tile

            url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack
            url += '/z/' + str(slice_in) + '/tile-specs'

            tilespecs = requests.get(url).json()

            # tilesize = '{:.0f},{:.0f}'.format(tilespecs[0]['width'], tilespecs[0]['height'])

            # slicerun_p['--tileSize'] = tilesize

            slicerun_p['--tileWidth'] = '{:.0f}'.format(tilespecs[0]['width'])
            slicerun_p['--tileHeight'] = '{:.0f}'.format(tilespecs[0]['height'])

            blocksize = list(map(int, slicerun_p['--blockSize'].split(',')))
            factors = list(map(int, slicerun_p['--factors'].split(',')))

            for idx, dim in enumerate(['X', 'Y', 'Z']):
                slicerun_p['--min' + dim] = eval(dim + 'min')
                slicerun_p['--max' + dim] = eval(dim + 'max') + 1

                # make sure blocksize and factors are not bigger than data

                extent = slicerun_p['--max' + dim] - slicerun_p['--min' + dim]

                blocksize[idx] = min(blocksize[idx], extent)
                factors[idx] = min(blocksize[idx], factors[idx])

            # contrast limits

            slicerun_p['--minIntensity'] = c_limits[0]
            slicerun_p['--maxIntensity'] = c_limits[1]

            run_params_generate = {}

            run_params_generate.update(slicerun_p)

            target_args = {}
            run_args = run_params_generate.copy()

            script = '...'

            # #   This is how to enforce custom jar files

            # script = 'org.janelia.saalfeldlab.hotknife.SparkConvertRenderStackToN5'
            # script  += " --jarfile=" + params.hotknife_dir + "/target/hot-knife-0.0.4-SNAPSHOT.jar"

        # generate script call...

        with open(param_file, 'w') as f:
            json.dump(run_params_generate, f, indent=4)

        run_prefix = launch_jobs.run_prefix()

        log_file = params.render_log_dir + '/' + parent + '_' + run_prefix
        err_file = log_file + '.err'
        log_file += '.log'

        sliceexport_p = launch_jobs.run(target=comp_sel,
                                     pyscript=script,
                                     jsonfile=param_file,
                                     run_args=run_args,
                                     target_args=target_args,
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