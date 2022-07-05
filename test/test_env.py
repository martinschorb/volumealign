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


# check existence of environment on desired targets
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


# check existence of relevant paths
def test_paths():
    dirlist = [
        'base_dir',
        'render_dir',
        'conda_dir',
        'render_log_dir',
        'rendermodules_dir',
        'asap_dir',
        'spark_dir'
    ]

    for dir_var in dirlist:
        thisdir = getattr(params,dir_var)
        print(thisdir)
        assert os.path.exists(thisdir)
