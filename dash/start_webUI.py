#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 08:49:53 2021

@author: schorb
"""


import os
import json

import params



target_machines = ['login.cluster.embl.de']
target_user = params.user


user_file = './web_users.json'


# required for many cluster environments, including SPARK
ssh_key_login = True



home = os.getenv('HOME')

with open(user_file,'r') as f:
    users_exist = json.load(f)
    
if params.user not in users_exist.keys():
    
    # create new user...
   
    if ssh_key_login:
        if not os.path.exists(home+'/.ssh/id_rsa_render'):
            os.system('ssh-keygen -t rsa -b 4096 -q -p -f '+home+'/.ssh/id_rsa_render')
        
        for target in target_machines:
            os.system('ssh-copy-id -i ' + home + '/.ssh/id_rsa_render ' + target_user +'@' + target)
        
    
    port = max(users_exist.values()) + 1
    
    users_exist[params.user] = port
    
    with open(user_file,'w') as f:
            json.dump(users_exist,f,indent=4)
    
    