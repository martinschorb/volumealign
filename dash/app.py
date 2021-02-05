#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 15:25:59 2020

@author: schorb
"""

import dash
from flask import Flask
import logging
server = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = dash.Dash(__name__,title='Volume EM alignment with Render',server=server, suppress_callback_exceptions=True)

