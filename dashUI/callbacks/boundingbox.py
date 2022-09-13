#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 14:52:17 2021

@author: schorb
"""

import dash
from dash import callback
# import dash_core_components as dcc
# import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

outs = list()

for dim in ['X', 'Y', 'Z']:
    @callback([Output({'component': 'start' + dim, 'module': MATCH}, 'max'),
               Output({'component': 'end' + dim, 'module': MATCH}, 'min')],
              [Input({'component': 'start' + dim, 'module': MATCH}, 'value'),
               Input({'component': 'end' + dim, 'module': MATCH}, 'value')]
              )
    def innerlimits(minval, maxval):
        return maxval, minval


    outs.extend([Output({'component': 'start' + dim, 'module': MATCH}, 'value'),
                 Output({'component': 'start' + dim, 'module': MATCH}, 'min'),
                 Output({'component': 'end' + dim, 'module': MATCH}, 'value'),
                 Output({'component': 'end' + dim, 'module': MATCH}, 'max')])

outs.append(Output({'component': 'sliceim_bboxparams_0', 'module': MATCH}, 'data'))


@callback(outs,
          [Input({'component': 'sliceim_rectsel_0', 'module': MATCH}, "data")],
          State({'component': 'sliceim_params_0', 'module': MATCH}, 'data')
          )
def paramstoouterlimits(annotations, imparams):
    if not dash.callback_context.triggered:
        raise PreventUpdate
    out = list()
    outdims = dict()

    for dim in ['X', 'Y']:
        minval = annotations[dim][0] # - annotations[dim + '_offset']
        maxval = annotations[dim][1] # - annotations[dim + '_offset']

        outdims[dim] = [minval, maxval]

        out.extend([minval, minval, maxval, maxval])

    outdims['Z'] = [imparams['minZ'], imparams['maxZ']]
    out.extend([imparams['minZ'], imparams['minZ'], imparams['maxZ'], imparams['maxZ']])
    out.append(outdims)

    return out
