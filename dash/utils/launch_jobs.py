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
import datetime

import requests

from gc3libs.session import Session

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


def status(run_state):   
        
    res_status = checkstatus(run_state) 

    link=''

    if res_status is None:
        return 'input',link


    if type(res_status) is str:
        if res_status=='error':
            out_stat = 'Error while excecuting '+str(run_state['id'])+'.'
        else:
            out_stat=res_status
    
    # ONLY single processes/jobs for now!
    
    elif type(res_status) is list:
    #     out_stat='wait'
    #     # print(res_status)
    #     for idx,item in enumerate(res_status):

    #         link = ''
    #         if '__' in item:
    #             res_status[idx] = item.split('__')[0]
    #             link = item.split('__')[1]

    #     # multiple cluster job IDs
        if 'error' in res_status:
            out_stat = 'Error while excecuting '+str(run_state['id'])+'.'
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
    
    return out_stat , link


def checkstatus(run_state):

    logfile = run_state['logfile']
    
    runvar = run_state['id']
    
    if run_state['type'] == 'standalone':
        if run_state['status'] in ['running','launch']:

            if runvar in params.processes.keys():
                p = params.processes[runvar]

                if p.poll() is None:
                    return 'running'

                elif p.poll() == 0:
                    params.processes.pop(runvar)
                    return 'done'

                else:
                    params.processes.pop(runvar)
                    return 'error'
        else:
            return run_state['status']
         
         
    
    elif run_state['type'].startswith('gc3_'):
        return gc3_status(run_state)

    #     else:
    #         return cluster_status(runvar,logfile),[runvar]

    
    # if type(runvar) is list:
    #     outvar=list()
    #     for rv in runvar:
    #         if type(rv) is subprocess.Popen:
    #             if rv.poll() is None:
    #                 outvar.append(rv)
    #             elif rv.poll() > 0:
    #                 return 'error',rv.args
    #         elif type(rv) is str:
    #             if runvar.startswith('gc3_'):
    #                 return gc3_status(runvar,logfile),runvar
    #             else:
    #                 return cluster_status(runvar,logfile),runvar
            
            
    #     if len(outvar)>1:
    #         return 'running',outvar
    #     elif len(outvar)==1:
    #         return 'running',rv
    #     else:
    #         return 'done',outvar


def gc3_status(run_state):
        
    gc3_sessiondir = run_state['type'].lstrip('gc3_')

    gc3_session = Session(gc3_sessiondir)

    if gc3_session ==[]:
        return 'error'

    out_statlist =[]

    for task in gc3_session.tasks.values():
        print(task.execution.state)

        if 'RUNNING' in task.execution.state:
            out_statlist.append('running')
        elif task.execution.state=='TERMINATED':
            print(task.execution.exitcode)

            if task.execution.exitcode > 0:
                out_statlist.append('error')
            elif task.execution.exitcode == 0:
                out_statlist.append('done')

        elif 'SUBMITTED' in task.execution.state:
            out_statlist.append('pending')
        elif 'FAILED' in task.execution.state:
            out_statlist.append('error')



    return out_statlist


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
    link=''
    
    j_ids,j_types = cluster_status_init(job_ids)
    
    for j_idx,j_id in enumerate(j_ids):
    
        cl_type = j_types[j_idx]
        
        if cl_type == 'slurm':
            command =  'sacct --jobs='
            command += j_id
            command += ' --format=jobid,state --parsable'
            
        elif cl_type == 'sparkslurm':                       
            
            command =  'sacct --jobs='
            command += j_id
            command += ' --format=jobid,state,node --parsable'
            
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
                
                with open(sp_masterfile) as f: sp_master=f.read().strip('\n')
                
                link = '__' + sp_master
                url = sp_master + '/json/' 
                
                try:
                    sp_query = requests.get(url).json() 
                except:
                    print('Problem connecting to Spark: ' + url)
                    out_stat.append('Problem connecting to Spark!')
                    return out_stat
                
                
                if sp_query['activeapps'] == []:                    
                    if sp_query['workers'] ==[]:
                        out_stat.append('Startup Spark')
                    else:
                        t_format = "%Y%m%d%H%M%S"
                        e_starttime = sp_query['workers'][0]['id'].strip('worker-').split('-1')[0]
                        now = datetime.datetime.now().strftime(t_format)
                        
                        if int(now) - int(e_starttime) < 45:
                            out_stat.append('Startup Spark' + link)
                        else:
                            if sp_query['completedapps'] == []: 
                                out_stat.append('Error in Spark setup!')
                            else:
                                if 'FINISHED' in sp_query['completedapps'][0]['state']:
                                    
                                    drop = canceljobs('sparkslurm__'+j_id)
                                    out_stat.append('done')
                                    
                                elif 'KILLED' in sp_query['completedapps'][0]['state']:
                                    
                                    drop = canceljobs('sparkslurm__'+j_id)
                                    out_stat.append('Spark app was killed.')
                                else:
                                    out_stat.append('running' + link)
                else:                    
                    out_stat.append(sp_query['activeapps'][0]['state'].lower() + link)
                
                
                
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
        
    
    
    

def run(target='standalone',
        pyscript='thispyscript',
        jsonfile='',
        run_args='',
        target_args=None,
        logfile=os.path.join(params.render_log_dir,'render.out'),
        errfile=os.path.join(params.render_log_dir,'render.err')):
    
    my_env = os.environ.copy()
    os.chdir(workdir)
    
    # # command = '../'+target
    # # command += '/launcher.sh '    
    # command = '../launchers/'+ target +'.sh'
    
    command = 'cd ' + params.launch_dir
        
    command += ' && '
    

    if run_args is None: run_args = ''
    
    
    # DEBUG function.......

    print('launching - ')
    
    if target.startswith('gc3_'):
        
        command += './gc3run.sh'
        
        resource = target.lstrip('gc3_')

        logbase = os.path.basename(logfile).rstrip('.log')

        gc3_session = os.path.join(os.path.dirname(logfile),'gc3_session_'+logbase)
        gc3_outdir = os.path.join(os.path.dirname(logfile),'gc3_session_'+logbase)
        
        command += ' -s ' + gc3_session
        command += ' -o ' + gc3_outdir
        command += ' -r ' + resource
        command += ' -C 5'  # poll every 5 seconds and trigger job launch
        command += ' --config-files ' + params.gc3_conffile
        
        if not target_args is None:
            command += args2string(target_args)  
        
        command += ' "./render_run.sh '
        command += params.launch_dir
        command += ' python ' + pyscript
        command += ' --input_json ' + jsonfile +'"'
        command += run_args
        
        print(command)
        
        with open(logfile,"wb") as out, open(errfile,"wb") as err:
            p = subprocess.Popen(command, stdout=out,stderr=err, shell=True, env=my_env, executable='bash')
         
        return gc3_session
    
    elif target=='standalone':
        command += pyscript
        command += ' '+jsonfile
        command += run_args
        
        print(command)
        
        with open(logfile,"wb") as out, open(errfile,"wb") as err:
            p = subprocess.Popen(command, stdout=out,stderr=err, shell=True, env=my_env, executable='bash')
            pid = p.pid
            
            params.processes[pid]=p
            
            return p.pid
    
    elif target == 'generic':
        command = pyscript        
        command += ' '+run_args
        
        print(command)
        
        with open(logfile,"wb") as out, open(errfile,"wb") as err:
            p = subprocess.Popen(command, stdout=out,stderr=err, shell=True, env=my_env, executable='bash')
           
        return p
    
    elif target == 'slurm':
        
        command += pyscript
        command += ' ' + jsonfile
        
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

        
def run_prefix():
    timestamp = time.localtime()
    user = os.getlogin()

    return user + '_{}{:02d}{:02d}-{:02d}{:02d}'.format(timestamp.tm_year,timestamp.tm_mon,timestamp.tm_mday,timestamp.tm_hour,timestamp.tm_min)


       
     
if __name__ == '__main__':
    run()    
