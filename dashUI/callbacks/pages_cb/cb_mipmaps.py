#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""

import os
import requests
import numpy as np
import importlib
import json

import dash
from dash.exceptions import PreventUpdate
from dash import dcc, html

from dashUI import params

from dashUI.utils import launch_jobs
from dashUI.utils import helper_functions as hf
from dashUI.pageconf.conf_mipmaps import status_table_cols, compute_table_cols, module


def mipmaps_stacktodir(stack_sel, owner, project, stack, allstacks, thispage):
    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    dir_out = ''
    out = dict()

    t_fields = [''] * len(status_table_cols)
    ct_fields = [1] * len(compute_table_cols)

    if (not stack_sel == '-') and (allstacks is not None):
        stacklist = [stack for stack in allstacks if stack['stackId']['stack'] == stack_sel]
        stack = stack_sel

        if not stacklist == []:
            stackparams = stacklist[0]
            out['zmin'] = stackparams['stats']['stackBounds']['minZ']
            out['zmax'] = stackparams['stats']['stackBounds']['maxZ']
            out['numtiles'] = stackparams['stats']['tileCount']
            out['numsections'] = stackparams['stats']['sectionCount']

            num_blocks = int(np.max((np.floor(out['numsections'] / params.section_split), 1)))

            url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project \
                  + '/stack/' + stack + '/z/' + str(out['zmin']) + '/render-parameters'
            tiles0 = requests.get(url).json()

            tilefile0 = os.path.abspath(tiles0['tileSpecs'][0]['mipmapLevels']['0']['imageUrl'].strip('file:'))

            dir_out = os.path.join(os.sep, *tilefile0.split(os.sep)[:-params.datadirdepth[owner] - 1])

            out['gigapixels'] = out['numtiles'] * stackparams['stats']['maxTileWidth'] * stackparams['stats'][
                'maxTileHeight'] / (10 ** 9)

            t_fields = [stack, str(stackparams['stats']['sectionCount']), str(stackparams['stats']['tileCount']),
                        '%0.2f' % out['gigapixels']]

            n_cpu = params.n_cpu_script

            timelim = np.ceil(
                out['gigapixels'] / n_cpu * params.mipmaps['min/Gpix/CPU'] * (1 + params.time_add_buffer) / num_blocks)

            ct_fields = [n_cpu, timelim, params.section_split]

    outlist = [dir_out, stack]  # ,out]
    outlist.extend(t_fields)
    outlist.extend(ct_fields)

    return outlist


def mipmaps_store_compute_settings(*inputs):
    thispage = inputs[-1]
    inputs = inputs[:-1]
    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    storage = dict()

    in_labels, in_values = hf.input_components()

    for input_idx, label in enumerate(in_labels):
        storage[label] = in_values[input_idx]

    return storage


def mipmaps_gobutton(mipmapdir, click, click2, run_state, comp_sel, runstep_in, owner, project, stack, stackparams,
                     comp_set, disable_out, dircheckdiv, logfile, outstore):
    trigger = hf.trigger()

    # init output

    rstate = 'wait'
    runstep = runstep_in

    launch_store = dash.no_update

    if logfile is None:
        logfile = params.render_log_dir + '/out.txt'
        launch_store = dict()
        launch_store['logfile'] = logfile
        launch_store['status'] = 'wait'
        run_state['status'] = 'wait'

    out_pop = dcc.ConfirmDialog(
        id={'component': 'danger-novaliddir', 'module': module}, displayed=True,
        message='The selected directory does not exist or is not writable!'
    )

    # ------------------------------------
    # activate button, prepare launch

    if 'path_input' in trigger:
        disable_out = True
        if any([mipmapdir == '', mipmapdir is None]):
            if not (run_state['status'] == 'running'):
                rstate = 'wait'

        elif os.path.isdir(mipmapdir):
            if os.path.exists(os.path.join(mipmapdir, params.mipmapdir)):
                rstate = 'input'
                out_pop.message = 'Warning: there already exists a MipMap directory. Will overwrite it.'
                disable_out = False
                dircheckdiv = out_pop

            if not (run_state['status'] == 'running'):
                rstate = 'input'
                disable_out = False

        else:
            if not (run_state['status'] == 'running'):
                rstate = 'wait'
                dircheckdiv = [out_pop, 'The selected directory does not exist or is not writable!']

    # ------------------------------------
    #  button   pressed,  launch

    elif 'go' in trigger:
        disable_out = True
        importlib.reload(params)
        runstep = 'generate'

        run_params = params.render_json.copy()
        run_params['render']['owner'] = owner
        run_params['render']['project'] = project

        run_params_generate = run_params.copy()

        # generate mipmaps script call...

        run_params_generate['input_stack'] = stack

        mipmapdir += '/mipmaps'

        if not os.path.exists(mipmapdir):
            os.makedirs(mipmapdir)

        run_params_generate['output_dir'] = mipmapdir

        with open(os.path.join(params.json_template_dir, 'generate_mipmaps.json'), 'r') as f:
            run_params_generate.update(json.load(f))

        sec_start = stackparams['zmin']
        sliceblock_idx = 0
        sec_end = sec_start
        run_prefix = launch_jobs.run_prefix()

        while sec_end <= stackparams['zmax']:
            sec_end = int(np.min([sec_start + comp_set['input_section_split'], stackparams['zmax']]))
            run_params_generate['zstart'] = sec_start
            run_params_generate['zend'] = sec_end

            run_params_generate['output_json'] = os.path.join(params.json_run_dir,
                                                              'output_' + module + '_' + run_prefix + '_' + str(
                                                                  sliceblock_idx) + '.json')

            param_file = params.json_run_dir + '/' + runstep + '_' + module + run_prefix + '_' + str(
                sliceblock_idx) + '.json'

            with open(param_file, 'w') as f:
                json.dump(run_params_generate, f, indent=4)

            log_file = params.render_log_dir + '/' + runstep + '_' + module + '_' + run_prefix + '_' + str(
                sliceblock_idx)
            err_file = log_file + '.err'
            log_file += '.log'

            sec_start = sec_end + 1
            sec_end = sec_start
            sliceblock_idx += 1

            # launch
            # -----------------------

            # check resource settings
            target_args = None

            if comp_sel == 'slurm':
                slurm_args = ['-N1']
                slurm_args.append('-n1')
                slurm_args.append('-c ' + str(comp_set['input_Num_CPUs']))
                slurm_args.append('--mem  ' + str(params.mem_per_cpu) + 'G')
                slurm_args.append('-t 00:%02i:00' % comp_set['input_runtime_minutes'])

                target_args = slurm_args

            mipmap_generate_p = launch_jobs.run(target=comp_sel,
                                                pyscript=params.asap_dir + '/dataimport/generate_mipmaps.py',
                                                jsonfile=param_file, run_args=[], target_args=target_args,
                                                logfile=log_file, errfile=err_file)

        launch_store = dict()
        launch_store['logfile'] = log_file
        launch_store['status'] = 'running'
        launch_store['id'] = mipmap_generate_p
        launch_store['type'] = comp_sel

        outstore = dict()
        outstore['owner'] = owner
        outstore['project'] = project
        outstore['stack'] = stack

    # ------------------------------------
    # launch apply mipmaps task when generate mipmaps task has completed successfully
    # TODO: refactor this to use proper sequentiall calls!

    elif 'interval1' in trigger:
        outstore = dash.no_update
        if runstep == 'generate' and run_state['status'] == 'done' and mipmapdir is not None:

            runstep = 'apply'
            run_prefix = launch_jobs.run_prefix()

            run_params = params.render_json.copy()
            run_params['render']['owner'] = owner
            run_params['render']['project'] = project

            mipmapdir += '/mipmaps/'

            run_params_generate = run_params.copy()

            with open(os.path.join(params.json_template_dir, 'apply_mipmaps.json'), 'r') as f:
                run_params_generate.update(json.load(f))

            # run_params_generate['output_json'] = os.path.join(params.json_run_dir, 'output_' + module
            #                                                   + params.run_prefix + '.json')
            run_params_generate["input_stack"] = stack
            run_params_generate["output_stack"] = stack #+ "_mipmaps"
            run_params_generate["mipmap_prefix"] = "file://" + mipmapdir

            param_file = params.json_run_dir + '/' + runstep + '_' + module + '_' + run_prefix + '.json'
            run_params_generate["zstart"] = stackparams['zmin']
            run_params_generate["zend"] = stackparams['zmax']
            run_params_generate["pool_size"] = params.n_cpu_script
            run_params_generate['output_json'] = os.path.join(params.json_run_dir,
                                                              'output_apply_' + module + '_' + run_prefix + '.json')

            with open(param_file, 'w') as f:
                json.dump(run_params_generate, f, indent=4)

            log_file = params.render_log_dir + '/' + runstep + '_' + module + '_' + run_prefix
            err_file = log_file + '.err'
            log_file += '.log'

            mipmap_apply_p = launch_jobs.run(target=comp_sel,
                                             pyscript=params.asap_dir + '/dataimport/apply_mipmaps_to_render.py',
                                             jsonfile=param_file, run_args=[], logfile=log_file, errfile=err_file)

            launch_store = dict()
            launch_store['logfile'] = log_file
            launch_store['status'] = html.Div(
                [html.Img(src='../assets/gears.gif', height=72), html.Br(), 'running apply mipmaps to stack'])
            launch_store['id'] = mipmap_apply_p
            launch_store['type'] = launch_jobs.runtype(comp_sel)

        elif runstep == 'apply' and run_state['status'] == 'done' and mipmapdir is not None:

            launch_store = dict()
            launch_store['status'] = 'done'
            launch_store['logfile'] = logfile

    return disable_out, dircheckdiv, runstep, launch_store, outstore
