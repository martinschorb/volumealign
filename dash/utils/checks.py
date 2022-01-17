#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 10:59:21 2021

@author: schorb
"""

from dash.dependencies import Input
import re

def makeinput(component,prop='value'):
    if type(component) == Input:
        return Input(component.component_id, prop)
    elif type(component) == str:
        return Input(component, prop)
    elif type(component) ==dict:
        return Input(component, prop)
    else:
        raise TypeError('Component description needs to be string, valid dash dictionary or dash.dependencies.Input!')


def clean_render_name(instr):
    return re.sub('[^a-zA-Z0-9_]','_',instr)

def is_bad_filename(instr):
    return len(re.findall('[^a-zA-Z0-9_./-]',instr))>0