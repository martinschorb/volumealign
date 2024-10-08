#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020
solve
@author: schorb
"""
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import os
import json
import time

import renderapi

from dashUI import params

from dashUI.utils import pages, launch_jobs, checks
from dashUI.utils import helper_functions as hf

from dashUI.callbacks import render_selector

from dashUI.pages.side_bar import sidebar

module = 'solve'

dash.register_page(__name__,
                   name='Solve Positions')

storeinit = {}
store = pages.init_store(storeinit, module)

for storeitem in params.match_store.keys():
    store.append(dcc.Store(id={'component': 'store_' + storeitem, 'module': module}, storage_type='session',
                           data=params.match_store[storeitem]))

main = html.Div(id={'component': 'main', 'module': module},
                children=html.H3("Solve tile Positions from PointMatchCollection"))

page = [main]

# # ===============================================
#  RENDER STACK SELECTOR

page1 = pages.render_selector(module)

page.append(page1)

# ===============================================
# Match selector


page2 = pages.match_selector(module)

page.append(page2)

# ===============================================


tileview = pages.tile_view(module)

page.append(tileview)

# ===============================================

slice_view = pages.section_view(module)

page.append(slice_view)

# ==============================

page.append(pages.substack_sel(module))

# ========================


# ------------------
# SET STACK


# assemble dropdown

stack_div = html.Div(id=module + 'out_stack_div', children=[html.H4("Select Output Render Stack:"),
                                                            dcc.Dropdown(
                                                                id={'component': 'outstack_dd', 'module': module},
                                                                persistence=True,
                                                                clearable=False),
                                                            html.Div(children=['Enter new stack name: ',
                                                                               dcc.Input(id=module + "stack_input",
                                                                                         type="text", debounce=True,
                                                                                         placeholder="new_stack",
                                                                                         persistence=False)
                                                                               ], id=module + 'newstack',
                                                                     style={'display': 'none'}),
                                                            html.Br(),
                                                            html.Div([html.A('Browse Project',
                                                                             id=module + 'browse_proj',
                                                                             target="_blank"),
                                                                      html.Div([' - ',
                                                                                html.A('Browse Stack',
                                                                                       id=module + 'browse_stack',
                                                                                       target="_blank")
                                                                                ], id=module + 'browse_stackdiv',
                                                                               style={'display': 'flex',
                                                                                      'white-space': 'pre'})
                                                                      ], style={'display': 'flex'}),
                                                            html.Br(), ]
                     )

page.append(stack_div)


# dropdown callback

# Fills the Stack DropDown

@callback([Output({'component': 'outstack_dd', 'module': module}, 'options'),
           Output({'component': 'outstack_dd', 'module': module}, 'value'),
           Output(module + 'browse_proj', 'href'),
           Output(module + 'browse_proj', 'style')
           ],
          [Input({'component': 'stack_dd', 'module': module}, 'options'),
           Input(module + 'stack_input', 'value')],
          [State({'component': 'owner_dd', 'module': module}, 'value'),
           State({'component': 'project_dd', 'module': module}, 'value'),
           State('url', 'pathname')],
          prevent_initial_call=True)
def solve_stacks(dd_options_in, newstack_name, owner, project_sel, thispage):
    thispage = thispage.lstrip('/')

    if thispage in (None, '') or thispage not in hf.trigger(key='module') and dd_options_in is not None:
        raise PreventUpdate

    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0].partition(module)[2]
    stack = 'newstack'
    dd_options = [{'label': 'Create new Stack', 'value': 'newstack'}]

    if project_sel is None or owner is None or dd_options_in is None:
        return dash.no_update

    dd_options.extend(dd_options_in)

    proj_href = params.render_base_url + 'view/stacks.html?renderStackOwner=' + owner

    if 'project_dd' in trigger:
        stack = 'newstack'

    elif trigger == 'stack_input':
        newstack_name = checks.clean_render_name(newstack_name)
        dd_options.append({'label': newstack_name, 'value': newstack_name})
        stack = newstack_name

    return dd_options, stack, proj_href, {}


@callback([Output(module + 'browse_stack', 'href'),
           Output(module + 'browse_stackdiv', 'style')],
          Input({'component': 'outstack_dd', 'module': module}, 'value'),
          [State({'component': 'project_dd', 'module': module}, 'value'),
           State({'component': 'owner_dd', 'module': module}, 'value'),
           State('url', 'pathname')],
          prevent_initial_call=True)
def solve_update_stack_browse(stack_state, project_sel, owner, thispage):
    thispage = thispage.lstrip('/')

    if thispage in (None, '') or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    if project_sel is None or owner is None or stack_state is None:
        raise PreventUpdate

    if stack_state == 'newstack':
        return params.render_base_url, {'display': 'none'}
    else:
        return params.render_base_url + 'view/stack-details.html?renderStackOwner=' + owner + '&renderStackProject=' + \
               project_sel + '&renderStack=' + stack_state, {'display': 'block'}


# Create a new Stack

@callback(Output(module + 'newstack', 'style'),
          Input({'component': 'outstack_dd', 'module': module}, 'value'),
          prevent_initial_call=True)
def solve_new_stack_input(stack_value):
    if stack_value == 'newstack':
        style = {'display': 'block'}
    else:
        style = {'display': 'none'}

    return style


# =============================================

# set transformation type


tform_options = list()

for trafo in params.solve_transforms:
    tform_options.append({'label': trafo, 'value': trafo})

type_options = list()
for stype in params.solve_types:
    type_options.append({'label': stype, 'value': stype})

transform = html.Div(id=module + 'tformsel_div', children=[html.H4("Select Transform type:"),
                                                           dcc.Dropdown(id={'component': 'tform_dd', 'module': module},
                                                                        persistence=True,
                                                                        clearable=False, options=tform_options,
                                                                        value='rigid'),
                                                           html.Br(),
                                                           html.Details([
                                                               html.Summary('Range of sections to consider:  '),
                                                               dcc.Input(
                                                                   id={'component': 'sec_range', 'module': module},
                                                                   type='number', min=1,
                                                                   max=params.max_slicerange,
                                                                   value=3),
                                                               dcc.Checklist(['Same weight for all distances.'],
                                                                             id={'component': 'dz_weights',
                                                                                 'module': module}
                                                                             )]),
                                                           html.Details([
                                                               html.Summary("Select Solve type:"),
                                                               dcc.Dropdown(
                                                                   id={'component': 'type_dd', 'module': module},
                                                                   persistence=True,
                                                                   clearable=False, options=type_options,
                                                                   value='3D')
                                                           ])
                                                           ])

page.append(transform)

# =============================================
# Start Button


gobutton = html.Div(children=[html.Br(),
                              html.Button('Start Solve',
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
           Input({'component': 'matchcoll_dd', 'module': module}, 'value'),
           Input({'component': 'outstack_dd', 'module': module}, 'value'),
           Input({'component': 'tform_dd', 'module': module}, 'value')],
          [State({'component': 'type_dd', 'module': module}, 'value'),
           State({'component': 'compute_sel', 'module': module}, 'value'),
           State({'component': 'startsection', 'module': module}, 'value'),
           State({'component': 'endsection', 'module': module}, 'value'),
           State({'component': 'sec_range', 'module': module}, 'value'),
           State({'component': 'dz_weights', 'module': module}, 'value'),
           State({'component': 'store_owner', 'module': module}, 'data'),
           State({'component': 'store_project', 'module': module}, 'data'),
           State({'component': 'stack_dd', 'module': module}, 'value'),
           State({'component': 'mc_owner_dd', 'module': module}, 'value')],
          prevent_initial_call=True)
def solve_execute_gobutton(click, matchcoll, outstack, tform, stype, comp_sel, startsection, endsection, sec_range,
                           dz_weights, owner, project, stack, mc_own):
    if not dash.callback_context.triggered:
        raise PreventUpdate

    trigger = hf.trigger()

    if 'go' not in trigger:
        if any(['' in [matchcoll, outstack, mc_own], None in [matchcoll, outstack, mc_own],
                'newstack' in [stack, outstack]]):
            return True, dash.no_update, dash.no_update

        return False, dash.no_update, dash.no_update

    if click is None:
        return dash.no_update

    # prepare parameters:
    run_prefix = launch_jobs.run_prefix()

    rp = params.render_json.copy()
    rp['render']['owner'] = owner
    rp['render']['project'] = project

    run_params_generate = dict()

    # generate script call...

    with open(os.path.join(params.json_template_dir, module + '.json'), 'r') as f:
        run_params_generate.update(json.load(f))

    run_params_generate['output_json'] = params.render_log_dir + '/' + module + '_' + run_prefix + '_' + stack + '.json'

    run_params_generate['first_section'] = startsection
    run_params_generate['last_section'] = endsection

    run_params_generate['solve_type'] = stype
    run_params_generate['transformation'] = tform

    run_params_generate['input_stack'].update(rp['render'])
    run_params_generate['input_stack']['name'] = stack

    run_params_generate['pointmatch'].update(rp['render'])
    run_params_generate['pointmatch']['owner'] = mc_own
    run_params_generate['pointmatch']['name'] = matchcoll

    run_params_generate['output_stack'].update(rp['render'])
    run_params_generate['output_stack']['name'] = outstack

    run_params_generate['matrix_assembly'] = {}
    run_params_generate['matrix_assembly']['depth'] = list(range(sec_range))

    if dz_weights != []:
        run_params_generate['matrix_assembly']['inverse_dz'] = False

    if comp_sel in params.comp_clustertypes:
        run_params_generate['n_parallel_jobs'] = params.n_cpu_script

    param_file = params.json_run_dir + '/' + module + '_' + run_prefix + '.json'

    with open(param_file, 'w') as f:
        json.dump(run_params_generate, f, indent=4)

    log_file = params.render_log_dir + '/' + module + '_' + run_prefix
    err_file = log_file + '.err'
    log_file += '.log'

    # copy resolution metadata to the new output stack

    render = renderapi.Render(host=rp['render']['host'], port=rp['render']['port'],
                              client_scripts=rp['render']['client_scripts'])

    orig_meta = render.run(renderapi.stack.get_stack_metadata, stack, owner=owner, project=project)

    # time.sleep(5)

    solve_generate_p = launch_jobs.run(target=comp_sel, pyscript=params.asap_dir + '/solver/solve.py',
                                       jsonfile=param_file, run_args=None, target_args=None, logfile=log_file,
                                       errfile=err_file)

    time.sleep(5)

    # populate new stack with the original resolution values

    try:
        md = (renderapi.stack.get_stack_metadata(outstack, render=render, project=project, owner=owner))
    except:
        launch_store = dict()
        launch_store['logfile'] = log_file
        launch_store['status'] = 'error'
        launch_store['id'] = '-'
        launch_store['type'] = launch_jobs.runtype(comp_sel)

        return False, launch_store, dash.no_update

    md.stackResolutionX = orig_meta.stackResolutionX
    md.stackResolutionY = orig_meta.stackResolutionY
    md.stackResolutionZ = orig_meta.stackResolutionZ

    md1 = renderapi.stack.get_full_stack_metadata(outstack, render=render, owner=owner, project=project)

    # in case the solve process is already done

    setcomplete = False
    if md1['state'] == 'COMPLETE':
        setcomplete = True

    render.run(renderapi.stack.set_stack_metadata, outstack, md, owner=owner, project=project)

    if setcomplete:
        renderapi.stack.set_stack_state(outstack, state='COMPLETE', render=render, owner=owner, project=project)

    launch_store = dict()
    launch_store['logfile'] = log_file
    launch_store['status'] = 'running'
    launch_store['id'] = solve_generate_p
    launch_store['type'] = launch_jobs.runtype(comp_sel)

    outstore = dict()
    outstore['owner'] = owner
    outstore['project'] = project
    outstore['stack'] = outstack

    return True, launch_store, outstore


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
