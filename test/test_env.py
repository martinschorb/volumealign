#!/usr/bin/env python
'''
'''

import os
import subprocess
import pytest
import paramiko

from dashUI import params

from dashUI.utils.launch_jobs import remote_user

compute_targets = params.comp_defaultoptions
remote_targets = list(params.remote_compute)

for target in params.remote_logins.keys():
    if target not in remote_targets:
        remote_targets.append(target)

# test availability of remote hosts
def test_remote():
    for target in remote_targets:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
        ssh.connect(target, username=remote_user(target),timeout=5)

# check existence of environment on desired targets
def test_conda_envs():
    for target in compute_targets:
        command = 'conda env list'

        if target == 'standalone':
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode()

        else:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
            ssh.connect(target, username=remote_user(target),timeout=5)

            stdin, stdout, stderr = ssh.exec_command(command)

            result = ''.join(stdout.readlines())

        assert '\n' + params.render_envname + ' '*4 in result