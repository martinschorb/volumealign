#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 08:49:53 2021

@author: schorb
"""

import os
import json
import time

from dashUI import params
from dashUI.utils.launch_jobs import run_prefix, remote_user

target_machines = params.remote_compute

user_file = params.base_dir + '/dashUI/web_users.json'

if not os.path.exists(user_file):
    with open(user_file, 'w') as f:
        json.dump({}, f, indent=4)
        os.system('chmod +w ' + user_file)

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
        print('Please follow the instructions below.\n')
        print('==============================================\n\n')
        # create new user...

        if ssh_key_login:
            if not os.path.exists(home + '/.ssh'):
                os.makedirs(home + '/.ssh')

            if not os.path.exists(home + '/.ssh/id_rsa'):
                os.system("ssh-keygen -t rsa -b 4096 -q -f " + home + "/.ssh/id_rsa")

            for target in target_machines:
                thost = list(target.keys())[0]
                os.system('ssh-copy-id -i ' + home + '/.ssh/id_rsa ' + remote_user(thost) + '@' + thost)

            if params.hostname.endswith('embl.de'):
                print('\n==============================================\n\n')

                print('In order to enable cluster submission, you need to log into this website:\n'
                      'https://pwtools.embl.de/sshkey \n'
                      'and copy the text below into the field for your SSH key. \n'
                      'Do not use CTRL+C to copy the address, this will close the process.\n'
                      '==============================================')
                os.system('cat ' + home + '/.ssh/id_rsa.pub')

                print('==============================================\n')
                print('waiting for 1 minute and will then start the server...')
                time.sleep(60)

        # find port for new user
        if len(users_exist.values()) ==0:
            port = params.dash_startingport
        else:
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
