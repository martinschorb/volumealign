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
        elif all(item=='done' for item in res_status):
            out_stat = 'done'

    return out_stat, link


def checkstatus(run_state):

    runvar = run_state['id']
    
    if run_state['type'] == 'standalone':

        if run_state['status'] in ['running','launch']:

            if psutil.pid_exists(runvar):
                p = psutil.Process(runvar)

                if p.is_running():
                    if not p.status() == 'zombie':
                        return 'running',''



            if os.path.exists(run_state['logfile']+'_exit'):
                return 'error',''

            else:
                return 'done',''
        else:
            return run_state['status'],''

    else:
        return cluster_status(run_state)



            
def cluster_status(run_state):
    my_env = os.environ.copy()
    out_stat=list()
    link=''

    j_id = run_state['id']

    if j_id=='':
        return 'wait',link

    cl_type = run_state['type']
    logfile = run_state['logfile']
    if cl_type == 'slurm':
            command =  'sacct --jobs='
            command += str(j_id)
            command += ' --format=jobid,state --parsable'
            
    elif cl_type == 'sparkslurm':
            
            command =  'sacct --jobs='
            command += str(j_id)
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
        else:
            out_stat.append('launch')

    elif cl_type == 'sparkslurm':
        slurm_stat = []
        slurm_stat0 = result.decode()

        stat_list = slurm_stat0.split('\n')

        #check for master job

        for job_item in stat_list[1:]:
            jobstat = job_item.split('|')

            if jobstat[0] == str(j_id) + '+0':
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
                        out_stat.append('Startup Spark' + link)
                    else:
                        if sp_query['completedapps'] == []:
                            out_stat.append('Error in Spark setup!')
                        else:
                            if 'FINISHED' in sp_query['completedapps'][0]['state']:
                                out_stat.append(canceljobs(run_state,'done'))

                            elif 'KILLED' in sp_query['completedapps'][0]['state']:
                                drop = canceljobs(run_state)
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
            if run_state['status'] == 'done':
                out_stat.append('done')
            else:
                out_stat.append('cancelled')
        else:
            out_stat.append('launch')

    return out_stat[0],link


def canceljobs(run_state, out_status='cancelled'):

    j_id = run_state['id']
    
    cl_type = run_state['type']
        
    if 'slurm' in cl_type:
        command = 'scancel '+str(j_id)
        os.system(command)


    return out_status


def run(target='standalone',
        pyscript='thispyscript',
        jsonfile='',
        run_args='',
        target_args=None,
        logfile=os.path.join(params.render_log_dir,'render.out'),
        errfile=os.path.join(params.render_log_dir,'render.err')):
    
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


    
    # DEBUG function.......

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
    script = ''
    script += 'source '+os.path.join(conda_dir,"etc/profile.d/conda.sh")+'\n'
    script += '\n'
    script += 'conda activate ' + env_name + '\n'

    return script

     
if __name__ == '__main__':
    run()    
