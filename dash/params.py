#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# dash volume EM interface global parameters:

import json
import os
import subprocess
import requests
import socket

#=============================================================
## Directory presets

base_dir = '/g/emcf/schorb/code/volumealign/'#'/g/emcf/software/volumealign/'

render_dir = '/g/emcf/software/render'

conda_dir = '/g/emcf/software/python/miniconda'

render_log_dir = '/g/emcf/software/render-logs'

rendermodules_dir = '/g/emcf/schorb/code/render-modules/'

gc3_conffile = os.path.join(base_dir,'launchers/gc3conf/template_gc3pie.conf')

spark_dir = '/g/emcf/software/spark-3.0.0-bin-hadoop3.2'

# derived base directories for launchers etc...
# you can point these to other targets if desired

workdir = os.path.join(base_dir,'dash')

launch_dir = os.path.join(base_dir,'launchers')

json_template_dir = os.path.join(base_dir,'JSON_parameters','templates')

json_run_dir = os.path.join(base_dir,'JSON_parameters','runs')

json_match_dir = os.path.join(base_dir,'JSON_parameters','MatchTrials')


# notification and documentation
user = os.getlogin()
email = '@embl.de'
doc_url = 'https://schorb.embl-community.io/volumealign/usage/'

init_logfile = 'out.txt' #render_log_dir + 'fancylogfile.log'

#==============================================================
## Compute resources presets

# name of the conda environment that provides the gc3Pie runtime
gc3_envname = 'gc3pie'

# name of the conda environment that provides the render-modules and renderapi packages
render_envname = 'render'


comp_options = [
                # {'label': 'Gc3', 'value': 'gc3'},
                {'label': 'Cluster (slurm)', 'value': 'slurm'},
                {'label': 'locally', 'value': 'standalone'},
                {'label': 'Spark Cluster (on slurm)', 'value': 'sparkslurm'}
                ]

# gc3conf = Configuration(gc3_conffile)
#
# for resource in gc3conf.resources.keys():
#     comp_options.append({'label': resource, 'value': 'gc3_'+resource})
#

comp_default = 'standalone'

comp_defaultoptions = ['standalone']#,'sparkslurm']

min_chunksize = 5e5 # minimum chunk size for n5/zarr export (in bytes)

time_add_buffer = 0.2 # time buffer for job submission (relative)

n_cpu_script = 24
mem_per_cpu = 4     # GB

# standalone

n_cpu_standalone = 8


# spark

n_cpu_spark = 300
cpu_pernode_spark = 10

mipmaps=dict()
mipmaps['min/Gpix/CPU'] = 6

export=dict()
export['min/GPix/CPU_N5'] = 30


section_split = 500 #split stack into processing chunks for certain operations (mipmaps,...)



#==============================================================
## Data type presets

# directory structure

datasubdirs = {
    'SBEM':'/tiles',
    'SerialEM':'.'}

mipmapdir = 'mipmaps'

outdirbase = 'aligned'

# slice numeration schemes

slicenumformat = { # string format in which the slice number appears in the tile labels
    'SBEM':'.%05i'
    }


# tile reformatting scheme

#SBEM
def tile_display_SBEM(tiles,prev_tile,slicenum):
    t_labels = tiles.copy()
    tile = tiles[0]

    for t_idx,t_label in enumerate(tiles):
        t_labels[t_idx] = t_label.partition('.')[2].partition('.')[0]

        if (not prev_tile is None) and t_labels[t_idx] in prev_tile:
            tile = t_label.partition('.')[0]+'.'+ t_labels[t_idx] + slicenumformat['SBEM'] %slicenum


    return t_labels, tile

tile_display = {
    'SBEM':tile_display_SBEM
    }


#=============================================================

default_status = {'id':None,'type':None, 'status':'input', 'logfile':init_logfile}


default_store = {'run_status':default_status,
                 'r_status':default_status,
                 'launch_status':default_status,
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

hostname = socket.gethostname()

p=subprocess.Popen('id -gn',stdout=subprocess.PIPE,shell=True)
group = p.communicate()[0].decode(encoding='utf8').strip("\n")


v_base_url = '/render-ws/'
render_version = 'v1/'


# Choose Render parameters
with open(os.path.join(json_template_dir,'render.json'),'r') as f:
    render_json = json.load(f)

render_base_url = render_json['render']['host']
render_base_url += ':' + str(render_json['render']['port'])
render_base_url += v_base_url



# get initial list of owners in Render:

url = render_base_url + render_version + 'owners'

render_owners = requests.get(url).json()
default_store['init_render']['allowners'] = render_owners

processes = dict()