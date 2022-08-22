#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 08:49:53 2021

@author: schorb
"""

import os
import json
import subprocess

from dashUI import params
from dashUI.utils.launch_jobs import run_prefix

target_machines = params.remote_compute

user_file = params.base_dir + '/dashUI/web_users.json'

# required for many cluster environments, including SPARK
ssh_key_login = True

home = os.getenv('HOME')

prefix = 'http://'

if os.path.exists(os.path.join(params.base_dir, 'cert.pem')) and \
        os.path.exists(os.path.join(params.base_dir, 'key.pem')):

    prefix = 'https://'

if __name__ == "__main__":

    with open(user_file, 'r') as f:
        users_exist = json.load(f)

    if params.user not in users_exist.keys():

        print('Setting up new user for Render WebUI. This is necessary only once.\n')
        # create new user...

        if ssh_key_login:
            if not os.path.exists(home + '/.ssh'):
                os.mkdirs(home + '/.ssh')

            if not os.path.exists(home + '/.ssh/id_rsa_render'):
                os.system("ssh-keygen -t rsa -b 4096 -q -f '+home+'/.ssh/id_rsa_render -N ''")

            for target in target_machines:
                os.system('ssh-copy-id -i ' + home + '/.ssh/id_rsa_render ' + target_machines[target] + '@' + target)

        port = max(users_exist.values()) + 1

        users_exist[params.user] = port

        with open(user_file, 'w') as f:
            json.dump(users_exist, f, indent=4)

    else:
        port = users_exist[params.user]

    # check directory access for transient files to be written:

    for checkdir in [params.render_log_dir, params.json_run_dir]:
        if not os.access(checkdir, 7):
            raise OSError('The directory ' + checkdir + ' is not accessible. Check its user rights.')

    logfile = os.path.join(params.render_log_dir, 'webUI_' + run_prefix() + '.log')

    print('Starting Render WebUI.\n')
    print('As long as this window is open, you can access Render through:\n\n')
    print(prefix + params.hostname + ':' + str(port) + '\n\n')
    print('from any device in the network.\n Do not use CTRL+C to copy the address, this will close the process.')
    print('To avoid excessive resource use, please close the server when done with your processing.')

    os.system('python dashUI/app.py ' + str(port) + ' > ' + logfile)
