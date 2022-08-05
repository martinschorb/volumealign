#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 15:26:45 2020

@author: schorb
"""

import os
import sys

import dash
from dash import dcc, __version__
import dash_bootstrap_components as dbc

from dashUI import params
from index import navbar

app = dash.Dash(
    __name__,
    use_pages=True,
)

intervals = dcc.Interval(id='interval1', interval=params.refresh_interval, n_intervals=0)

app.layout = dbc.Container(
    [navbar, dcc.Location(id='url', refresh=True), intervals, dash.page_container]
)

if __name__ == '__main__':
    debug = True
    port = 8050

    if len(sys.argv) > 1:
        debug = False
        port = sys.argv[1]

    print('using dash version ', __version__)

    if os.path.exists('cert.pem') and os.path.exists('key.pem'):
        app.run_server(host='0.0.0.0', debug=debug, port=port, ssl_context=('cert.pem', 'key.pem'))
    else:
        print('No HTTPS encrypted connection supported. Check documentation.')
        app.run_server(host='0.0.0.0', debug=debug, port=port)
