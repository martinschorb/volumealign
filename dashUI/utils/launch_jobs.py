#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:24:32 2020

@author: schorb
"""

import os
import subprocess

import dash

from dashUI import params
import time
import datetime
import psutil
import paramiko
import requests


def args2string(args, separator='='):
    """
    Converts arguments as list or dict into a string to be issued on CLI.
    If a keyword argument contains a list, it will be issued multiple times.
    {'arg: [1,2,3]} -> ' arg=1 arg=2 arg=3 '
    This is according to what some Render CL scripts expect when defining
    multiple input files.

    :param args: list, dict or str of command line arguments
    :param str separator: char to separate/link arguments
    :return: string of arguments
    :rtype: str
    """

    if args is None:
        argstring = ''
    elif type(args) == list:
        argstring = ' ' + " ".join(map(str, args))
    elif type(args) == dict:
        argstring = str()
        for item in args.items():
            if type(item[1]) is list:
                argstring += ' ' + ' '.join([str(item[0]) + separator + str(currit) for currit in item[1]])
            else:
                argstring += ' ' + separator.join(map(str, item))
    elif type(args) == str:
        argstring = args
    else:
        raise TypeError('ERROR! command line arguments need to be passed as string, list or dict.')

    argstring += ' '

    return argstring


def activate_conda(conda_dir=params.conda_dir,
                   env_name=params.render_envname):
    """
    activates a conda environment to run a processing script

    :param str conda_dir: directory of the *conda installation
    :param str env_name: environment name
    :return: multi-line string to be issued as a shell command
    :rtype: str
    """

    script = ''
    script += 'source ' + os.path.join(conda_dir, "etc/profile.d/conda.sh") + '\n'
    script += '\n'
    script += 'conda activate ' + env_name + '\n'

    return script


def run_command(remotehost, command, logfile, errfile):
    """
    Launcher to run a shell command either locally or on a remote host.

    :param str remotehost: The name of the remote host. If not specified in params, launch locally.
    :param str command: The shell command to launch.
    :param str logfile: The log file for the task.
    :param str errfile: The error log file for the task.
    :return: PID or remote PID of the launched task.
    :rtype: str or dict
    """

    my_env = os.environ.copy()

    print(command)

    if remotehost in params.remote_hosts:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
        ssh.connect(remotehost, username=remote_user(remotehost))

        command = 'echo $$ && ' + command

        command += ' >  ' + logfile + ' 2> ' + errfile + ' || echo $? > ' + logfile + '_exit'

        stdin, stdout, stderr = ssh.exec_command(command)

        remote_pid = stdout.readline().split('\n')[0]

        return {remotehost: remote_pid}

    else:
        with open(logfile, "wb") as out, open(errfile, "wb") as err:
            p = subprocess.Popen(command, stdout=out, stderr=err, shell=True, env=my_env, executable='bash')

        return p.pid


def submit_command(remotehost, command, logfile):
    """
    Launcher to run a shell command that submits a/multiple HPC job(s) either locally or on a remote host.

    :param str remotehost: The name of the remote host. If not specified in params, submit locally.
    :param str command: The shell command to submit the task. (needs to be available on the target system)
    :param str logfile: The log file for the submission.
    :return: JOBID of the submitted task.
    :rtype: str
    """

    my_env = os.environ.copy()

    if remotehost in params.remote_submission.keys():
        remotehost = params.remote_submission[remotehost]

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
        ssh.connect(remotehost, username=remote_user(remotehost), timeout=10)

        stdin, stdout, stderr = ssh.exec_command(command)
        time.sleep(3)
        jobid = stdout.readline()
    else:
        p = subprocess.Popen(command, shell=True, env=my_env, executable='bash', stdout=subprocess.PIPE)
        time.sleep(3)
        jobid = p.stdout.readline().decode()

    print(command)

    with open(logfile, 'w+') as f:
        f.write('waiting for cluster job to start\n\n')
        f.write(jobid)

    return jobid


def status(run_state):
    """
    Top level function to return a string description of the processing status of a (multi-task) run_state dictionary.

    A run_state dict contains:
        - 'status': string describing the processing status of ALL tasks
        - 'type': string describing the type of compute infrastructure to be used.
            Currently supports ['standalone','generic','slurm','sparkslurm']
        - 'logfile': string path pointing to the/a log file of the processing run.
        - 'id':  ID of the processing task. Can be a single string to describe one task
            or a dict containing a list of task IDs:
            allowed keys: - 'par' for parallel tasks or 'seq' for sequential tasks.
                            These are exclusive and contain lists of job IDs
                          - 'logfiles': list of individual log files for the tasks.


    :param dict run_state: run state dictionary defining job ID(s), job type and logfile(s)
    :return: string describing the global processing status and link to status page if available
    :rtype: (str, str)
    """
    run_state = dict(run_state)

    (res_status, link), logfile, jobs = checkstatus(run_state)

    if res_status is None:
        return 'input', link

    out_stat = ''

    if type(res_status) is str:
        if res_status == 'error':
            out_stat = 'Error while excecuting ' + str(jobs) + '.'
        else:
            out_stat = res_status

    elif type(res_status) is list:
        if 'error' in res_status:
            out_stat = 'Error while excecuting ' + str(jobs) + '.'
        elif 'running' in res_status:
            out_stat = 'running'
        elif 'pending' in res_status:
            out_stat = 'pending'
        elif 'cancelled' in res_status:
            out_stat = 'Cluster Job(s) ' + str(jobs) + ' cancelled.'
        elif 'timeout' in res_status:
            out_stat = 'Cluster Job(s) ' + str(
                jobs) + ' cancelled due to a timeout. Try again with longer time constraint.'
        elif 'Problem connecting to Spark!' in res_status:
            out_stat = res_status[0]
        elif 'Spark app was killed.' in res_status:
            out_stat = res_status[0]
        elif all(item == 'done' for item in res_status):
            out_stat = 'done'

    run_state['status'] = out_stat
    run_state['logfile'] = logfile

    return out_stat, link, run_state


def checkstatus(run_state):
    """
    check the status of one or multiple processing job(s). Contains process monitoring for local jobs.
    returns a status string and a link to status page if available

    :param dict run_state: single or multi-task run_state dict
    :return: status string/list of strings, link to job, current logfile, job list
    :rtype: (str or list, str, str, list)
    """

    outstat = []
    # runvars = [run_state['id']]
    j_id = run_state['id']
    logfile = run_state['logfile']

    jobs = j_id

    if type(j_id) is dict:
        if 'par' in j_id.keys():
            runvars = [job for job in j_id['par']]
            jobs = runvars
        elif 'seq' in j_id.keys():
            runjob, idx = find_activejob(run_state)
            newrunstate = run_state.copy()
            jobs = runjob
            if runjob is None:
                # all tasks are completed/failed
                newrunstate['id'] = j_id['seq']
                jobs = j_id['seq']
                return checkstatus(newrunstate)

            elif type(runjob) is dict:
                lastjob = j_id['seq'][idx - 1]
                newrunstate['id'] = lastjob

                if 'done' in checkstatus(newrunstate)[0][0]:
                    if 'logfile' not in runjob.keys():
                        runjob['logfile'] = os.path.splitext(logfile)[0] + '_' + str(idx) \
                                            + os.path.splitext(logfile)[-1]

                    # start next job with these parameters

                    nextjobid = run(inputs=runjob)
                    nextjob = newrunstate.copy()
                    nextjob['logfile'] = runjob['logfile']
                    nextjob['id'] = nextjobid

                    run_state['id']['seq'][idx] = nextjobid
                    return checkstatus(nextjob)
                else:
                    jobs = lastjob
                    return checkstatus(newrunstate)

            else:
                jobs = runjob
                newrunstate['id'] = runjob
                return checkstatus(newrunstate)

        elif 'localhost' not in j_id.keys() and not list(j_id.keys())[0] in params.remote_hosts:
            #         parameter list for next sequential job
            return 'pending', '', logfile, jobs

        else:
            runvars = [j_id]

    elif type(j_id) is list:
        runvars = j_id

    elif type(j_id) is int:
        runvars = [j_id]

    elif type(j_id) is str:
        runvars = [j_id]

    if run_state['type'] in ['standalone', 'generic', 'localhost'] or run_state['type'] in params.remote_hosts:
        if run_state['status'] in ['running', 'launch']:

            for runvar in runvars:

                if type(runvar) is dict:

                    # remote check
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
                    remotehost = list(runvar.keys())[0]
                    ssh.connect(remotehost, username=remote_user(remotehost), timeout=10)

                    command = 'ps aux | grep "' + params.user + ' *' + str(runvar[remotehost]) + ' "'

                    stdin, stdout, stderr = ssh.exec_command(command)
                    time.sleep(2)
                    res = stdout.readlines()

                    if len(res) > 0:
                        outstat.append('running')
                        continue
                    #
                    # elif run_state['status'] == 'launch':
                    #     outstat.append('launch')

                elif type(runvar) is int:
                    if psutil.pid_exists(runvar):

                        p = psutil.Process(runvar)

                        if p.is_running():
                            if not p.status() == 'zombie':
                                outstat.append('running')
                                continue
                else:
                    raise TypeError('JOB ID for standalone jobs needs to be dict (host:id) or int for local call.')

                if os.path.exists(run_state['logfile'] + '_exit'):
                    outstat.append('error')
                else:
                    outstat.append('done')

            return (outstat, ''), logfile, jobs

        else:
            return (run_state['status'], ''), logfile, jobs

    else:
        return cluster_status(run_state), logfile, jobs


def cluster_status(run_state):
    """
    Check a single or multiple cluster job(s) run state

    :param dict run_state: single- or multi-task run_state dictionary
    :return: status string and link to status page if available
    :rtype: (str, str)
    """

    my_env = os.environ.copy()
    out_stat = list()
    link = ''

    j_ids = run_state['id']

    if type(j_ids) is dict:
        if 'par' in j_ids:
            j_ids = j_ids['par']
        if 'seq' in j_ids:
            j_ids, idx = find_activejob(run_state)

    if type(j_ids) is str:
        j_ids = [j_ids]

    if j_ids == '':
        return 'wait', link

    cl_type = run_state['type']
    logfile = run_state['logfile']

    if cl_type == 'slurm':
        command = 'sacct --jobs='
        command += ','.join(map(str, j_ids))
        command += ' --format=jobid,state --parsable'

    elif cl_type == 'sparkslurm':
        command = 'sacct --jobs='
        command += ','.join(map(str, j_ids))
        command += ' --format=jobid,state,node --parsable'

        # commands for other cluster types go HERE
    if run_state['status'] in ['cancelled', 'error']:
        return run_state['status'], link

    if cl_type in params.remote_submission.keys():

        remotehost = params.remote_submission[cl_type]

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
        ssh.connect(remotehost, username=remote_user(remotehost))

        stdin, stdout, stderr = ssh.exec_command(command)

        result = ''.join(stdout.readlines())

    else:
        # check cluster status locally
        result = subprocess.check_output(command, shell=True, env=my_env, stderr=subprocess.STDOUT).decode()

    if cl_type == 'slurm':

        slurm_stat0 = result

        stat_list = slurm_stat0.split('\n')

        # check for master job
        slurm_stat = ''

        for job_item in stat_list[1:]:
            jobstat = job_item.split('|')
            if len(jobstat) < 2:
                continue

            if jobstat[0] in j_ids:
                slurm_stat = jobstat[1]

                if 'RUNNING' in slurm_stat:
                    out_stat.append('running')
                elif slurm_stat == 'COMPLETED':
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
        slurm_stat0 = result

        stat_list = slurm_stat0.split('\n')

        # check for master job

        masterjoblist = [job + '+0' for job in map(str, j_ids)]

        for job_item in stat_list[1:]:
            jobstat = job_item.split('|')

            if jobstat[0] in masterjoblist:
                # master job
                masterhost = jobstat[2]
                slurm_stat = jobstat[1]

        if 'RUNNING' in slurm_stat:

            sp_masterfile = os.path.join(logfile.rsplit(os.extsep)[0], 'spark-master-' + str(j_ids[0]), 'master')

            if not os.path.exists(sp_masterfile):
                return ['launch'], link

            with open(sp_masterfile) as f:
                sp_master = f.read().strip('\n')

            link = '__' + sp_master
            url = 'http://' + sp_master + ':' + params.spark_port + '/json/'

            try:
                sp_query = requests.get(url).json()
            except:
                print('Problem connecting to Spark: ' + url)
                out_stat.append('Problem connecting to Spark!')
                return out_stat, link

            if sp_query['activeapps'] == []:
                if sp_query['workers'] == []:
                    out_stat.append('Startup Spark')
                else:
                    time.sleep(10)
                    if sp_query['activeapps'] == []:
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
                                if 'FINISHED' in sp_query['completedapps'][-1]['state']:
                                    out_stat.append('done')
                                    donefile = run_state['logfile'] + '.done'
                                    with open(donefile, 'w') as f:
                                        f.write('spark job: ' + str(j_ids[0]) + ' is done.')

                                elif 'KILLED' in sp_query['completedapps'][0]['state']:
                                    drop = canceljobs(run_state)
                                    out_stat.append('Spark app was killed.')
                                else:
                                    out_stat.append('running')
                    else:
                        out_stat.append(sp_query['activeapps'][0]['state'].lower())

            else:
                out_stat.append(sp_query['activeapps'][0]['state'].lower())

        elif slurm_stat == 'COMPLETED':
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

    return out_stat, link


def find_activejob(run_state):
    """
    Identifies which job is currently running or the next one to run from a set of sequential tasks

    :param dict run_state: multi-task run_state dictionary with sequential tasks
    :return: single JobID, path to associated log file
    """

    if 'seq' not in run_state['id'].keys():
        raise TypeError('Jobs need to be sequential!')

    for idx, job in enumerate(run_state['id']['seq']):
        thisstate = run_state.copy()
        thisstate['id'] = job
        if checkstatus(thisstate) in ['pending', 'running']:
            return job, idx

        if type(job) is dict:
            # launch instructions for next job
            return job, idx

    # no job found
    return None, -1


def canceljobs(run_state, out_status='cancelled'):
    """
    cancel one/multiple cluster processing jobs

    :param dict run_state: multi-task run_state dictionary
    :param str out_status: status string to keep when canceling
    :return: status string
    """
    j_id = run_state['id']

    if type(j_id) == dict:
        if 'par' in j_id.keys():
            for job in j_id['par']:
                thisstate = run_state.copy()
                thisstate['id'] = job
                cstat = canceljobs(thisstate)

            return out_status

        elif 'seq' in j_id.keys():
            j_id, logfile = find_activejob(run_state)

    cl_type = run_state['type']

    if 'slurm' in cl_type:
        command = 'scancel ' + str(j_id)

    #     add other cluster types here

    elif 'standalone' in cl_type or 'generic' in cl_type:
        command = 'kill ' + str(j_id)

    if cl_type in params.remote_submission.keys():
        remotehost = params.remote_submission[cl_type]

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
        ssh.connect(remotehost, username=remote_user(remotehost))

        stdin, stdout, stderr = ssh.exec_command(command)
    else:
        os.system(command)

    return out_status


def run(target='standalone',
        pyscript=os.path.join(params.base_dir, 'launchers/test.py'),
        jsonfile='',
        run_args='',
        target_args=None,
        special_args=None,
        logfile=os.path.join(params.render_log_dir, 'render.log'),
        errfile='',
        inputs={}):
    """
    Launcher of a processing task.

    :param str target: target for processing. Currently supports:
        ['standalone','generic','slurm','localspark','sparkslurm'].
        Remote compute through ssh is also supported. Generic or spark runs on remote hosts syntax - $prefix::$host
    :param str pyscript: script to execute
    :param str or list jsonfile: string path of JSON file with the script parameters or list for multiple parallel tasks
    :param str or dict or list run_args: str, dict or list with run-time arguments for the specific launcher
    :param str or dict or list target_args: str, dict or list with setup arguments for the specific launcher
    :param str or dict or list special_args: str, dict or list with additional arguments
    :param str logfile: path to log file
    :param str errfile: path to error log
    :param dict or list inputs: dict or list of dicts containing the parameters.
    :return: Job ID (str or dict or list of Job IDs)
    :rtype: str or dict or list
    """

    if type(inputs) is list:
        # multiple sequential tasks to be initiated
        if any([type(inp) is not dict for inp in inputs]):
            raise TypeError('List of input parameters need to consist of dicts for sequential tasks!')

        outids = []

        # launch first task
        outids.append(run(**inputs[0]))

        # add the other tasks' parameters to the status list
        for seq_input in inputs[1:]:
            outids.append(seq_input)

        return {'seq': outids}

    elif inputs != {}:
        return run(**inputs)

    if type(jsonfile) is list:
        # multiple parallel tasks to be initiated

        outids = []
        for curr_json in jsonfile:
            curr_logfile = params.render_log_dir + '/' + os.path.splitext(os.path.basename(curr_json))[0] + '.log'
            curr_errfile = params.render_log_dir + '/' + os.path.splitext(os.path.basename(curr_json))[0] + '.err'
            outids.append(run(target=target, pyscript=pyscript, run_args=run_args, target_args=target_args,
                              special_args=special_args, logfile=curr_logfile, errfile=curr_errfile,
                              jsonfile=curr_json)
                          )

        return {'par': outids}

    # check target format
    if type(target) is not str:
        raise TypeError('Target needs to be string.')

    logbase = os.path.splitext(os.path.basename(logfile))[0]
    logdir = os.path.dirname(logfile)

    if errfile == '':
        errfile = os.path.join(logdir, logbase + '.err')

    runscriptfile = os.path.join(logdir, logbase + '.sh')

    if run_args is None:
        run_args = ''

    runscript = '#!/bin/bash \n'
    runscript += activate_conda()
    runscript += '\n'
    runscript += '#launch message \n'
    runscript += 'python ' + pyscript
    runscript += ' --input_json ' + jsonfile
    runscript += args2string(run_args)

    print('launching - ')
    print(target)

    if target in ['standalone', 'localhost'] or target in params.remote_hosts:
        command = 'bash ' + runscriptfile

        runscript.replace('#launch message', 'echo "Launching Render standalone processing script on " `hostname`')
        runscript += ' >  ' + logfile + ' 2> ' + errfile + ' || echo $? > ' + logfile + '_exit'

        with open(runscriptfile, 'w') as f:
            f.write(runscript)

        return run_command(target, command, logfile, errfile)

    elif target == 'generic' or target.split('generic::')[-1] in params.remote_hosts:
        command = pyscript
        command += ' ' + run_args

        remotehost = target.split('generic::')[-1]

        return run_command(remotehost, command, logfile, errfile)

    elif target == 'localspark' or target.split('spark::')[-1] in params.remote_hosts:
        command = params.launch_dir + '/localspark.sh'
        remotehost = target.split('spark::')[-1]

        spark_args = dict()

        r_params = remote_params(remotehost)

        spark_args['--cpu'] = r_params['cpu']
        spark_args['--mem'] = r_params['mem']

        if type(special_args) is dict:
            spark_args.update(special_args)



        spark_args['--class'] = pyscript
        spark_args['--spark_home'] = params.spark_dir

        if not target == 'localspark':
            spark_args['--logdir'] = logbase

        spark_args['--render_dir'] = params.render_dir

        command += ' ' + args2string(spark_args)
        command += '--params= ' + args2string(run_args, ' ')



        return run_command(remotehost, command, logfile, errfile)

    elif target == 'slurm':
        runscript.replace('#launch message',
                          '"Launching Render processing script on " `hostname`". Slurm job ID: " $SLURM_JOBID"."')

        with open(runscriptfile, 'w') as f:
            f.write(runscript)

        command = runscriptfile

        if target_args is None:
            slurm_args = '-N1 -n1 -c' + str(params.n_cpu_script) + ' --mem ' + str(params.mem_per_cpu)\
                         + 'G -t 00:' + str(params.default_walltime) + ':00 -W '
        else:
            slurm_args = args2string(target_args)

        slurm_args += '-e ' + errfile + ' -o ' + logfile

        sl_command = 'sbatch ' + slurm_args + ' ' + command

        jobid = submit_command(target, sl_command, logfile)
        jobid = jobid.strip('\n')[jobid.rfind(' ') + 1:]

        return jobid

    elif target == 'sparkslurm':

        command = params.launch_dir + '/launcher_' + target
        command += '.sh '

        target_args['--email'] = params.user + params.email
        target_args['--template'] = os.path.join(params.launch_dir, "spark_slurm_template.sh")

        logbase = logfile.partition('.log')[0]

        target_args['--runscript'] = logbase + '.' + target + '.sh'

        if '--worker_cpu' not in target_args:
            target_args['--worker_cpu'] = params.cpu_pernode_spark

        if '--worker_mempercpu' not in target_args:
            target_args['--worker_mempercpu'] = params.mem_per_cpu

        spsl_args = args2string(target_args)

        # spsl_args += args2string({'--logfile':logfile})
        # spsl_args += args2string({'--errfile':errfile})
        spsl_args += args2string({'--logdir': logbase})

        spark_args = dict()
        if type(special_args) is dict:
            spark_args.update(special_args)


        spark_args['--class'] = pyscript
        spark_args['--logdir'] = logbase
        spark_args['--spark_home'] = params.spark_dir
        spark_args['--render_dir'] = params.render_dir

        spsl_args += '--scriptparams= ' + args2string(spark_args)
        spsl_args += '--params= ' + args2string(run_args, ' ')

        command += spsl_args

        jobid = submit_command(target, command, logfile)
        jobid = jobid.strip('\n')[jobid.rfind(' ') + 1:]

        return jobid

    else:
        raise NotImplementedError('This compute format is not (yet) implemented.')


def remote_user(remotehost):
    """
    Lookup for users on remote hosts. Fallback to local user if remote host not present in params.

    :param str remotehost: address or host name of remote machine
    :return: user name
    :rtype: str
    """

    return remote_params(remotehost)['user']


def remote_params(remotehost):
    """
    Lookup for launch parameters on remote hosts. Fallback to local setting if remote host not present in params.

    :param str remotehost: address or host name of remote machine
    :return: runtime parameters for remote host
    :rtype: dict
    """

    outparams = dict()

    if remotehost in params.remote_hosts:
        r_idx = params.remote_hosts.index(remotehost)
        for r_param in params.remote_params:
            if r_param in params.remote_compute[r_idx][remotehost].keys():
                outparams[r_param] = params.remote_compute[r_idx][remotehost][r_param]
            else:
                outparams[r_param] = params.default_compparams[r_param]
    else:
         outparams.update(params.default_compparams)

    return outparams


def runtype(comp_sel):
    """
    sanitizes compute location for remote computation

    :param str comp_sel: Compute selection from UI.
    :return: sanitized compute location type (removed remote host and specify run type)
    :rtype: str
    """

    if comp_sel in params.remote_hosts:
        return 'standalone'
    else:
        return comp_sel


def run_prefix(nouser=False, dateonly=False):
    """
    Creates a specific prefix for outputs (logfiles, directories)

    :param bool nouser: do not include the user name
    :param bool dateonly: only use the date, not the time
    :return: string prefix that can be incorporated in file/path names
    :rtype: str
    """

    timestamp = time.localtime()
    user = ''
    if not nouser:
        user = params.user + '_'

    if dateonly:
        t = '{}{:02d}{:02d}'.format(timestamp.tm_year, timestamp.tm_mon, timestamp.tm_mday)
    else:
        t = '{}{:02d}{:02d}-{:02d}{:02d}'.format(timestamp.tm_year, timestamp.tm_mon, timestamp.tm_mday,
                                                 timestamp.tm_hour, timestamp.tm_min)

    return user + t
