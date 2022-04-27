#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import os
import requests
import importlib

import params

from app import app

from utils import pages
from utils import helper_functions as hf

from callbacks import (runstate, render_selector,
                       boundingbox, tile_view,
                       substack_sel, filebrowse)

module = 'export'

subpages = [{'label': 'N5 (MoBIE/BDV)', 'value': 'N5'},
            {'label': 'slice images', 'value': 'slices'}
            ]

submodules = [
    'filetypes.N5_export',
    'filetypes.slice_export'
]

storeinit = {}
store = pages.init_store(storeinit, module)

main = html.Div(id={'component': 'main', 'module': module}, children=html.H3("Export Render stack to volume"))

page = [main]

# # ===============================================
#  RENDER STACK SELECTOR

# Pre-fill render stack selection from previous module

us_out, us_in, us_state = render_selector.init_update_store(module, 'solve')


@app.callback(us_out, us_in, us_state,
              prevent_initial_call=True)
def export_update_store(*args):
    thispage = args[-1]
    args = args[:-1]
    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    return render_selector.update_store(*args)


page.append(pages.render_selector(module))

# ===============================================

slice_view = pages.section_view(module, bbox=True)

page.append(slice_view)

# ==============================

page.append(pages.boundingbox(module))

# ===============================================

page0 = html.Div([html.H4("Choose output type."),
                  dcc.Dropdown(id={'component': 'subpage_dd', 'module': module},
                               options=subpages,
                               className='dropdown_inline',
                               value=''),
                  html.Br()
                  ])

page.append(page0)

page3 = html.Div(id={'component': 'page2', 'module': module}, children=[html.H4('Output path'),
                                                                        dcc.Input(id={'component': "path_input",
                                                                                      'module': module}, type="text",
                                                                                  debounce=True, persistence=True,
                                                                                  className='dir_textinput'),
                                                                        # dcc.Input(id={'component': "path_input", 'module': label}, type="text",style={'display': 'none'})
                                                                        # html.Button('Browse',id={'component': "browse1", 'module': label}),
                                                                        # 'graphical browsing works on cluster login node ONLY!',
                                                                        # html.Br()
                                                                        ])

page.append(page3)

pathbrowse = pages.path_browse(module)

page.append(pathbrowse)


# callback for output

@app.callback(Output({'component': 'path_ext', 'module': module}, 'data'),
              [Input({'component': "path_input", 'module': module}, 'n_blur'),
               Input({'component': "path_input", 'module': module}, 'n_submit'),
               Input({'component': 'stack_dd', 'module': module}, 'value')],
              [State({'component': 'store_owner', 'module': module}, 'data'),
               State({'component': 'store_project', 'module': module}, 'data'),
               State({'component': 'store_allstacks', 'module': module}, 'data'),
               State({'component': "path_input", 'module': module}, 'value')
               ]
              )
def export_stacktodir(dir_trigger, trig2, stack_sel, owner, project, allstacks, browsedir):
    dir_out = browsedir
    trigger = hf.trigger()

    if (not stack_sel == '-') and (allstacks is not None):
        stacklist = [stack for stack in allstacks if stack['stackId']['stack'] == stack_sel]
        stack = stack_sel

        if not trigger == 'path_input':
            if not stacklist == []:
                stackparams = stacklist[0]

                if 'None' in (stackparams['stackId']['owner'], stackparams['stackId']['project']):
                    return dash.no_update

                url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project \
                      + '/stack/' + stack + '/z/' + str(int(
                    (stacklist[0]['stats']['stackBounds']['maxZ'] - stacklist[0]['stats']['stackBounds']['minZ']) / 2))\
                      + '/render-parameters'

                tiles0 = requests.get(url).json()

                tilefile0 = os.path.abspath(tiles0['tileSpecs'][0]['mipmapLevels']['0']['imageUrl'].strip('file:'))

                dir_out = os.path.join(os.sep, *tilefile0.split(os.sep)[:-params.datadirdepth[owner] - 1])

    return dir_out


# =============================================
# # Page content for specific export call


page1 = [pages.log_output(module, hidden=True)]

# # =============================================
# # # Page content

page1.append(html.Div([html.Br(), 'No data type selected.'],
                      id=module + '_nullpage'))

switch_outputs = [Output(module + '_nullpage', 'style')]

status_inputs = []

page2 = []

for subsel, impmod in zip(subpages, submodules):
    thismodule = importlib.import_module(impmod)

    page1.append(html.Div(getattr(thismodule, 'page1'),
                          id={'component': 'page1', 'module': subsel['value']},
                          style={'display': 'none'}))
    switch_outputs.append(Output({'component': 'page1', 'module': subsel['value']}, 'style'))

    page2.append(html.Div(getattr(thismodule, 'page2'),
                          id={'component': 'page2', 'module': subsel['value']},
                          style={'display': 'none'}))
    switch_outputs.append(Output({'component': 'page2', 'module': subsel['value']}, 'style'))

    status_inputs.append(Input({'component': 'status', 'module': subsel['value']}, 'data'))


# Switch the visibility of elements for each selected sub-page based on the import type dropdown selection

@app.callback(switch_outputs,
              Input({'component': 'subpage_dd', 'module': module}, 'value'),
              State('url', 'pathname'))
def convert_output(dd_value, thispage):
    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    outputs = dash.callback_context.outputs_list
    outstyles = [{'display': 'none'}] * len(outputs)

    modules = [m['id']['module'] for m in outputs[1:]]

    for ix, mod in enumerate(modules):

        if mod == dd_value:
            outstyles[ix + 1] = {}

    if dd_value not in modules:
        outstyles[0] = {}

    return outstyles


# collect variables from sub pages and make them available to following pages

c_in, c_out = render_selector.subpage_launch(module, subpages)

if not c_in == []:
    @app.callback(c_out, c_in)
    def convert_merge_launch_stores(*inputs):
        return hf.trigger_value()

page.append(html.Div(page1))
page.append(html.Div(page2))
