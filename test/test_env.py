#!/usr/bin/env python
'''
tests for the basic environment setup for running volumealign
'''

import os
import subprocess
import pytest
import paramiko

from dashUI import params

from dashUI.utils.launch_jobs import remote_user

dirlist = [
    'render_dir',
    'conda_dir',
    'render_log_dir',
    'rendermodules_dir',
    'asap_dir'
]

compute_targets = params.comp_defaultoptions
remote_targets = list(params.remote_hosts)

if len(params.remote_submission.keys()) > 0:
    remote_targets.extend(list(params.remote_submission.keys()))


# test availability of remote hosts
def test_remote():
    for target in remote_targets:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
        ssh.connect(target, username=remote_user(target), timeout=5)


# check existence of relevant paths
def test_paths():

    # check configured base directory (locally)
    thisdir = params.base_dir
    assert os.path.exists(thisdir)

    command = 'ls ' + thisdir


    # check availability of run script directories for each compute target

    for target in compute_targets:
        print('Test directory availability on ' + target)
        if 'spark' in target:
            thisdir = params.spark_dir
            assert os.path.exists(thisdir)
        else:
            for dir_var in dirlist:
                thisdir = getattr(params, dir_var)
                print(thisdir)


                if target == 'standalone':
                    result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode()

                elif target in params.comp_clustertypes:
                    continue

                else:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
                    ssh.connect(target, username=remote_user(target), timeout=5)

                    stdin, stdout, stderr = ssh.exec_command(command)

                    assert stdout.channel.recv_exit_status() == 0



            # check existence of environment on desired targets (default compute targets)
def test_conda_envs():
    for target in compute_targets:
        command = 'conda env list'

        if target == 'standalone':
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode()

        elif target in params.comp_clustertypes:
            continue

        else:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
            ssh.connect(target, username=remote_user(target), timeout=5)

            stdin, stdout, stderr = ssh.exec_command(command)

            result = ''.join(stdout.readlines())

        assert '\n' + params.render_envname + ' ' * 4 in result

        assert '\n' + params.dash_envname + ' ' * 4 in result
