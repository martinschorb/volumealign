#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# dash volume EM interface global parameters:

import json   
import os 
import time

#=============================================================
## Directory presets

json_template_dir = '/g/emcf/schorb/code/volumealign/JSON_parameters/templates'

json_run_dir = '/g/emcf/schorb/code/volumealign/JSON_parameters/runs'

render_log_dir = '/g/emcf/software/render-logs'

# base directory for launchers etc...
workdir = '/g/emcf/schorb/code/volumealign/dash'

#==============================================================
## Compute resources presets

time_add_buffer = 0.2 # time buffer for job submission (relative)

n_cpu_script = 24 

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
## UI parameters

# controls refresh rate and length of console output
refresh_interval = 1000   # ms
disp_lines = 50          # output lines to display

idle_interval = 10000   # ms


# -------------  
# derived parameters

user = os.getlogin()

timestamp = time.localtime()

run_prefix = user + '_{}{:02d}{:02d}-{:02d}{:02d}'.format(timestamp.tm_year,timestamp.tm_mon,timestamp.tm_mday,timestamp.tm_hour,timestamp.tm_min)

v_base_url = '/render-ws/'
render_version = 'v1/'


# Choose Render parameters
with open(os.path.join(json_template_dir,'render.json'),'r') as f:
    render_json = json.load(f)

render_base_url = 'http://' + render_json['render']['host']
render_base_url += ':' + str(render_json['render']['port'])
render_base_url += v_base_url

