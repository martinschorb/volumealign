#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""

import pytest
import os
import time
import subprocess
import requests

from dash._callback_context import context_value

import renderapi

from dashUI import params
from dashUI.start_webUI import prefix

from dashUI.inputtypes.fibsem_conv import fibsem_conv_gobutton

from test_pages.helpers import set_callback_context, get_renderparams


@pytest.fixture(scope='session')
def startup_webui():
    try:
        response = requests.get(prefix + 'localhost:8050', verify=False)
        s = 200
    except:
        s = 404

    if s == 200:
        outfile =  'server is already running'
    else:
        outfile = os.path.join(params.base_dir, 'test', 'webui_temp.out')

        p = subprocess.Popen(os.path.join(params.base_dir, 'WebUI.sh'), stdout=open(outfile, 'w'))

        # check for regular running
        time.sleep(8)

        assert p.errors is None

        assert p.returncode is None
        assert os.path.exists(outfile)

    yield outfile

    if not s == 200:
        os.system('kill $(echo $(ps x -o "pid command" | grep "dashUI/app" |grep "sh -c python") | cut -d " " -f 1)')
        os.system('kill $(echo $(ps x -o "pid command" | grep "dashUI/app" |grep "python") | cut -d " " -f 1)')
        os.system('rm ' + outfile)


@pytest.fixture(scope='session')
def prepare_teststack(request):
    # from rendermodules_addons tes_data
    # example TIFF Stack input data

    example_dir = os.path.abspath(os.path.join(params.rendermodules_dir, '..', 'tests', 'test_files'))
    temp_dir = os.path.join(params.base_dir, 'test', 'test_files')

    example_tifz = os.path.join(example_dir, 'testtiff.tgz')
    example_tif = os.path.abspath(os.path.join(temp_dir, 'tif_testdata'))

    if not os.path.exists(example_tif):
        try:
            os.system('tar xvfz ' + example_tifz + ' -C ' + temp_dir)
        except OSError as e:
            pass

    gobutton_el = 'convert_FIBSEM' + 'go'

    context_value.set(set_callback_context(gobutton_el, 1, valkey='n_clicks'))

    test_projname = 'testproject'
    test_stackname = 'testtack'
    in_status = {'logfile': 'out.txt', 'status': 'input'}

    result = fibsem_conv_gobutton(test_stackname, example_tif, 1, test_projname, params.comp_test, 10, 20,
                                  dict(in_status), {})

    k = 0

    expectedstackdict = result[3]

    while k < 60:
        time.sleep(10)
        k += 1
        if get_renderparams(expectedstackdict)[0] == expectedstackdict:
            break

    yield expectedstackdict

    # cleanup
    os.system('rm -rf ' + example_tif)

    render_params = params.render_json['render']
    render_params['project'] = test_projname
    render_params['owner'] = expectedstackdict['owner']
    render = renderapi.connect(**render_params)

    renderapi.stack.delete_stack(expectedstackdict['stack'], render=render)
