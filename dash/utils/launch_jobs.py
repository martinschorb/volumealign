#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:24:32 2020

@author: schorb
"""

import os
import subprocess


def run(target='standalone',pyscript=None,json=None,run_args=None,logfile='/g/emcf/schorb/render-output/render.out',errfile='/g/emcf/schorb/render-output/render.err' ):
    
    command = 'bash ../'+target
    command += '/launcher.sh'

    
    
    with open(logfile,"wb") as out, open(errfile,"wb") as err:
        subprocess.Popen(command, stdout=out,stderr=err, shell=True)
   
        
    
        
    
    
    