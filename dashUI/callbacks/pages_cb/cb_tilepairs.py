#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""
import json
import os

import dash
from dash.exceptions import PreventUpdate

from dashUI import params
from dashUI.utils import launch_jobs
from dashUI.utils import helper_functions as hf

module = 'tilepairs'


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


def tilepairs_execute_gobutton(click, pairmode, stack, slicedepth, comp_sel, startsection, endsection, owner, project,
                               multi, stacklist):
    if click is None:
        raise PreventUpdate

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
