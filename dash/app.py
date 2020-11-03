#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 15:25:59 2020

@author: schorb
"""

import dash

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server