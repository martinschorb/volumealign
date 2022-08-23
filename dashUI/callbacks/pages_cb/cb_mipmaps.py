#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""

import os
import requests
import numpy as np

import dash
from dash.exceptions import PreventUpdate

from dashUI import params

from dashUI.utils import helper_functions as hf
from dashUI.pageconf.conf_mipmaps import status_table_cols, compute_table_cols


def mipmaps_stacktodir(stack_sel, owner, project, stack, allstacks, thispage):
    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    dir_out = ''
    out = dict()

    t_fields = [''] * len(status_table_cols)
    ct_fields = [1] * len(compute_table_cols)

    if (not stack_sel == '-') and (allstacks is not None):
        stacklist = [stack for stack in allstacks if stack['stackId']['stack'] == stack_sel]
        stack = stack_sel

        if not stacklist == []:
            stackparams = stacklist[0]
            out['zmin'] = stackparams['stats']['stackBounds']['minZ']
            out['zmax'] = stackparams['stats']['stackBounds']['maxZ']
            out['numtiles'] = stackparams['stats']['tileCount']
            out['numsections'] = stackparams['stats']['sectionCount']

            num_blocks = int(np.max((np.floor(out['numsections'] / params.section_split), 1)))

            url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project \
                  + '/stack/' + stack + '/z/' + str(out['zmin']) + '/render-parameters'
            tiles0 = requests.get(url).json()

            tilefile0 = os.path.abspath(tiles0['tileSpecs'][0]['mipmapLevels']['0']['imageUrl'].strip('file:'))

            dir_out = os.path.join(os.sep, *tilefile0.split(os.sep)[:-params.datadirdepth[owner] - 1])

            out['gigapixels'] = out['numtiles'] * stackparams['stats']['maxTileWidth'] * stackparams['stats'][
                'maxTileHeight'] / (10 ** 9)

            t_fields = [stack, str(stackparams['stats']['sectionCount']), str(stackparams['stats']['tileCount']),
                        '%0.2f' % out['gigapixels']]

            n_cpu = params.n_cpu_script

            timelim = np.ceil(
                out['gigapixels'] / n_cpu * params.mipmaps['min/Gpix/CPU'] * (1 + params.time_add_buffer) / num_blocks)

            ct_fields = [n_cpu, timelim, params.section_split]

    outlist = [dir_out, stack]  # ,out]
    outlist.extend(t_fields)
    outlist.extend(ct_fields)

    return outlist
