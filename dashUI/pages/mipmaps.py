#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 16:15:27 2020

@author: schorb
"""
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

import json
import requests
import os
import importlib
import numpy as np

from dashUI import params

from dashUI.utils import launch_jobs, pages
from dashUI.utils import helper_functions as hf

from dashUI.callbacks import runstate, render_selector, substack_sel
from dashUI.callbacks.pages_cb import cb_mipmaps as cb

from dashUI.pages.side_bar import sidebar
from dashUI.pageconf.conf_mipmaps import status_table_cols, compute_table_cols

module = 'mipmaps'

dash.register_page(__name__,
                   name='Generate MipMaps')

storeinit = {}
store = pages.init_store(storeinit, module)

store.append(dcc.Store(id={'component': 'runstep', 'module': module}, data='generate'))

# =========================================

main = html.Div(id={'component': 'main', 'module': module}, children=html.H3("Generate MipMaps for Render stack"))

page = [main]

# # ===============================================
#  RENDER STACK SELECTOR

# Pre-fill render stack selection from previous module

us_out, us_in, us_state = render_selector.init_update_store(module, 'convert')


@callback(us_out, us_in, us_state)
def mipmaps_update_store(*args):
    thispage = args[-1]
    args = args[:-1]
    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    return render_selector.update_store(*args)


page1 = pages.render_selector(module)

page.append(page1)

# # ===============================================
#  SPECIFIC PAGE CONTENT


page2 = html.Div(id={'component': 'page2', 'module': module},
                 children=[html.H3('Mipmap output directory (subdirectory "mipmaps")'),
                           dcc.Input(id={'component': "path_input", 'module': module}, type="text", debounce=True,
                                     persistence=True, className='dir_textinput'),
                           pages.path_browse(module),
                           html.Br()])

page.append(page2)

# # ===============================================
# Compute Settings

compute_settings = html.Details(children=[html.Summary('Compute settings:'),
                                          html.Table([html.Tr([html.Th(col) for col in status_table_cols]),
                                                      html.Tr(
                                                          [html.Td('', id={'component': 't_' + col, 'module': module})
                                                           for col in status_table_cols])
                                                      ], className='table'),
                                          html.Br(),
                                          html.Table([html.Tr([html.Th(col) for col in compute_table_cols]),
                                                      html.Tr([
                                                          html.Td(
                                                              dcc.Input(id={'component': 'input_' + col, 'module': module},
                                                                        type='number', min=1))
                                                          for col in compute_table_cols])
                                                      ], className='table'),
                                          dcc.Store(id={'component': 'store_compset', 'module': module})
                                          ])
page.append(compute_settings)
page.append(pages.substack_sel(module, hidden=True))


# callbacks

@callback(Output({'component': 'store_compset', 'module': module}, 'data'),
          [Input({'component': 'input_' + col, 'module': module}, 'value') for col in compute_table_cols],
          State('url', 'pathname'),
          prevent_initial_call=True)
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


# Update directory and compute settings from stack selection

stackoutput = [Output({'component': 'path_ext', 'module': module}, 'data'),
               Output({'component': 'store_stack', 'module': module}, 'data'),
               # Output({'component': 'store_stackparams', 'module': module}, 'data')
               ]
tablefields = [Output({'component': 't_' + col, 'module': module}, 'children') for col in status_table_cols]
compute_tablefields = [Output({'component': 'input_' + col, 'module': module}, 'value') for col in compute_table_cols]

stackoutput.extend(tablefields)

stackoutput.extend(compute_tablefields)


@callback(stackoutput,
              Input({'component': 'stack_dd', 'module': module}, 'value'),
              [State({'component': 'store_owner', 'module': module}, 'data'),
               State({'component': 'store_project', 'module': module}, 'data'),
               State({'component': 'store_stack', 'module': module}, 'data'),
               State({'component': 'store_allstacks', 'module': module}, 'data'),
               State('url', 'pathname')],
              prevent_initial_call=True)
def mipmaps_stacktodir(*args):

    return cb.mipmaps_stacktodir(*args)


# =============================================
# Start Button

gobutton = html.Div(children=[html.Br(),
                              html.Button('Start MipMap generation & apply to current stack',
                                          id={'component': 'go', 'module': module}, disabled=True),
                              html.Div(id={'component': 'buttondiv', 'module': module}),
                              html.Div(id={'component': 'directory-popup', 'module': module}),
                              html.Br(),
                              pages.compute_loc(module),
                              html.Br(),
                              html.Div(id={'component': 'run_state', 'module': module}, style={'display': 'none'},
                                       children='wait')])

page.append(gobutton)


@callback([Output({'component': 'go', 'module': module}, 'disabled'),
               Output({'component': 'directory-popup', 'module': module}, 'children'),
               Output({'component': 'runstep', 'module': module}, 'data'),
               Output({'component': 'store_launch_status', 'module': module}, 'data'),
               Output({'component': 'store_render_launch', 'module': module}, 'data')],
              [Input({'component': 'path_input', 'module': module}, 'value'),
               Input({'component': 'go', 'module': module}, 'n_clicks'),
               Input('interval1', 'n_intervals')],
              [State({'component': 'store_run_status', 'module': module}, 'data'),
               State({'component': 'compute_sel', 'module': module}, 'value'),
               State({'component': 'runstep', 'module': module}, 'data'),
               State({'component': 'store_owner', 'module': module}, 'data'),
               State({'component': 'store_project', 'module': module}, 'data'),
               State({'component': 'store_stack', 'module': module}, 'data'),
               State({'component': 'store_stackparams', 'module': module}, 'data'),
               State({'component': 'store_compset', 'module': module}, 'data'),
               State({'component': 'go', 'module': module}, 'disabled'),
               State({'component': 'directory-popup', 'module': module}, 'children'),
               State({'component': 'outfile', 'module': module}, 'children'),
               State({'component': 'store_render_launch', 'module': module}, 'data')],
              prevent_initial_call=True)
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
            run_params_generate["output_stack"] = stack + "_mipmaps"
            run_params_generate["mipmap_prefix"] = "file://" + mipmapdir

            param_file = params.json_run_dir + '/' + runstep + '_' + module + '_' + run_prefix + '.json'
            run_params_generate["zstart"] = stackparams['zmin']
            run_params_generate["zend"] = stackparams['zmax']
            run_params_generate["pool_size"] = params.n_cpu_script

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
    return [sidebar(), html.Div(page, className='main')]
