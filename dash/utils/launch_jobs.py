#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:24:32 2020

@author: schorb
"""

import os
import subprocess


def args2string(args):
    if args==None:
        argstring=''
    elif type(args)==list:
        argstring=" ".join(map(str,args))
    elif type(args)==dict:
        argstring=str()
        for item in args.items():argstring+=' '+' '.join(map(str,item))
    elif type(args)==str:
        argstring=args
    else:
        raise TypeError('ERROR! command line arguments need to be passed as string, list or dict.')
    return argstring

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
            slurm_args = args2string(target_args)
            
        
        slurm_args += '-e '+errfile+' -o '+logfile
        
        command = 'sbatch '+slurm_args+' '+command+' '+args2string(run_args)
        
        os.system('echo waiting for cluster job to start > '+logfile)
	
        print(command)
	
        p = subprocess.Popen(command, shell=True, env=my_env, executable='bash')
           
        return p
       
        
     
if __name__ == '__main__':
    run()    
