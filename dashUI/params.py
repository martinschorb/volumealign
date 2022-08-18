#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# dash volume EM interface global parameters:

import json
import os
import getpass
import glob
import subprocess
import requests
import socket
import numpy as np

# =============================================================
# Directory presets

base_dir = os.path.join(os.path.dirname(__file__), '..')

# for debugging at a specific location uncomment the next line
# base_dir = '/g/emcf/software/volumealign/'

render_dir = '/g/emcf/software/render'

conda_dir = '/g/emcf/software/python/miniconda'

render_log_dir = '/g/emcf/software/render-logs'

rendermodules_dir = '/g/emcf/schorb/code/rendermodules-addons/rmaddons'

asap_dir = '/g/emcf/schorb/code/asap-modules/asap/'

spark_dir = '/g/emcf/software/spark-3.0.0-bin-hadoop3.2'

# derived directories for launchers etc...
# you can point these to other targets if desired

workdir = os.path.join(base_dir, 'dashUI')

launch_dir = os.path.join(base_dir, 'launchers')

json_template_dir = os.path.join(base_dir, 'JSON_parameters', 'templates')

json_run_dir = os.path.join(base_dir, 'JSON_parameters', 'runs')

json_match_dir = os.path.join(base_dir, 'JSON_parameters', 'MatchTrials')

# default_dir = "/g/"+group
# defined at the end!

# notification and documentation
user = getpass.getuser()
email = '@embl.de'
doc_url = 'https://schorb.embl-community.io/volumealign/usage/'

init_logfile = 'out.txt'  # render_log_dir + 'fancylogfile.log'

# ==============================================================
# Compute resources presets

# name of the conda environment that provides the render-modules and renderapi packages
render_envname = 'render'
dash_envname = 'dash-new'

comp_options = [
    {'label': 'Cluster (slurm)', 'value': 'slurm'},
    {'label': 'locally', 'value': 'standalone'},
    {'label': 'Spark Cluster (on slurm)', 'value': 'sparkslurm'},
    {'label': 'Spark locally', 'value': 'localspark'}
]

comp_default = 'standalone'

comp_clustertypes = ['slurm']

comp_defaultoptions = ['standalone', 'slurm']

# list remote workstations/login nodes and the remote launch parameters if special (dict or str)

remote_params = ['user', 'cpu', 'mem']

remote_compute = [
    # {'pc-emcf-16.embl.de': {'user': 'testuser',
    #                         'cpu': 2,
    #                         'mem': 4}},
    {'render.embl.de': {'cpu': 2,
                        'mem': 4}},
    {'login01.cluster.embl.de': {}}]

# dict. If empty, submission and status calls for cluster environments will be issued locally
remote_submission = {'slurm': 'login01.cluster.embl.de',
                     'sparkslurm': 'login01.cluster.embl.de'}

# add remote resources

remote_hosts = []

for resource in remote_compute:
    r_name = list(resource.keys())[0]
    remote_hosts.append(r_name)
    comp_options.append({'label': 'Remote using ' + r_name, 'value': r_name})
    comp_options.append({'label': 'Local Spark on ' + r_name, 'value': 'spark::' + r_name})
    comp_defaultoptions.append(r_name)

min_chunksize = 5e5  # minimum chunk size for n5/zarr export (in bytes)

time_add_buffer = 0.2  # time buffer for job submission (relative)

n_cpu_script = 4
mem_per_cpu = 4  # GB
n_jobs_default = 8
default_walltime = 5  # min

# standalone

n_cpu_standalone = 8
mem_standalone = 8  # GB

default_compparams = {'user': user,
                      'cpu': n_cpu_standalone,
                      'mem': mem_standalone}

# spark

n_cpu_spark = 200
cpu_pernode_spark = 10

spark_port = '8080'
spark_job_port = '4040'

# runtime parameters

mipmaps = dict()
mipmaps['min/Gpix/CPU'] = 6

export = dict()
export['min/GPix/CPU_N5'] = 5
export['min/GPix/CPU_slice'] = 20

section_split = 500  # split stack into processing chunks for certain operations (mipmaps,...)

# ==============================================================
# Data type presets

# directory structure

datadirdepth = {
    'SBEM': 3,
    'SerialEM': 1,
    'FIBSEM': 1}  # levels how deep inside the root directory the actual tile images are stored

mipmapdir = 'mipmaps'

outdirbase = 'aligned'

# slice numeration schemes

slicenumformat = {  # string format in which the slice number appears in the tile labels
    'SBEM': '.%05i'
}


# tile reformatting scheme

# SBEM
def tile_display_SBEM(tiles, prev_tile, slicenum):
    t_labels = tiles.copy()
    tile = tiles[0]
    gridids = []
    gridlabels = tiles.copy()

    for t_idx, t_label in enumerate(tiles):
        t_labels[t_idx] = t_label.partition('.')[2].partition('.')[0]
        gridlabels[t_idx] = 'grid' + t_label.partition('.')[0] + ' - tile' + t_label.partition('.')[2].partition('.')[0]
        gridids.append(t_label.partition('.')[0])

        if (prev_tile is not None) and t_labels[t_idx] in prev_tile:
            tile = t_label.partition('.')[0] + '.' + t_labels[t_idx] + slicenumformat['SBEM'] % slicenum

        if len(np.unique(gridids)) > 1:
            t_labels = gridlabels

    return t_labels, tile


tile_display = {
    'SBEM': tile_display_SBEM
}

# =============================================================

default_status = {'id': None, 'type': None, 'status': 'input', 'logfile': init_logfile}

default_store = {'run_status': default_status,
                 'r_status': default_status,
                 'launch_status': default_status,
                 'init_render': {'owner': '', 'project': '', 'stack': '',
                                 'matchcoll': '', 'mc_owner': ''},
                 'render_launch': {'owner': '', 'project': '', 'stack': ''},
                 # 'allowners':None,
                 'allstacks': None,
                 'owner': '',
                 'project': '',
                 'stack': '',
                 'stackparams': None
                 }

match_store = {  # 'init_match':{},
    'all_matchcolls': None
}

# match trial owner default ('flyTEM' in built)

mt_owner = 'flyTEM'

# =============================================================
# UI parameters

# maximum number of tile view images per UI module
max_tileviews = 2
# view image width
im_width = 900

default_tile_scale = 0.5

# controls refresh rate and length of console output
refresh_interval = 6000  # ms
disp_lines = 50  # output lines to display

# =============================================================
# solve parameters

solve_transforms = [
    'AffineModel', 'SimilarityModel', 'Polynomial2DTransform',
    'affine', 'rigid', 'affine_fullsize', 'RotationModel',
    'TranslationModel', 'ThinPlateSplineTransform']

solve_types = ['montage', '3D']

# -------------
# derived parameters

hostname = socket.gethostname()

p = subprocess.Popen('id -gn', stdout=subprocess.PIPE, shell=True)
group = p.communicate()[0].decode(encoding='utf8').strip("\n")

v_base_url = '/render-ws/'
render_version = 'v1/'

# Choose Render parameters
with open(os.path.join(json_template_dir, 'render.json'), 'r') as f:
    render_json = json.load(f)

render_base_url = render_json['render']['host']
render_base_url += ':' + str(render_json['render']['port'])
render_base_url += v_base_url

render_sparkjar = glob.glob(render_dir + '/render-ws-spark-client/target/render-ws-spark-client-*-standalone.jar')[0]

# get initial list of owners in Render:

url = render_base_url + render_version + 'owners'

render_owners = requests.get(url).json()
default_store['init_render']['allowners'] = render_owners
default_dir = "/g/" + group
