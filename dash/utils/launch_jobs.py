#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:24:32 2020

@author: schorb
"""

import os
import subprocess


def run(target='standalone',pyscript='thispyscript',json='JSON',run_args=None,logfile='/g/emcf/schorb/render-output/render.out',errfile='/g/emcf/schorb/render-output/render.err'):
    my_env = os.environ.copy()
    command = '../'+target
    command += '/launcher.sh '
    command += pyscript
    command += ' '+json
    
    
    
    # DEBUG function.......
    
    command = 'hostname '
    
    for i in range(10): command+='&& sleep 1 && echo '+str(i)
    


    
    with open(logfile,"wb") as out, open(errfile,"wb") as err:
        p = subprocess.Popen(command, stdout=out,stderr=err, shell=True, env=my_env, executable='bash')
   
        
    return p
     
if __name__ == '__main__':
    run()    