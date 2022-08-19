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

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from contextvars import copy_context
from dash._callback_context import context_value
from dash._utils import AttributeDict

from dashUI.inputtypes.sbem_conv import sbem_conv_gobutton
from dashUI.utils.launch_jobs import run_prefix

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

    inputtypes = ['SBEM', 'SerialEM', 'tifstack']

    check_subpages(inputtypes, input_dd, module, thisdash)


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

    result = sbem_conv_gobutton(stack_val, os.getcwd(), 1, 'test', 'standalone', in_status, {})

    assert result[0]
    assert result[1] == ''
    assert result[2] == in_status
    assert type(result[3]) is dash._callback.NoUpdate

    # check 2:  other stack -> enabled button
    context_value.set(set_callback_context(stack_el, 'test'))
    result = sbem_conv_gobutton('test', os.getcwd(), 1, 'test', 'standalone', in_status, {})

    assert result[0] is False
    assert result[1] == ''
    assert result[2] == in_status
    assert type(result[3]) is dash._callback.NoUpdate

    # check 3:  bad input directory -> popup text, disabled button
    context_value.set(set_callback_context(dir_el, dir_val))

    result = sbem_conv_gobutton('test', dir_val, 1, 'test', 'standalone', in_status, {})

    assert result[0]
    assert result[1] == 'Directory not accessible.'
    assert result[2] == {'logfile': 'out.txt', 'status': 'wait'}
    assert type(result[3]) is dash._callback.NoUpdate

    # check 4:  wrong directory characters
    result = sbem_conv_gobutton('test', 'this directory/has wrong chars!', 1, 'test', 'standalone', in_status, {})

    assert result[0]
    assert result[1] == 'Wrong characters in input directory path. Please fix!'
    assert result[2] == {'logfile': 'out.txt', 'status': 'wait'}
    assert type(result[3]) is dash._callback.NoUpdate

    # check 5: click go button and launch processing
    gobutton_el = label + 'go'

    context_value.set(set_callback_context(gobutton_el, 1, valkey='n_clicks'))

    prefix = run_prefix()
    result = sbem_conv_gobutton('teststack', os.getcwd(), 1, 'testproject', 'test', in_status, {})

    assert result[0]
    assert result[1] == ''

    assert result[2]['type'] == 'test'
    assert result[2]['id'] == 'test_launch'
    assert result[2]['status'] == 'running'
    assert prefix in result[2]['logfile']
    assert inp_module in result[2]['logfile']

    assert result[3] == {'owner': 'SBEM', 'project': 'testproject', 'stack': 'teststack'}


# def test_conv_SerialEM(thisdash):
#     inp_sel = 'SerialEM'
#     inp_module = 'serialem_conv'
#     label = module + '_' + inp_sel
#
#     thisdash.driver.get(thisdash.server_url + '/' + module)
#
#     # check input type dropdown -> subpage selection
#     input_dd = thisdash.find_element(module_selector('import_type_dd', module))
#
#     input_dd.clear()
#     input_dd.send_keys(inp_sel, Keys.RETURN)
#
#     check_browsedir(thisdash, inp_sel)
#
#     check_renderselect(thisdash, label, components={'owner': 'SerialEM', 'project': True, 'stack': True})
#
#     # Check the go callback
#     # ====================================
#
#     stack_el = ("stack_dd", label)
#     stack_val = 'newstack'
#
#     dir_el = ("path_input", label)
#     dir_val = 'notexistingdirectory'
#
#     in_status = {'logfile': 'out.txt', 'status': 'input'}
#
#     # check 1:  new stack -> disabled button
#     context_value.set(set_callback_context(stack_el, stack_val))
#
#     result = sbem_conv_gobutton(stack_val, os.getcwd(), 1, 'test', 'standalone', in_status, {})
#
#     assert result[0]
#     assert result[1] == ''
#     assert result[2] == in_status
#     assert type(result[3]) is dash._callback.NoUpdate
#
#     # check 2:  other stack -> enabled button
#     context_value.set(set_callback_context(stack_el, 'test'))
#     result = sbem_conv_gobutton('test', os.getcwd(), 1, 'test', 'standalone', in_status, {})
#
#     assert result[0] is False
#     assert result[1] == ''
#     assert result[2] == in_status
#     assert type(result[3]) is dash._callback.NoUpdate
#
#     # check 3:  bad input directory -> popup text, disabled button
#     context_value.set(set_callback_context(dir_el, dir_val))
#
#     result = sbem_conv_gobutton('test', dir_val, 1, 'test', 'standalone', in_status, {})
#
#     assert result[0]
#     assert result[1] == 'Directory not accessible.'
#     assert result[2] == {'logfile': 'out.txt', 'status': 'wait'}
#     assert type(result[3]) is dash._callback.NoUpdate
#
#     # check 4:  wrong directory characters
#     result = sbem_conv_gobutton('test', 'this directory/has wrong chars!', 1, 'test', 'standalone', in_status, {})
#
#     assert result[0]
#     assert result[1] == 'Wrong characters in input directory path. Please fix!'
#     assert result[2] == {'logfile': 'out.txt', 'status': 'wait'}
#     assert type(result[3]) is dash._callback.NoUpdate
#
#     # check 5: click go button and launch processing
#     gobutton_el = label + 'go'
#
#     context_value.set(set_callback_context(gobutton_el, 1, valkey='n_clicks'))
#
#     prefix = run_prefix()
#     result = sbem_conv_gobutton('teststack', os.getcwd(), 1, 'testproject', 'test', in_status, {})
#
#     assert result[0]
#     assert result[1] == ''
#
#     assert result[2]['type'] == 'test'
#     assert result[2]['id'] == 'test_launch'
#     assert result[2]['status'] == 'running'
#     assert prefix in result[2]['logfile']
#     assert inp_module in result[2]['logfile']
#
#     assert result[3] == {'owner': 'SerialEM', 'project': 'testproject', 'stack': 'teststack'}
