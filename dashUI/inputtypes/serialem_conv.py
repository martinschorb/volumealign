#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 08:42:12 2020

@author: schorb
"""
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State

import os
import json

from dashUI import params

from dashUI.utils import launch_jobs, pages
from dashUI.utils.checks import is_bad_filename

from dashUI.callbacks import filebrowse, render_selector

# element prefix
parent = "convert"

label = parent + "_SerialEM"

# SELECT input directory

# get user name and main group to pre-polulate input directory

group = params.group

# ============================
# set up render parameters

owner = "SerialEM"


# =============================================
# # Page content

store = pages.init_store({}, label)

# Pick source directory


directory_sel = html.Div(children=[html.H4("Select dataset metadata file (*.idoc):"),
                                   # html.Script(type="text/javascript",children="alert('test')"),                                   
                                   dcc.Input(id={'component': 'path_input', 'module': label}, type="text",
                                             debounce=True,
                                             value=params.default_dir,
                                             persistence=True, className='dir_textinput')
                                   ])

pathbrowse = pages.path_browse(label, show_files=True, file_types=['idoc'])

page1 = [directory_sel, pathbrowse, html.Div(store)]

# # ===============================================
#  RENDER STACK SELECTOR

page2 = []
page2.append(
    html.Div(pages.render_selector(label, create=True, owner=True, header='Select target stack:'),
             id={'component': 'render_seldiv', 'module': label})
    )

# =============================================
# Start Button


gobutton = html.Div(children=[html.Br(),
                              html.Button('Start conversion', id=label + "go", disabled=True),
                              html.Div([], id=label + 'directory-popup', style={'color': '#E00'}),
                              html.Br(),
                              pages.compute_loc(label)],
                    style={'display': 'inline-block'})

page2.append(gobutton)

page2.append(pages.donelink(label))

# =============================================
# Processing status

# initialized with store
# embedded from callbacks import runstate

# # =============================================
# # PROGRESS OUTPUT


collapse_stdout = pages.log_output(label)

# ----------------

# Full page layout:


page2.append(collapse_stdout)


# page2.extend(store)

# =============================================

#  LAUNCH CALLBACK FUNCTION

# =============================================


@callback([Output(label + 'go', 'disabled'),
           Output(label + 'directory-popup', 'children'),
           Output({'component': 'store_launch_status', 'module': label}, 'data'),
           Output({'component': 'store_render_launch', 'module': label}, 'data')
           ],
          [Input({'component': 'stack_dd', 'module': label}, 'value'),
           Input({'component': 'path_input', 'module': label}, 'value'),
           Input(label + 'go', 'n_clicks')
           ],
          [State({'component': 'project_dd', 'module': label}, 'value'),
           State({'component': 'compute_sel', 'module': label}, 'value'),
           State({'component': 'store_run_status', 'module': label}, 'data'),
           State({'component': 'store_render_launch', 'module': label}, 'data')],
          prevent_initial_call=True)
def serialem_conv_gobutton(stack_sel, in_dir, click, proj_dd_sel, compute_sel, run_state, outstore):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0].partition(label)[2]
    but_disabled = True
    popup = ''
    out = run_state
    log_file = run_state['logfile']

    # outstore = dash.no_update
    outstore = dict()
    outstore['owner'] = 'SerialEM'
    outstore['project'] = proj_dd_sel
    outstore['stack'] = stack_sel

    if 'go' in trigger:
        # launch procedure

        # prepare parameters:
        run_prefix = launch_jobs.run_prefix()

        param_file = params.json_run_dir + '/' + label + '_' + run_prefix + '.json'

        run_params = params.render_json.copy()
        run_params['render']['owner'] = outstore['owner']
        run_params['render']['project'] = proj_dd_sel

        with open(os.path.join(params.json_template_dir, 'SBEMImage_importer.json'), 'r') as f:
            run_params.update(json.load(f))

        run_params['image_file'] = in_dir
        run_params['stack'] = stack_sel

        with open(param_file, 'w') as f:
            json.dump(run_params, f, indent=4)

        log_file = params.render_log_dir + '/' + 'serialem_conv_' + run_prefix
        err_file = log_file + '.err'
        log_file += '.log'

        # launch
        # -----------------------

        sbem_conv_p = launch_jobs.run(target=compute_sel,
                                      pyscript=params.rendermodules_dir +
                                               '/dataimport/generate_EM_tilespecs_from_SerialEMmontage.py',
                                      jsonfile=param_file, logfile=log_file, errfile=err_file)

        run_state['status'] = 'running'
        run_state['id'] = sbem_conv_p
        run_state['type'] = launch_jobs.runtype(compute_sel)
        run_state['logfile'] = log_file

    else:

        outstore = dash.no_update
        # check launch conditions and enable/disable button
        if any([in_dir == '', in_dir is None]):
            if not (run_state['status'] == 'running'):
                run_state['status'] = 'wait'
                popup = 'No input file chosen.'

        elif is_bad_filename(in_dir):
            run_state['status'] = 'wait'
            popup = 'Wrong characters in input directory path. Please fix!'

        elif os.path.isfile(in_dir):
            # print(in_dir)
            if any([stack_sel == 'newstack', proj_dd_sel == 'newproj']):
                if not (run_state['status'] == 'running'):
                    run_state['status'] = 'wait'

            else:
                if not (run_state['status'] == 'running'):
                    run_state['status'] = 'input'
                    but_disabled = False

        else:
            if not (run_state['status'] == 'running'):
                run_state['status'] = 'wait'
                popup = 'Input Data not accessible.'

    out.update(run_state)

    return but_disabled, popup, out, outstore
