#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# dash volume EM interface global parameters:

import json
import os
import time
import subprocess
import requests
import socket

#=============================================================
## Directory presets

json_template_dir = '/g/emcf/software/volumealign/JSON_parameters/templates'

json_run_dir = '/g/emcf/software/volumealign/JSON_parameters/runs'

json_match_dir = '/g/emcf/software/volumealign/JSON_parameters/MatchTrials'

render_log_dir = '/g/emcf/software/render-logs'

# hotknife_dir = "/g/emcf/schorb/code/hot-knife"

# base directory for launchers etc...
workdir = '/g/emcf/software/volumealign/dash'

# emails

email = '@embl.de'
doc_url = 'https://schorb.embl-community.io/volumealign/usage/'

init_logfile = 'out.txt' #render_log_dir + '/pointmatch_schorb_20210303-1617.log'

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

# standalone

n_cpu_standalone = 8


# spark

n_cpu_spark = 300
cpu_pernode_spark = 30

mipmaps=dict()
mipmaps['min/Gpix/CPU'] = 6

export=dict()
export['min/GPix/CPU_N5'] = 50


section_split = 500 #split stack into processing chunks for certain operations (mipmaps,...)



#==============================================================
## Data type presets

# directory structure

datasubdirs = {
    'SBEM':'/tiles'}

mipmapdir = 'mipmaps'

outdirbase = 'aligned'



#=============================================================


default_store = {'run_state':{'state':'input', 'logfile':init_logfile},
                 'r_status':{'state':'input', 'logfile':init_logfile},
                 'r_launch':{'state':'input', 'logfile':init_logfile},
                 'init_render':{'owner':'','project':'','stack':'',
                                'matchcoll': '', 'mc_owner':''},
                 'render_launch':{'owner':'','project':'','stack':''},
                 # 'allowners':None,
                 'allstacks':None,
                 'owner':'',
                 'project':'',
                 'stack':'',
                 'stackparams':None
                 }

match_store = {#'init_match':{},
               'all_matchcolls':None
               }


#=============================================================
## UI parameters

# maximum number of tile view images per UI module
max_tileviews = 3
# view image width
im_width = 900

default_tile_scale = 0.5

# controls refresh rate and length of console output
refresh_interval = 1000   # ms
disp_lines = 50          # output lines to display

idle_interval = 5000   # ms


#=============================================================
## solve parameters

solve_transforms = [
            'AffineModel', 'SimilarityModel', 'Polynomial2DTransform',
            'affine', 'rigid', 'affine_fullsize', 'RotationModel',
            'TranslationModel', 'ThinPlateSplineTransform']

solve_types = ['montage', '3D']

# -------------
# derived parameters

user = os.getlogin()

hostname = socket.gethostname()


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
