#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:24:32 2020

@author: schorb
"""

import os
import subprocess


def run(target='standalone',pyscript='thispyscript',json='JSON',run_args=None,target_args=None,logfile='/g/emcf/schorb/render-output/render.out',errfile='/g/emcf/schorb/render-output/render.err'):
    my_env = os.environ.copy()
    command = '../'+target
    command += '/launcher.sh '
    command += pyscript
    command += ' '+json
    
    
    
    # DEBUG function.......
    
    # command = 'hostname '
    
    # for i in range(10): command+='&& sleep 1 && echo '+str(i)
    
    if target=='standalone':
                
        with open(logfile,"wb") as out, open(errfile,"wb") as err:
            p = subprocess.Popen(command, stdout=out,stderr=err, shell=True, env=my_env, executable='bash')
           
        return p
    
    elif target == 'slurm':
        
        if target_args==None:
            slurm_args = '-N1 -n1 -c 8 --mem 8G -t 00:10:00 -W '
        else:
            slurm_args = target_args
            
        
        slurm_args += '-e '+errfile+' -o '+logfile
        
        
        
        command = 'srun '+slurm_args+' '+command
        
        os.system('echo waiting for cluster job to start > '+logfile)
        
	
        p = subprocess.Popen(command, shell=True, env=my_env, executable='bash')
           
        return p
       
        
     
if __name__ == '__main__':
    run()    
