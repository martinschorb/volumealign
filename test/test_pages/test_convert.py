#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""

from dash.testing.application_runners import import_app
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
from dashUI.inputtypes.sbem_conv import sbem_conv_gobutton
from dashUI.inputtypes.serialem_conv import serialem_conv_gobutton
from dashUI.inputtypes.fibsem_conv import fibsem_conv_gobutton

from dashUI.utils.launch_jobs import run_prefix
from dashUI.params import json_run_dir, render_json

from helpers import module_selector, \
    check_subpages, \
    check_browsedir, \
    check_renderselect, \
    set_callback_context

module = 'convert'



def test_convert(thisdash):

    thisdash.driver.get(thisdash.server_url + '/' + module)

    # check input type dropdown -> subpage selection
    input_dd = thisdash.find_element(module_selector('import_type_dd', module))

    inputtypes = ['SBEM', 'SerialEM', 'FIBSEM']

    check_subpages(inputtypes, input_dd, module, thisdash)


@pytest.mark.dependency(depends=["test_webUI"])
def test_conv_SBEM(thisdash):
    inp_sel = 'SBEM'
    inp_module = 'sbem_conv'
    label = module + '_' + inp_sel

    thisdash.driver.get(thisdash.server_url + '/' + module)

    # check input type dropdown -> subpage selection
    input_dd = thisdash.find_element(module_selector('import_type_dd', module))

    input_dd.clear()
    input_dd.send_keys(inp_sel, Keys.RETURN)

    check_browsedir(thisdash, inp_sel)

    check_renderselect(thisdash, label, components={'owner': 'SBEM', 'project': True, 'stack': True})

    # Check the go callback
    # ====================================

    stack_el = ("stack_dd", label)
    stack_val = 'newstack'

    dir_el = ("path_input", label)
    dir_val = 'notexistingdirectory'

    in_status = {'logfile': 'out.txt', 'status': 'input'}

    # check 1:  new stack -> disabled button
    context_value.set(set_callback_context(stack_el, stack_val))

    result = sbem_conv_gobutton(stack_val, os.getcwd(), 1, 'test', 'standalone', dict(in_status), {})

    assert result[0]
    assert result[1] == ''
    assert result[2] == {'logfile': 'out.txt', 'status': 'wait'}
    assert type(result[3]) is dash._callback.NoUpdate

    # check 2:  other stack -> enabled button
    context_value.set(set_callback_context(stack_el, 'test'))
    result = sbem_conv_gobutton('test', os.getcwd(), 1, 'test', 'standalone', dict(in_status), {})

    assert result[0] is False
    assert result[1] == ''
    assert result[2] == in_status
    assert type(result[3]) is dash._callback.NoUpdate

    # check 3:  bad input directory -> popup text, disabled button
    context_value.set(set_callback_context(dir_el, dir_val))

    result = sbem_conv_gobutton('test', dir_val, 1, 'test', 'standalone', dict(in_status), {})

    assert result[0]
    assert result[1] == 'Directory not accessible.'
    assert result[2] == {'logfile': 'out.txt', 'status': 'wait'}
    assert type(result[3]) is dash._callback.NoUpdate

    # check 4:  wrong directory characters
    result = sbem_conv_gobutton('test', 'this directory/has wrong chars!', 1,
                                'test', 'standalone', dict(in_status), {})

    assert result[0]
    assert result[1] == 'Wrong characters in input directory path. Please fix!'
    assert result[2] == {'logfile': 'out.txt', 'status': 'wait'}
    assert type(result[3]) is dash._callback.NoUpdate

    # check 5: click go button and launch processing
    gobutton_el = label + 'go'

    context_value.set(set_callback_context(gobutton_el, 1, valkey='n_clicks'))

    test_projname = 'testproject'
    test_stackname = 'teststack'

    prefix = run_prefix()
    result = sbem_conv_gobutton(test_stackname, os.getcwd(), 1, test_projname, 'test', dict(in_status), {})

    assert result[0]
    assert result[1] == ''

    assert result[2]['type'] == 'test'
    assert result[2]['id'] == 'test_launch'
    assert result[2]['status'] == 'running'
    assert prefix in result[2]['logfile']
    assert inp_module in result[2]['logfile']

    assert result[3] == {'owner': 'SBEM', 'project': 'testproject', 'stack': 'teststack'}

    #     check parameter file output for initiating the processing

    param_file = json_run_dir + '/' + label + '_' + prefix + '.json'

    assert os.path.exists(param_file)

    with open(param_file) as f:
        outputparams = json.load(f)

    expectedrender = dict(render_json)
    expectedrender['render']['owner'] = inp_sel
    expectedrender['render']['project'] = test_projname

    assert outputparams['render'] == expectedrender['render']

    assert outputparams['stack'] == test_stackname
    assert outputparams['image_directory'] == os.getcwd()

    assert outputparams['close_stack'] == 'True'


@pytest.mark.dependency(depends=["test_webUI"])
def test_conv_SerialEM(thisdash):
    inp_sel = 'SerialEM'
    inp_module = 'serialem_conv'
    label = module + '_' + inp_sel

    thisdash.driver.get(thisdash.server_url + '/' + module)

    # check input type dropdown -> subpage selection
    input_dd = thisdash.find_element(module_selector('import_type_dd', module))

    input_dd.clear()
    input_dd.send_keys(inp_sel, Keys.RETURN)

    check_browsedir(thisdash, inp_sel)

    check_renderselect(thisdash, label, components={'owner': 'SerialEM', 'project': True, 'stack': True})

    # Check the go callback
    # ====================================

    stack_el = ("stack_dd", label)
    stack_val = 'newstack'

    dir_el = ("path_input", label)
    dir_val = 'test_idoc.idoc'

    in_status = {'logfile': 'out.txt', 'status': 'input'}

    os.system('touch test_idoc.idoc')

    # check 1 :    new stack -> disabled button

    context_value.set(set_callback_context(stack_el, stack_val))

    result = serialem_conv_gobutton(stack_val, dir_val, 1, 'test', 'standalone', dict(in_status), {})

    assert result[0]
    assert result[1] == ''
    assert result[2] == {'logfile': 'out.txt', 'status': 'wait'}
    assert type(result[3]) is dash._callback.NoUpdate

    # check 2:  other stack -> enabled button
    context_value.set(set_callback_context(stack_el, 'test'))
    result = serialem_conv_gobutton('test', dir_val, 1, 'test', 'standalone', dict(in_status), {})

    assert result[0] is False
    assert result[1] == ''
    assert result[2] == in_status
    assert type(result[3]) is dash._callback.NoUpdate

    # check 3:  wrong directory characters
    result = serialem_conv_gobutton('test', 'this directory/has wrong chars!', 1,
                                    'test', 'standalone', dict(in_status), {})

    assert result[0]
    assert result[1] == 'Wrong characters in input directory path. Please fix!'
    assert result[2] == {'logfile': 'out.txt', 'status': 'wait'}
    assert type(result[3]) is dash._callback.NoUpdate

    # check 4: click go button and launch processing
    gobutton_el = label + 'go'

    context_value.set(set_callback_context(gobutton_el, 1, valkey='n_clicks'))

    test_projname = 'testproject'
    test_stackname = 'teststack'

    prefix = run_prefix()
    result = serialem_conv_gobutton(test_stackname, os.getcwd(), 1, test_projname, 'test', dict(in_status), {})

    assert result[0]
    assert result[1] == ''

    assert result[2]['type'] == 'test'
    assert result[2]['id'] == 'test_launch'
    assert result[2]['status'] == 'running'
    assert prefix in result[2]['logfile']
    assert inp_module in result[2]['logfile']

    assert result[3] == {'owner': 'SerialEM', 'project': 'testproject', 'stack': 'teststack'}

    #     check parameter file output for initiating the processing

    param_file = json_run_dir + '/' + label + '_' + prefix + '.json'

    assert os.path.exists(param_file)

    with open(param_file) as f:
        outputparams = json.load(f)

    expectedrender = dict(render_json)
    expectedrender['render']['owner'] = inp_sel
    expectedrender['render']['project'] = test_projname

    assert outputparams['render'] == expectedrender['render']

    assert outputparams['stack'] == test_stackname
    assert outputparams['image_file'] == os.getcwd()

    assert outputparams['close_stack'] == 'True'

    # check 5:  bad input directory -> popup text, disabled button
    context_value.set(set_callback_context(dir_el, dir_val))

    os.system('rm test_idoc.idoc')

    result = serialem_conv_gobutton(stack_val, dir_val, 1, 'test', 'standalone', dict(in_status), {})

    assert result[0]
    assert result[1] == 'Input Data not accessible.'
    assert result[2] == {'logfile': 'out.txt', 'status': 'wait'}
    assert type(result[3]) is dash._callback.NoUpdate

    #     check parameter file output for initiating the processing

    param_file = json_run_dir + '/' + label + '_' + prefix + '.json'

    assert os.path.exists(param_file)

    with open(param_file) as f:
        outputparams = json.load(f)

    expectedrender = dict(render_json)
    expectedrender['render']['owner'] = inp_sel
    expectedrender['render']['project'] = test_projname

    assert outputparams['render'] == expectedrender['render']

    assert outputparams['stack'] == test_stackname
    assert outputparams['image_directory'] == os.getcwd()

    assert outputparams['close_stack'] == 'True'

@pytest.mark.dependency(depends=["test_webUI"])
def test_conv_fibsem(thisdash):
    inp_sel = 'FIBSEM'
    inp_module = 'fibsem_conv'
    label = module + '_' + inp_sel

    thisdash.driver.get(thisdash.server_url + '/' + module)

    # check input type dropdown -> subpage selection
    input_dd = thisdash.find_element(module_selector('import_type_dd', module))

    input_dd.clear()
    input_dd.send_keys(inp_sel, Keys.RETURN)

    check_browsedir(thisdash, inp_sel)

    check_renderselect(thisdash, label, components={'owner': 'FIBSEM', 'project': True, 'stack': True})

    # check resolution values
    resdiv = thisdash.find_element('#fibsem_stack_resolution_div')

    xyinput = resdiv.find_element(By.XPATH, './input[contains(@id,"xy_px_input")]')
    zinput = resdiv.find_element(By.XPATH, './input[contains(@id,"z_px_input")]')

    assert xyinput.get_attribute('value') == '10'
    assert zinput.get_attribute('value') == '10'

    validstyle = xyinput.value_of_css_property('outline')

    xyinput.clear()
    xyinput.send_keys('abs')
    assert xyinput.value_of_css_property('outline') != validstyle

    xyinput.clear()
    xyinput.send_keys('0')
    assert xyinput.value_of_css_property('outline') != validstyle

    xyinput.clear()
    xyinput.send_keys('10')
    assert xyinput.value_of_css_property('outline') == validstyle

    zinput.clear()
    zinput.send_keys('abs')
    assert zinput.value_of_css_property('outline') != validstyle

    zinput.clear()
    zinput.send_keys('0')
    assert zinput.value_of_css_property('outline') != validstyle

    zinput.clear()
    zinput.send_keys('20')
    assert zinput.value_of_css_property('outline') == validstyle


    # Check the go callback
    # ====================================

    stack_el = ("stack_dd", label)
    stack_val = 'newstack'

    dir_el = ("path_input", label)
    dir_val = 'notexistingdirectory'

    in_status = {'logfile': 'out.txt', 'status': 'input'}

    # check 1:  new stack -> disabled button
    context_value.set(set_callback_context(stack_el, stack_val))

    result = fibsem_conv_gobutton(stack_val, os.getcwd(), 1, 'test', 'standalone', 10, 10, dict(in_status), {})

    assert result[0]
    assert result[1] == ''
    assert result[2] == {'logfile': 'out.txt', 'status': 'wait'}
    assert type(result[3]) is dash._callback.NoUpdate

    # check 2:  other stack -> enabled button
    context_value.set(set_callback_context(stack_el, 'test'))
    result = fibsem_conv_gobutton('test', os.getcwd(), 1, 'test', 'standalone', 10, 10, dict(in_status), {})

    assert result[0] is False
    assert result[1] == ''
    assert result[2] == in_status
    assert type(result[3]) is dash._callback.NoUpdate

    # check 3:  bad input directory -> popup text, disabled button
    context_value.set(set_callback_context(dir_el, dir_val))

    result = fibsem_conv_gobutton('test', dir_val, 1, 'test', 'standalone', 10, 10, dict(in_status), {})

    assert result[0]
    assert result[1] == 'Input Data not accessible.'
    assert result[2] == {'logfile': 'out.txt', 'status': 'wait'}
    assert type(result[3]) is dash._callback.NoUpdate

    # check 4:  wrong directory characters
    result = fibsem_conv_gobutton('test', 'this directory/has wrong chars!', 1,
                                  'test', 'standalone', 10, 10, dict(in_status), {})

    assert result[0]
    assert result[1] == 'Wrong characters in input directory path. Please fix!'
    assert result[2] == {'logfile': 'out.txt', 'status': 'wait'}
    assert type(result[3]) is dash._callback.NoUpdate

    # check 5: click go button and launch processing
    gobutton_el = label + 'go'

    context_value.set(set_callback_context(gobutton_el, 1, valkey='n_clicks'))

    test_projname = 'testproject'
    test_stackname = 'teststack'

    prefix = run_prefix()
    result = fibsem_conv_gobutton(test_stackname, os.getcwd(), 1, test_projname, 'test', 10, 20, dict(in_status), {})

    assert result[0]
    assert result[1] == ''

    assert result[2]['type'] == 'test'
    assert result[2]['id'] == 'test_launch'
    assert result[2]['status'] == 'running'
    assert prefix in result[2]['logfile']
    assert inp_module in result[2]['logfile']

    assert result[3] == {'owner': 'FIBSEM', 'project': 'testproject', 'stack': 'teststack'}

    #     check parameter file output for initiating the processing

    param_file = json_run_dir + '/' + label + '_' + prefix + '.json'

    assert os.path.exists(param_file)

    with open(param_file) as f:
        outputparams = json.load(f)

    expectedrender = dict(render_json)
    expectedrender['render']['owner'] = inp_sel
    expectedrender['render']['project'] = test_projname

    assert outputparams['render'] == expectedrender['render']

    assert outputparams['stack'] == test_stackname
    assert outputparams['image_directory'] == os.getcwd()

    assert outputparams['pxs'] == [10, 10, 20]

    assert outputparams['close_stack'] == 'True'
