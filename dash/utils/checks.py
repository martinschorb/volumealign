#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 18:01:50 2021

@author: schorb
"""

import re

def clean_render_name(instr):
    return re.sub('[^a-zA-Z0-9_]','_',instr)
    