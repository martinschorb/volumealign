#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 15:26:45 2020

@author: schorb
"""

import os
import sys
import logging

import dash
from dash import dcc, html, callback, ctx, __version__
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate

from dashUI import params
from dashUI.index import navbar, globalstore

logging.getLogger('werkzeug').setLevel(logging.ERROR)

debug = True
port = params.dash_startingport

if len(sys.argv) > 1:
    debug = False
    port = sys.argv[1]

app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True
)

intervals = dcc.Interval(id='interval1', interval=params.refresh_interval, n_intervals=0)

app.layout = html.Div([navbar,
                       dcc.Location(id='url', refresh=True),
                       intervals,
                       globalstore,
                       dash.page_container])


@callback(Output('render_store', 'data'),
          Input({'component': 'store_render_launch', 'module': ALL}, 'data'),
          State('render_store', 'data'),
          prevent_initial_callback=True)
def update_render_store(*inputs):
    if ctx.triggered[0]['value'] is None:
        raise PreventUpdate

    store = inputs[-1]

    for key, val in ctx.triggered[0]['value'].items():
        if val not in ['', None]:
            store[key] = ctx.triggered[0]['value'][key]

    return store


if __name__ == '__main__':

    print('using dash version ', __version__)

    sslcert = os.path.join(params.base_dir, 'cert.pem')
    sslkey = os.path.join(params.base_dir, 'key.pem')

    if os.path.exists(sslcert) and os.path.exists(sslkey):
        app.run(host='0.0.0.0', debug=debug, port=port, ssl_context=(sslcert, sslkey))
    else:
        print('No HTTPS encrypted connection supported. Check documentation.')
        app.run(host='0.0.0.0', debug=debug, port=port)
