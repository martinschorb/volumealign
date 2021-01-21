#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# dash volume EM interface global parameters:

import json   
import os 
import time
import subprocess
import requests

#=============================================================
## Directory presets

json_template_dir = '/g/emcf/schorb/code/volumealign/JSON_parameters/templates'

json_run_dir = '/g/emcf/schorb/code/volumealign/JSON_parameters/runs'

json_match_dir = '/g/emcf/schorb/code/volumealign/JSON_parameters/MatchTrials'

render_log_dir = '/g/emcf/software/render-logs'

# base directory for launchers etc...
workdir = '/g/emcf/schorb/code/volumealign/dash'

#==============================================================
## Compute resources presets


comp_options = [{'label': 'Cluster (slurm)', 'value': 'slurm'},
                {'label': 'locally (this submission node)', 'value': 'standalone'},
                {'label': 'Spark Cluster (on slurm)', 'value': 'sparkslurm'}]

comp_default = 'slurm'

comp_defaultoptions = ['slurm','standalone']


time_add_buffer = 0.2 # time buffer for job submission (relative)

n_cpu_script = 24
mem_per_cpu = 8     # GB 

mipmaps=dict()
mipmaps['min/Gpix/CPU'] = 6

section_split = 500 #split stack into processing chunks for certain operations (mipmaps,...)



#==============================================================
## Data type presets

# directory structure

datasubdirs = {
    'SBEM':'/tiles'}

mipmapdir = 'mipmaps'





#=============================================================


default_store = {'run_state':{'state':'input', 'logfile':render_log_dir + '/out.txt'},
                 'r_status':{'state':'input', 'logfile':render_log_dir + '/out.txt'},
                 'r_launch':{'state':'input', 'logfile':render_log_dir + '/out.txt'},
                 'init_render':{'owner':'','project':'','stack':''},
                 'render_launch':{'owner':'','project':'','stack':''},
                 # 'allowners':None,
                 'allstacks':None,
                 'owner':'',
                 'project':'',
                 'stack':'',
                 'stackparams':None
                 }

match_store = {'init_match':{},
               'all_matchcolls':None
               }


#=============================================================
## UI parameters

# controls refresh rate and length of console output
refresh_interval = 1000   # ms
disp_lines = 50          # output lines to display

idle_interval = 10000   # ms


# -------------  
# derived parameters

user = os.getlogin()

timestamp = time.localtime()


p=subprocess.Popen('id -gn',stdout=subprocess.PIPE,shell=True)
group = p.communicate()[0].decode(encoding='utf8').strip("\n")


run_prefix = user + '_{}{:02d}{:02d}-{:02d}{:02d}'.format(timestamp.tm_year,timestamp.tm_mon,timestamp.tm_mday,timestamp.tm_hour,timestamp.tm_min)

v_base_url = '/render-ws/'
render_version = 'v1/'


# Choose Render parameters
with open(os.path.join(json_template_dir,'render.json'),'r') as f:
    render_json = json.load(f)

render_base_url = 'http://' + render_json['render']['host']
render_base_url += ':' + str(render_json['render']['port'])
render_base_url += v_base_url



# get initial list of owners in Render:
    
url = render_base_url + render_version + 'owners'
render_owners = requests.get(url).json()
default_store['init_render']['allowners'] = render_owners

