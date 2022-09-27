#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""

import dash

import requests
import time
import os
import json
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from contextvars import copy_context
from dash._callback_context import context_value
from dash._utils import AttributeDict

# import callbacks to check
from dashUI.callbacks.pages_cb.cb_tilepairs import tilepairs_execute_gobutton

from dashUI.utils.launch_jobs import run_prefix
from dashUI import params

from helpers import check_renderselect, \
    select_radioitem, \
    check_substackselect, \
    set_callback_context

module = 'tilepairs'


@pytest.mark.dependency(depends=["webUI"],
                        scope='session')
def test_tilepairs(thisdash, startup_webui):
    thisdash.driver.get(thisdash.server_url + '/' + module)

    check_renderselect(thisdash, module)

    # check option visibility
    head = thisdash.driver.find_element(By.XPATH, '//h3')
    owner_dd = thisdash.driver.find_element(By.XPATH, '//div[@class="dash-dropdown" and contains(@id,"owner")'
                                                      ' and contains(@id,"' + module + '")]')

    owners = []
    i = 0

    while True:
        try:
            thisdash.select_dcc_dropdown(owner_dd, index=i)
            owners.append(owner_dd.text)
            i += 1
        except IndexError:
            break

    head.click()

    multi_run = thisdash.driver.find_element(By.XPATH, '//div[contains(@id,"multi-run")'
                                                       ' and contains(@id,"' + module + '")]')

    div_3d = thisdash.driver.find_element(By.XPATH, '//div[contains(@id,"page2")'
                                                    ' and contains(@id,"' + module + '")]')

    for o in owners:
        thisdash.select_dcc_dropdown(owner_dd, value=o)
        # check the 2D-only types
        if o in params.owners_2d:
            assert multi_run.get_attribute('style') != 'display: none;'
            assert div_3d.get_attribute('style') == 'display: none;'
        else:
            o_3D = o
            assert multi_run.get_attribute('style') == 'display: none;'
            assert div_3d.get_attribute('style') != 'display: none;'

    thisdash.select_dcc_dropdown(owner_dd, value=o_3D)

    pairmode = thisdash.driver.find_element(By.XPATH, '//div[contains(@id,"pairmode")'
                                                      ' and contains(@id,"' + module + '")]')

    slices_3d = thisdash.driver.find_element(By.XPATH, '//div[contains(@id,"3Dslices")'
                                                       ' and contains(@id,"' + module + '")]')

    # 2D
    select_radioitem(pairmode, 0)
    assert slices_3d.get_attribute('style') == 'display: none;'

    # 3D
    select_radioitem(pairmode, 1)
    assert slices_3d.get_attribute('style') != 'display: none;'

    check_substackselect(thisdash, module, switch=select_radioitem(pairmode, 1))

    # Check the go callback
    # ====================================

    stack_el = ("stack_dd", module)
    stack_val = 'newstack'

    # check 1:  no click -> no update
    # .(click, pairmode, stack, slicedepth, comp_sel, startsection, endsection, owner, project, multi, stacklist)
    with pytest.raises(dash.exceptions.PreventUpdate):
        result = tilepairs_execute_gobutton(None, '', '', '', '', '', '', '', '', '', '')

    # check 2: trigger not go button -> no action, button enabled
    context_value.set(set_callback_context(stack_el, stack_val))
    result = tilepairs_execute_gobutton(1, '', '', '', '', '', '', '', '', '', '')

    assert not result[0]
    assert type(result[1]) is dash._callback.NoUpdate
    assert type(result[2]) is dash._callback.NoUpdate

    # check 3: 2D tilepairs

    go_el = ("go", module)
    go_val = 1

    context_value.set(set_callback_context(go_el, go_val))

    pairm = '2D'

    test_projname = 'testproject'
    test_stackname = 'teststack'

    minz = 1
    maxz = 11

    prefix = run_prefix()
    result = tilepairs_execute_gobutton(1, pairm, test_stackname, 1, 'test', minz, maxz,
                                        'owner', test_projname, None, [])

    assert result[0]

    assert type(result[1]) is dict
    assert result[1]['type'] == 'test'
    assert result[1]['id'] == 'test_launch'
    assert result[1]['status'] == 'launch'
    assert prefix in result[1]['logfile']
    assert module in result[1]['logfile']

    assert type(result[2]) is dict
    assert result[2]['owner'] == 'owner'
    assert result[2]['project'] == test_projname
    assert result[2]['stack'] == test_stackname
    assert pairm in result[2]['tilepairdir']
    assert prefix in result[2]['tilepairdir']
    assert module in result[2]['tilepairdir']

    #     check parameter file output for initiating the processing

    param_file = params.json_run_dir + '/' + module + '_' + prefix + '_' + test_stackname + '_' + pairm + '.json'

    assert os.path.exists(param_file)

    with open(param_file) as f:
        outputparams = json.load(f)

    expectedrender = dict(params.render_json)
    expectedrender['render']['owner'] = 'owner'
    expectedrender['render']['project'] = test_projname

    assert outputparams['render'] == expectedrender['render']

    assert outputparams['stack'] == test_stackname
    assert outputparams['output_dir'] == os.path.splitext(param_file)[0]
    assert outputparams['output_json'] == os.path.join(outputparams['output_dir'], 'tiles_' + pairm)

    assert outputparams['minZ'] == minz
    assert outputparams['maxZ'] == maxz

    assert outputparams['excludeSameLayerNeighbors'] == 'False'
    assert outputparams['zNeighborDistance'] == 0

    # check 4: 3D tilepairs

    pairm = '3D'

    test_projname = 'testproject'
    test_stackname = 'teststack'

    minz = 1
    maxz = 11

    test_slicedepth = 3

    prefix = run_prefix()
    # .(click, pairmode, stack, slicedepth, comp_sel, startsection, endsection, owner, project, multi, stacklist)

    result = tilepairs_execute_gobutton(1, pairm, test_stackname, test_slicedepth, 'test',
                                        minz, maxz, 'owner', test_projname, None, [])

    assert result[0]

    assert type(result[1]) is dict
    assert result[1]['type'] == 'test'
    assert result[1]['id'] == 'test_launch'
    assert result[1]['status'] == 'launch'
    assert prefix in result[1]['logfile']
    assert module in result[1]['logfile']

    assert type(result[2]) is dict
    assert result[2]['owner'] == 'owner'
    assert result[2]['project'] == test_projname
    assert result[2]['stack'] == test_stackname
    assert pairm in result[2]['tilepairdir']
    assert prefix in result[2]['tilepairdir']
    assert module in result[2]['tilepairdir']

    #     check parameter file output for initiating the processing

    param_file = params.json_run_dir + '/' + module + '_' + prefix + '_' + test_stackname + '_' + pairm + '.json'

    assert os.path.exists(param_file)

    with open(param_file) as f:
        outputparams = json.load(f)

    expectedrender = dict(params.render_json)
    expectedrender['render']['owner'] = 'owner'
    expectedrender['render']['project'] = test_projname

    assert outputparams['render'] == expectedrender['render']

    assert outputparams['stack'] == test_stackname
    assert outputparams['output_dir'] == os.path.splitext(param_file)[0]
    assert outputparams['output_json'] == os.path.join(outputparams['output_dir'], 'tiles_' + pairm)

    assert outputparams['minZ'] == minz
    assert outputparams['maxZ'] == maxz

    assert outputparams['excludeSameLayerNeighbors'] == 'True'
    assert outputparams['zNeighborDistance'] == test_slicedepth

    # check 5: 2D tilepairs multi stack

    go_el = ("go", module)
    go_val = 1

    context_value.set(set_callback_context(go_el, go_val))

    pairm = '2D'

    test_projname = 'testproject'
    test_stackname = 'teststack'

    minz = 1
    maxz = 11

    stacklist = [{'label': 1, 'value': test_stackname + '_nav_1'},
                 {'label': 2, 'value': test_stackname + '_nav_2'},
                 {'label': 3, 'value': test_stackname + '_nav_10'}]

    prefix = run_prefix()
    result = tilepairs_execute_gobutton(1, pairm, test_stackname, 1, 'test', minz, maxz,
                                        'owner', test_projname, 1, stacklist)

    assert result[0]

    assert type(result[1]) is dict
    assert result[1]['type'] == 'test'
    assert result[1]['id'] == {'par': ['test_launch'] * len(stacklist)}
    assert result[1]['status'] == 'launch'
    assert prefix in result[1]['logfile']
    assert module in result[1]['logfile']

    assert type(result[2]) is dict
    assert result[2]['owner'] == 'owner'
    assert result[2]['project'] == test_projname
    assert result[2]['stack'] == test_stackname
    assert pairm in result[2]['tilepairdir']
    assert prefix in result[2]['tilepairdir']
    assert module in result[2]['tilepairdir']

    #     check parameter file output for initiating the processing

    param_file = params.json_run_dir + '/' + module + '_' + prefix + '_' + test_stackname + '_' + pairm + '.json'

    assert os.path.exists(param_file)

    with open(param_file) as f:
        outputparams = json.load(f)

    expectedrender = dict(params.render_json)
    expectedrender['render']['owner'] = 'owner'
    expectedrender['render']['project'] = test_projname

    assert outputparams['render'] == expectedrender['render']

    assert outputparams['stack'] == test_stackname
    assert outputparams['output_dir'] == os.path.splitext(param_file)[0]
    assert outputparams['output_json'] == os.path.join(outputparams['output_dir'], 'tiles_' + pairm)

    assert outputparams['minZ'] == minz
    assert outputparams['maxZ'] == maxz

    assert outputparams['excludeSameLayerNeighbors'] == 'False'
    assert outputparams['zNeighborDistance'] == 0
