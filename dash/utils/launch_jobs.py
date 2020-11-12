#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:24:32 2020

@author: schorb
"""

import os
import subprocess


def run(target='standalone',pyscript=None,json=None,run_args=None,logfile='~/render.log'):
    
    if target=='standalone':
        p=subprocess.run('echo here I am '+'123f'+json+' > '+logfile,shell=True)
        
    
        
    
    
    