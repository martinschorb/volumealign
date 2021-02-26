#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:24:32 2020

@author: schorb
"""

import os
import subprocess
import params
import time


import requests
import json


workdir = params.workdir


def args2string(args,separator='='):
    if args==None:
        argstring=''
    elif type(args)==list:
        argstring=" ".join(map(str,args))
    elif type(args)==dict:
        argstring=str()
        for item in args.items():
            if type(item[1]) is list:
                argstring+=' '+' '.join([str(item[0]) + separator + currit for currit in item[1]])
            else:
                argstring+=' '+separator.join(map(str,item))
    elif type(args)==str:
        argstring=args
    else:
        raise TypeError('ERROR! command line arguments need to be passed as string, list or dict.')
    
    argstring+=' '
    
    return argstring


def status(processes,logfile):
    res_status,processes = checkstatus(processes,logfile) 
    
    if res_status=='error':
        out_stat = 'Error while excecuting '+processes+'.'
    else:
        out_stat=res_status
    
    if type(res_status) is list:
        out_stat='wait'
        # multiple cluster job IDs
        if 'error' in res_status:
            out_stat = 'Error while excecuting '+processes[res_status.index('error')]+'.'
        elif 'running' in res_status:
            out_stat = 'running'
        elif 'pending' in res_status:
            out_stat = 'pending'
        elif 'cancelled' in res_status:
            out_stat = 'Cluster Job '+processes[res_status.index('cancelled')]+' was cancelled.'
        elif 'timeout' in res_status:
            out_stat = 'Cluster Job '+processes[res_status.index('timeout')]+' was cancelled due to a timeout. Try again with longer time constraint.'
        elif all(item=='done' for item in res_status):
            out_stat = 'done'
        
        
    
    return out_stat


def checkstatus(runvar,logfile):    
    if type(runvar) is subprocess.Popen:
        if runvar.poll() is None:
            return 'running',runvar
        
        elif runvar.poll() == 0:
            return 'done',None
            
        else:
            return 'error',runvar.args
    
    elif type(runvar) is str:
        return cluster_status(runvar,logfile),[runvar]
        
    if type(runvar) is list:
        outvar=list()
        for rv in runvar:
            if type(rv) is subprocess.Popen:
                if rv.poll() is None:
                    outvar.append(rv)
                elif rv.poll() > 0:
                    return 'error',rv.args
            elif type(rv) is str:
                return cluster_status(runvar,logfile),runvar 
            
            
        if len(outvar)>1:
            return 'running',outvar
        elif len(outvar)==1:
            return 'running',rv
        else:
            return 'done',outvar        



def cluster_status_init(job_ids):
    out_ids=list()
    out_type=list()
    if type(job_ids) is str:
        job_ids=[job_ids]
    
    if type(job_ids) is not list:
        raise TypeError('ERROR! JOB IDs need to be passed as list of strings with cluster type __ ID!')
        
    for jobid in job_ids:
        if (type(jobid) is not str or not '__' in jobid): raise TypeError('ERROR! JOB IDs need to be passed as string with cluster type __ ID!')
        
        cl_type = jobid[:jobid.find('__')]
        out_type.append(cl_type)
        j_id = jobid[jobid.rfind('__')+2:]
        out_ids.append(j_id)
                      
    return out_ids,out_type



            
def cluster_status(job_ids,logfile):
    my_env = os.environ.copy()
    out_stat=list()
    
    j_ids,j_types = cluster_status_init(job_ids)
    
    for j_idx,j_id in enumerate(j_ids):
    
        cl_type = j_types[j_idx]
        
        if cl_type == 'slurm':
            command =  'sacct --jobs='
            command += j_id
            command += ' --format=jobid,state --parsable'
            
        elif cl_type == 'sparkslurm':
            
            
            command = 'cat /g/emcf/schorb/code/volumealign/sslurm'
            
            
            # command =  'sacct --jobs='
            # command += j_id
            # command += ' --format=jobid,state,node --parsable'
        # commands for other cluster types go HERE
            
            
        result = subprocess.check_output(command, shell=True, env=my_env, stderr=subprocess.STDOUT)
        
        if cl_type == 'slurm':
            
            
            slurm_stat0 = result.decode()
            
            stat_list = slurm_stat0.split('\n')
            
            #check for master job
            
            for job_item in stat_list[1:]:
                jobstat = job_item.split('|')
                
                if jobstat[0] == j_id:
                    slurm_stat = jobstat[1] 
               
            if 'RUNNING' in slurm_stat:
                out_stat.append('running')
            elif slurm_stat=='COMPLETED':
                out_stat.append('done')
            elif 'FAILED' in slurm_stat:
                out_stat.append('error')
            elif 'TIMEOUT' in slurm_stat:
                out_stat.append('timeout')    
            elif 'PENDING' in slurm_stat:
                out_stat.append('pending')
            elif 'CANCELLED' in slurm_stat:
                out_stat.append('cancelled')
                
        elif cl_type == 'sparkslurm':
            slurm_stat = []
            slurm_stat0 = result.decode()
            
            stat_list = slurm_stat0.split('\n')
            
            #check for master job
            
            for job_item in stat_list[1:]:
                jobstat = job_item.split('|')
                
                if jobstat[0] == j_id + '+0':
                    # master job
                    masterhost = jobstat[2]
                    slurm_stat = jobstat[1] 
            
            
            if 'RUNNING' in slurm_stat:   
                
                sp_masterfile = os.path.join(logfile.rsplit(os.extsep)[0],'spark-master-' + j_id,'master')
                
                with open(sp_masterfile) as f: sp_master=f.read()

                url = sp_master + '/json/'

                sp_query = requests.get(url).json() 
                
                if sp_query['activeapps'] == []:
                    if sp_query['workers'] ==[]:
                        out_stat.append('Startup Spark')
                    else:
                        e_starttime = sp_query['workers'][0]['id'].strip('worker-').split('-1')[0]
                    
                else:
                    print('spark running')
                    out_stat.append(sp_query['activeapps'][0]['state'].lower())
                
                
            elif slurm_stat=='COMPLETED':
                out_stat.append('done')
            elif 'FAILED' in slurm_stat:
                out_stat.append('error')
            elif 'TIMEOUT' in slurm_stat:
                out_stat.append('timeout')    
            elif 'PENDING' in slurm_stat:
                out_stat.append('pending')
            elif 'CANCELLED' in slurm_stat:
                out_stat.append('cancelled')

    return out_stat







        
def canceljobs(job_ids):
    out_status=list()
    j_ids,j_types=cluster_status_init(job_ids)

    for j_idx,j_id in enumerate(j_ids):
    
        cl_type = j_types[j_idx]
        
        if 'slurm' in cl_type:
            command = 'scancel '+j_id
            os.system(command)
        
    
    out_status = 'cancelled'
    
    
    return out_status
        
    
    
    

def run(target='standalone',pyscript='thispyscript',json='JSON',run_args=None,target_args=None,logfile='/g/emcf/schorb/render-output/render.out',errfile='/g/emcf/schorb/render-output/render.err'):
    my_env = os.environ.copy()
    os.chdir(workdir)
    command = '../'+target
    command += '/launcher.sh '    
    
    
    # DEBUG function.......
    
    # command = 'hostname '
    
    # for i in range(10): command+='&& sleep 1 && echo '+str(i)
    print('launching - ')
    
    if target=='standalone':
        command += pyscript
        command += ' '+json
        
        print(command)

        
        with open(logfile,"wb") as out, open(errfile,"wb") as err:
            p = subprocess.Popen(command, stdout=out,stderr=err, shell=True, env=my_env, executable='bash')
           
        return [p]
    
    elif target == 'slurm':
        
        command += pyscript
        command += ' '+json
        
        if target_args==None:
            slurm_args = '-N1 -n1 -c4 --mem 4G -t 00:02:00 -W '
        else:
            slurm_args = args2string(target_args)
            
        
        slurm_args += '-e ' + errfile + ' -o ' + logfile
        
        sl_command = 'sbatch '+ slurm_args + ' ' + command + ' ' + args2string(run_args)
        
        print(sl_command)

        p = subprocess.Popen(sl_command, shell=True, env=my_env, executable='bash', stdout=subprocess.PIPE)
        
        
        with open(logfile,'w+') as f:
            f.write('waiting for cluster job to start\n\n')
            time.sleep(3)
            jobid = p.stdout.readline().decode()
            
            f.write(jobid)
            
            jobid=jobid.strip('\n')[jobid.rfind(' ')+1:]
            
            jobid=['slurm__'+jobid]
            
        
        return jobid
    
    elif target == 'sparkslurm':
        
        target_args['--email'] = params.user + params.email
        
        logbase = logfile.partition('.log')[0]
        
        target_args['--runscript'] = logbase + '.' + target + '.sh'
                
        spsl_args = args2string(target_args)  
        
        # spsl_args += args2string({'--logfile':logfile})
        # spsl_args += args2string({'--errfile':errfile})
        spsl_args += args2string({'--logdir':logbase})
 
        
        spark_args = dict()
        spark_args['--class'] = pyscript
        spark_args['--logdir'] = logbase
                
        
        spsl_args += '--scriptparams= ' + args2string(spark_args) 
        spsl_args += '--params= ' + args2string(run_args,' ')
        
        
        command += spsl_args
        
        p = subprocess.Popen(command, shell=True, env=my_env, executable='bash', stdout=subprocess.PIPE)
        
        print(command)
        
        with open(logfile,'w+') as f:
            f.write('waiting for cluster job to start\n\n')
            time.sleep(3)
            jobid = p.stdout.readline().decode()
            
            f.write(jobid)
            
            jobid=jobid.strip('\n')[jobid.rfind(' ')+1:]
            
            jobid=['sparkslurm__'+jobid]
        
        return jobid
       
        
     
if __name__ == '__main__':
    run()    
