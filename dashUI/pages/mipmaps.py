#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 16:15:27 2020

@author: schorb
"""
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dashUI.callbacks import render_selector
from dashUI.callbacks.pages_cb import cb_mipmaps as cb
from dashUI.pageconf.conf_mipmaps import status_table_cols, compute_table_cols, module
from dashUI.pages.side_bar import sidebar
from dashUI.utils import helper_functions as hf
from dashUI.utils import pages

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
                                                              dcc.Input(id={'component': 'input_' + col,
                                                                            'module': module},
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

    return cb.mipmaps_store_compute_settings(*inputs)


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
def mipmaps_gobutton(*args):

    return cb.mipmaps_gobutton(*args)


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
