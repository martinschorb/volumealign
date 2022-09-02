#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 16:15:27 2020

@author: schorb
"""
import dash
from dash import dcc, callback
from dash import html
from dash.dependencies import Input, Output, State

from dashUI.pages.side_bar import sidebar
from dashUI.callbacks.pages_cb import cb_tilepairs as cb

from dashUI import params
from dashUI.utils import pages
from dashUI.callbacks import render_selector

module = 'tilepairs'
dash.register_page(__name__,
                   name='Find Tile Pairs')

storeinit = {}
store = pages.init_store(storeinit, module)

store.append(dcc.Store(id={'component': 'runstep', 'module': module}, data='generate'))

main = html.Div(id={'component': 'main', 'module': module}, children=html.H3("Generate TilePairs for Render stack"))

page = [main]

# # ===============================================
#  RENDER STACK SELECTOR

page1 = pages.render_selector(module)

page.append(page1)

# # # ===============================================


page2 = html.Div(id={'component': 'page2', 'module': module},
                 children=[html.H4('Pair assignment mode'),
                           html.Div([dcc.RadioItems(options=[
                               {'label': '2D (tiles in montage/mosaic)', 'value': '2D'},
                               {'label': '3D (across sections)', 'value': '3D'}],
                               value='2D',
                               id={'component': 'pairmode', 'module': module}),
                           ],
                               style={'display': 'inline,block'}),
                           html.Br(),
                           pages.substack_sel(module)
                           ])

page.append(page2)


# # ===============================================

@callback([Output({'component': 'page2', 'module': module}, 'style'),
           Output({'component': 'multi-run', 'module': module}, 'style'),
           Output({'component': 'pairmode', 'module': module}, 'value')],
          Input({'component': 'owner_dd', 'module': module}, 'value'),
          prevent_initial_call=True)
def stack2Donly(owner):
    """
    Toggles visibility of the slice selectors.

    :param str owner: The Render owner
    :return: CSS display mode, '2D
    :rtype: dict
    """

    style1 = {}
    style2 = {'display': 'none'}
    val = '2D'
    if owner in params.owners_2d:
        style1 = {'display': 'none'}
        style2 = {}

    return style1, style2, val


@callback([Output({'component': '3Dslices', 'module': module}, 'style'),
           Output({'component': 'sec_input1', 'module': module}, 'value')],
          Input({'component': 'pairmode', 'module': module}, 'value'),
          prevent_initial_call=True)
def tilepairs_3D_status(pairmode):
    """
    Toggles visibility of the 3D parameter selectors.

    :param str pairmode: The choice of mode dimensionality. "sec_input1"
    :return: CSS display mode
    :rtype: dict
    """

    if pairmode == '2D':
        style = {'display': 'none'}
        val = 0
    elif pairmode == '3D':
        style = {'display': 'block'}
        val = 1
    return style, val


# optional bundle multi-stack import from SerialEM


page3 = html.Div(id={'component': 'multi-run', 'module': module},
                 children=[html.H4('Process all stacks from this data import (multiple nav items)?'),
                           html.Div([dcc.Checklist(options=[
                               {'label': 'process all nav items', 'value': 'multi'}],
                               id={'component': 'multi-nav', 'module': module}),
                           ],
                               style={'display': 'inline,block'}),
                           html.Br()
                           ])

page.append(page3)

# =============================================
# Start Button


gobutton = html.Div(children=[html.Br(),
                              html.Button('Start TilePair generation',
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
           Input({'component': 'pairmode', 'module': module}, 'value'),
           Input({'component': 'stack_dd', 'module': module}, 'value')],
          [State({'component': 'sec_input1', 'module': module}, 'value'),
           State({'component': 'compute_sel', 'module': module}, 'value'),
           State({'component': 'startsection', 'module': module}, 'value'),
           State({'component': 'endsection', 'module': module}, 'value'),
           State({'component': 'store_owner', 'module': module}, 'data'),
           State({'component': 'store_project', 'module': module}, 'data'),
           State({'component': 'multi-nav', 'module': module}, 'value'),
           State({'component': 'stack_dd', 'module': module}, 'options')],
          prevent_initial_call=True)
def tilepairs_execute_gobutton(*inputs):
    return cb.tilepairs_execute_gobutton(*inputs)


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
