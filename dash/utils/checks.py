#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 10:59:21 2021

@author: schorb
"""

from dash.dependencies import Input

def makeinput(component,prop='value'):    
    if type(component) == Input:
        return Input(component.component_id, prop)
    elif type(component) == str:
        return Input(component, prop)
    elif type(component) ==dict:
        return Input(component, prop)
    else:
        raise TypeError('Component description needs to be string, valid dash dictionary or dash.dependencies.Input!')