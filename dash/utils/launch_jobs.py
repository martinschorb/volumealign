#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:24:32 2020

@author: schorb
"""

import os
import subprocess
import params

workdir = params.workdir


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


def checkstatus(runvar):    
    if type(runvar) is subprocess.Popen:
        if runvar.poll() is None:
            return 'running',runvar
        
        elif runvar.poll() == 0:
            return 'done',None
            
        else:
            return 'error',runvar
    
    elif type(runvar) is str:
        return cluster_status(runvar),[runvar]
        
    if type(runvar) is list:
        outvar=list()
        for rv in runvar:
            if type(rv) is subprocess.Popen:
                if rv.poll() is None:
                    outvar.append(rv)
                elif rv.poll() > 0:
                    return 'error',rv
            elif type(rv) is str:
                return cluster_status(rv),outvar 
            
            
        if len(outvar)>1:
            return 'running',outvar
        elif len(outvar)==1:
            return 'running',rv
        else:
            return 'done',outvar        
               

            
def cluster_status(job_ids):
    
    out_stat=list
    
    if type(job_ids) is str:
        job_ids=[job_ids]
    
    if type(job_ids) is not list:
        raise TypeError('ERROR! JOB IDs need to be passed as list of strings with cluster type __ ID!')
        
    for jobid in job_ids:
        if (type(jobid) is not str or not '__' in jobid): raise TypeError('ERROR! JOB IDs need to be passed as string with cluster type __ ID!')
        
        cl_type = jobid[:jobid.find('__')]
        j_id = jobid[jobid.rfind('__')+2:]
        
        if cl_type == 'slurm':
            command =  'sacct --jobs='
            command += j_id
            command += '--format=state'
            
        # commands for other cluster types go HERE
            
            
        result = subprocess.check_output(command, stderr=subprocess.STDOUT)
        
        if cl_type == 'slurm':
            slurm_stat = result.splitlines()[-1].decode()
            
            if slurm_stat=='RUNNING':
                out_stat.append('running')
            elif slurm_stat=='COMPLETED':
                out_stat.append('done')
            elif slurm_stat=='FAILED':
                out_stat.append('error')
                
        
    return out_stat
        
        
        

def run(target='standalone',pyscript='thispyscript',json='JSON',run_args=None,target_args=None,logfile='/g/emcf/schorb/render-output/render.out',errfile='/g/emcf/schorb/render-output/render.err'):
    my_env = os.environ.copy()
    os.chdir(workdir)
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
