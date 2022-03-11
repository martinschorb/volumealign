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
import psutil
import requests


def args2string(args,separator='='):
    """
    Converts arguments as list or dict into a tring to be issued on CLI

    :param args: list, dict or str of command line arguments
    :param str separator: char to separate/link arguments
    :return: string of arguments
    """

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
    """
    Top level function to return a string description of the processing status of a (multi-task) run_state dictionary.

    A run_state dict contains:
        - 'status': string describing the processing status of ALL tasks
        - 'type': string describing the type of compute infrastructure to be used. Currently supports ['standalone','generic','slurm','sparkslurm']
        - 'logfile': string path pointing to the/a log file of the processing run.
        - 'id':  ID of the processing task. Can be a single string to describe one task or a dict containing a list of task IDs:
            allowed keys: - 'par' for parallel tasks or 'seq' for sequential tasks. These are exclusive and contain lists of job IDs
                          - 'logfiles': list of individual log files for the tasks.


    :param dict run_state: run state dictionary defining job ID(s), job type and logfile(s)
    :return: string describing the global processing status and link to status page if available
    """

    res_status,link = checkstatus(run_state)
    # print(run_state)
    # print('res_status:')
    # print(res_status)

    if res_status is None:
        return 'input',link

    out_stat=''

    if type(res_status) is str:
        if res_status=='error':
            out_stat = 'Error while excecuting '+str(run_state['id'])+'.'
        else:
            out_stat=res_status
    
    # ONLY single processes/jobs for now!
    
    elif type(res_status) is list:
        if 'error' in res_status:
            out_stat = 'Error while excecuting '+str(run_state['id'])+'.'
        elif 'running' in res_status:
            out_stat = 'running'
        elif 'pending' in res_status:
            out_stat = 'pending'
        elif 'cancelled' in res_status:
            out_stat = 'Cluster Job '+run_state['id']+' was cancelled.'
        elif 'timeout' in res_status:
            out_stat = 'Cluster Job '+run_state['id']+' was cancelled due to a timeout. Try again with longer time constraint.'
        elif 'Problem connecting to Spark!' in res_status:
            out_stat = res_status
        elif 'Spark app was killed.' in res_status:
            out_stat = res_status
        elif all(item=='done' for item in res_status):
            out_stat = 'done'

    return out_stat, link


def checkstatus(run_state):
    """
    check the status of one or multiple processing job(s). Contains process monitoring for local jobs.
    returns a status string and a link to status page if available

    :param dict run_state: single or multi-task run_state dict
    :return: status string and link
    """
    outstat=[]
    runvars = [run_state['id']]
    j_id = run_state['id']

    if type(j_id) == dict:
        if 'par' in j_id.keys():
            runvars = [job for job in j_id['par']]
        elif 'seq' in j_id.keys():
            runvars = [job for job in j_id['seq']]
    
    if run_state['type'] == 'standalone':

        if run_state['status'] in ['running','launch']:
            for runvar in runvars:
                if psutil.pid_exists(runvar):
                    p = psutil.Process(runvar)

                    if p.is_running():
                        if not p.status() == 'zombie':
                            outstat.append('running')

                if os.path.exists(run_state['logfile']+'_exit'):
                    outstat.append('error')
                else:
                    outstat.append('done')

            return outstat,''

        else:
            return run_state['status'],''

    else:
        return cluster_status(run_state)



            
def cluster_status(run_state):
    """
    Check a single or multiple cluster job(s) run state

    :param dict run_state: single- or multi-task run_state dictionary
    :return: status string and link to status page if available
    """

    my_env = os.environ.copy()
    out_stat=list()
    link=''

    j_ids = [run_state['id']]

    if j_ids==['']:
        return 'wait',link

    cl_type = run_state['type']
    logfile = run_state['logfile']
    if cl_type == 'slurm':
            command =  'sacct --jobs='
            command += ','.join(map(str,j_ids))
            command += ' --format=jobid,state --parsable'
            
    elif cl_type == 'sparkslurm':
            
            command =  'sacct --jobs='
            command += ','.join(map(str,j_ids))
            command += ' --format=jobid,state,node --parsable'
            
        # commands for other cluster types go HERE
            
            
    result = subprocess.check_output(command, shell=True, env=my_env, stderr=subprocess.STDOUT)
        
    if cl_type == 'slurm':

        slurm_stat0 = result.decode()

        stat_list = slurm_stat0.split('\n')

        #check for master job
        slurm_stat=''

        for job_item in stat_list[1:]:
            jobstat = job_item.split('|')
            if len(jobstat)<2:
                continue

            if jobstat[0] in j_ids:
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
        else:
            out_stat.append('launch')

    elif cl_type == 'sparkslurm':
        slurm_stat = []
        slurm_stat0 = result.decode()

        stat_list = slurm_stat0.split('\n')

        #check for master job

        masterjoblist = [job+'+0' for job in map(str,j_ids)]

        for job_item in stat_list[1:]:
            jobstat = job_item.split('|')

            if jobstat[0] in masterjoblist:
                # master job
                masterhost = jobstat[2]
                slurm_stat = jobstat[1]

        if 'RUNNING' in slurm_stat:

            sp_masterfile = os.path.join(logfile.rsplit(os.extsep)[0],'spark-master-' + str(j_id),'master')

            if not os.path.exists(sp_masterfile): return ['launch'],link

            with open(sp_masterfile) as f: sp_master=f.read().strip('\n')

            link = '__' + sp_master
            url = 'http://' + sp_master + ':' + params.spark_port + '/json/'

            try:
                sp_query = requests.get(url).json()
            except:
                print('Problem connecting to Spark: ' + url)
                out_stat.append('Problem connecting to Spark!')
                return out_stat, link

            if sp_query['activeapps'] == []:
                if sp_query['workers'] ==[]:
                    out_stat.append('Startup Spark')
                else:
                    t_format = "%Y%m%d%H%M%S"
                    e_starttime = sp_query['workers'][0]['id'].strip('worker-').split('-1')[0]
                    now = datetime.datetime.now().strftime(t_format)

                    if int(now) - int(e_starttime) < 45:
                        out_stat.append('Startup Spark')
                    else:
                        if sp_query['completedapps'] == []:
                            print('Error in Spark setup!')
                            out_stat.append('error')
                        else:
                            if 'FINISHED' in sp_query['completedapps'][0]['state']:
                                out_stat.append(canceljobs(run_state,'done'))
                                donefile = run_state['logfile']+'.done'
                                with open(donefile,'w') as f:
                                    f.write('spark job: '+j_id + ' is done.')

                            elif 'KILLED' in sp_query['completedapps'][0]['state']:
                                drop = canceljobs(run_state)
                                out_stat.append('Spark app was killed.')
                            else:
                                out_stat.append('running')
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
            if run_state['status'] == 'done':
                out_stat.append('done')
            else:
                out_stat.append('cancelled')
        else:
            out_stat.append('launch')

    return out_stat,link

def find_runningjob(run_state):
    """
    Identifies which job is curently running from a set of sequential tasks

    :param dict run_state: multi-task run_state dictionary with sequential tasks
    :return: single JobID, path to associated log file
    """

    for idx,job in enumerate(run_state['id']['seq']):
        thisstate = run_state.copy()
        thisstate['id'] = job
        if cluster_status(thisstate) in ['pending','running']:
            return job,run_state['id']['logfiles'][idx]
    #no job found
    return None,run_state['logfile']

def canceljobs(run_state, out_status='cancelled'):
    """
    cancel one/multiple cluster processing jobs

    :param dict run_state: multi-task run_state dictionary
    :param str out_status: status string to keep when canceling
    :return: status string
    """
    j_id = run_state['id']

    if type(j_id)==dict:
        if 'par' in j_id.keys():
            for job in j_id['par']:
                thisstate = run_state.copy()
                thisstate['id']=job
                cstat = canceljobs(thisstate)

            return out_status

        elif 'seq' in j_id.keys():
            j_id,logfile = find_runningjob(run_state)

    cl_type = run_state['type']

    if 'slurm' in cl_type:
        command = 'scancel ' + str(j_id)
        os.system(command)
    elif 'standalone' in cl_type or 'generic' in cl_type:
        command = 'kill ' + str(j_id)
        os.system(command)

    return out_status


def run(target='standalone',
        pyscript='thispyscript',
        jsonfile='',
        run_args='',
        target_args=None,
        special_args=None,
        logfile=os.path.join(params.render_log_dir,'render.out'),
        errfile=os.path.join(params.render_log_dir,'render.err')):
    """
    Launcher of a processing task.

    :param str target: target for processing. Currently supports ['standalone','generic','slurm','sparkslurm']
    :param str pyscript: script to execute
    :param jsonfile: string path of JSON file with the script parameters or list of those for multiple parallel tasks
    :param run_args: str, dict or list with run-time arguments for the specific launcher
    :param target_args: str, dict or list with setup arguments for the specific launcher
    :param special_args: str, dict or list with additional arguments
    :param str logfile: path to log file
    :param str errfile: path to error log
    :return: Job ID (str)
    """

    if type(jsonfile) is list:
        # multiple parallel tasks to be initiated

        outids = []
        for curr_json in jsonfile:
            outids.append(run(target=target,pyscript=pyscript,run_args=run_args,target_args=target_args,
                              special_args=special_args,logfile=logfile,errfile=errfile,
                              jsonfile=curr_json)
                          )

        return {'par':outids}

    my_env = os.environ.copy()

    logbase = os.path.basename(logfile).rstrip('.log')
    logdir = os.path.dirname(logfile)

    runscriptfile = os.path.join(logdir, logbase + '.sh')

    if run_args is None: run_args = ''

    runscript = '#!/bin/bash \n'
    runscript += activate_conda()
    runscript += '\n'
    runscript += '#launch message \n'
    runscript += 'python ' + pyscript
    runscript += ' --input_json ' + jsonfile
    runscript += args2string(run_args)

    print('launching - ')

    if target=='standalone':
        command = 'bash ' + runscriptfile

        runscript.replace('#launch message','echo "Launching Render standalone processing script on " `hostname`')
        runscript += ' || echo $? > ' + logfile + '_exit'

        with open(runscriptfile, 'a') as f:
            f.write(runscript)

        print(command)

        with open(logfile,"wb") as out, open(errfile,"wb") as err:
            p = subprocess.Popen(command, stdout=out,stderr=err, shell=True, env=my_env, executable='bash')

            return p.pid
    
    elif target == 'generic':
        command = pyscript        
        command += ' '+run_args
        
        print(command)
        
        with open(logfile,"wb") as out, open(errfile,"wb") as err:
            p = subprocess.Popen(command, stdout=out,stderr=err, shell=True, env=my_env, executable='bash')
           
        return p
    
    elif target == 'slurm':
        runscript.replace('#launch message','"Launching Render processing script on " `hostname`". Slurm job ID: " $SLURM_JOBID"."')

        with open(runscriptfile, 'a') as f:
            f.write(runscript)

        command = runscriptfile

        if target_args==None:
            slurm_args = '-N1 -n1 -c4 --mem 4G -t 00:02:00 -W '
        else:
            slurm_args = args2string(target_args)

        slurm_args += '-e ' + errfile + ' -o ' + logfile
        
        sl_command = 'sbatch '+ slurm_args + ' ' + command
        
        print(sl_command)

        p = subprocess.Popen(sl_command, shell=True, env=my_env, executable='bash', stdout=subprocess.PIPE)

        with open(logfile,'w+') as f:
            f.write('waiting for cluster job to start\n\n')
            time.sleep(3)
            jobid = p.stdout.readline().decode()
            
            f.write(jobid)
            
            jobid=jobid.strip('\n')[jobid.rfind(' ')+1:]
            
            #jobid=['slurm__'+jobid]
        
        return jobid
    
    elif target == 'sparkslurm':

        command = params.launch_dir + '/launcher_' + target
        command += '.sh '
        
        target_args['--email'] = params.user + params.email
        target_args['--template'] = os.path.join(params.launch_dir,"spark_slurm_template.sh")

        logbase = logfile.partition('.log')[0]
        
        target_args['--runscript'] = logbase + '.' + target + '.sh'
                
        spsl_args = args2string(target_args)  
        
        # spsl_args += args2string({'--logfile':logfile})
        # spsl_args += args2string({'--errfile':errfile})
        spsl_args += args2string({'--logdir':logbase})

        spark_args = dict()
        if type(special_args) is dict:
            spark_args.update(special_args)

        spark_args['--class'] = pyscript
        spark_args['--logdir'] = logbase
        spark_args['--spark_home'] = params.spark_dir
        spark_args['--render_dir'] = params.render_dir
        
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
        return jobid

        
def run_prefix(nouser=False,dateonly=False):
    """
    Creates a specific prefix for outputs (logfiles, directories)

    :param bool nouser: do not include the user name
    :param bool dateonly: only use the date, not the time
    :return: string prefix that can be incorporated in file/path names
    """

    timestamp = time.localtime()
    user=''
    if not nouser:
        user = params.user + '_'

    if dateonly:
        t='{}{:02d}{:02d}'.format(timestamp.tm_year,timestamp.tm_mon,timestamp.tm_mday)
    else:
        t='{}{:02d}{:02d}-{:02d}{:02d}'.format(timestamp.tm_year,timestamp.tm_mon,timestamp.tm_mday,timestamp.tm_hour,timestamp.tm_min)

    return user + t


def activate_conda(conda_dir=params.conda_dir,
                   env_name=params.render_envname):
    """
    activates a conda environment to run a processing script

    :param str conda_dir: directory of the *conda installation
    :param str env_name: environment name
    :return: multi-line string to be issued as a shell command
    """

    script = ''
    script += 'source '+os.path.join(conda_dir,"etc/profile.d/conda.sh")+'\n'
    script += '\n'
    script += 'conda activate ' + env_name + '\n'

    return script
