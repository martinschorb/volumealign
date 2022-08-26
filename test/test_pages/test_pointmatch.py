#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""

import dash

import os
import json
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from dash._callback_context import context_value

# import callbacks to check


from dashUI.utils.launch_jobs import run_prefix
from dashUI import params

from helpers import (module_selector,
                     check_subpages,
                     get_renderparams,
                     check_renderselect,
                     check_matchselect,
                     check_inputvalues,
                     check_tiles,
                     set_callback_context,
                     set_stack)

module = 'pointmatch'


@pytest.mark.dependency(depends=["webUI"],
                        scope='session')
def test_pointmatch(thisdash, startup_webui, prepare_teststack):
    thisdash.driver.get(thisdash.server_url + '/' + module)

    # check input type dropdown -> subpage selection
    input_dd = thisdash.find_element(module_selector('pm_type_dd', module))

    inputtypes = ['SIFT']

    # LAYOUT of pointmatch does not adhere to subpage-style!!!
    # check_subpages(inputtypes, input_dd, module, thisdash)

    check_tiles(thisdash, module)

    check_renderselect(thisdash, module)

    stack = get_renderparams()[0]

    set_stack(thisdash, module, stack)

    tp_template = os.path.join(params.base_dir, 'test', 'test_files', 'tilepairtest')

    tpdirname = 'tilepairs_' + params.user + '_test_' + stack['stack']

    tp_new = os.path.join(params.json_run_dir, tpdirname)

    os.system('cp -r ' + tp_template + ' ' + tp_new)

    tp_dd = thisdash.driver.find_element(By.XPATH, '//div[@class="dash-dropdown" and contains(@id,"tp_dd")'
                                                   ' and contains(@id,"' + module + '")]')

    thisdash.select_dcc_dropdown(tp_dd, value=tpdirname)

    assert tp_dd.text == tpdirname

    check_matchselect(thisdash, module, stack, components={'mc_owner': True, 'matchcoll': True})

# @pytest.mark.dependency(depends=["webUI"],
#                         scope='session')
# def test_conv_fibsem(thisdash, startup_webui):
#     inp_sel = 'FIBSEM'
#     inp_module = 'fibsem_conv'
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
#     check_renderselect(thisdash, label, components={'owner': 'FIBSEM', 'project': True, 'stack': True})
#
#     # check resolution values
#     resdiv = thisdash.find_element('#fibsem_stack_resolution_div')
#
#     xyinput = resdiv.find_element(By.XPATH, './input[contains(@id,"xy_px_input")]')
#     zinput = resdiv.find_element(By.XPATH, './input[contains(@id,"z_px_input")]')
#
#     assert xyinput.get_attribute('value') == '10'
#     assert zinput.get_attribute('value') == '10'
#
#     zinput.clear()
#     zinput.send_keys('20')
#
#     testvalues = {'2': True, '0': False, 'abc': False}
#     check_inputvalues(xyinput, testvalues)
#     check_inputvalues(zinput, testvalues)
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
#     result = fibsem_conv_gobutton(stack_val, os.getcwd(), 1, 'test', 'standalone', 10, 10, dict(in_status), {})
#
#     assert result[0]
#     assert result[1] == ''
#     assert result[2] == {'logfile': 'out.txt', 'status': 'wait'}
#     assert type(result[3]) is dash._callback.NoUpdate
#
#     # check 2:  other stack -> enabled button
#     context_value.set(set_callback_context(stack_el, 'test'))
#     result = fibsem_conv_gobutton('test', os.getcwd(), 1, 'test', 'standalone', 10, 10, dict(in_status), {})
#
#     assert not result[0]
#     assert result[1] == ''
#     assert result[2] == in_status
#     assert type(result[3]) is dash._callback.NoUpdate
#
#     # check 3:  bad input directory -> popup text, disabled button
#     context_value.set(set_callback_context(dir_el, dir_val))
#
#     result = fibsem_conv_gobutton('test', dir_val, 1, 'test', 'standalone', 10, 10, dict(in_status), {})
#
#     assert result[0]
#     assert result[1] == 'Input Data not accessible.'
#     assert result[2] == {'logfile': 'out.txt', 'status': 'wait'}
#     assert type(result[3]) is dash._callback.NoUpdate
#
#     # check 4:  wrong directory characters
#     result = fibsem_conv_gobutton('test', 'this directory/has wrong chars!', 1,
#                                   'test', 'standalone', 10, 10, dict(in_status), {})
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
#     test_projname = 'testproject'
#     test_stackname = 'testtack'
#
#     prefix = run_prefix()
#     result = fibsem_conv_gobutton(test_stackname, os.getcwd(), 1, test_projname, 'test', 10, 20, dict(in_status), {})
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
#     assert result[3] == {'owner': 'FIBSEM', 'project': 'testproject', 'stack': 'testtack'}
#
#     #     check parameter file output for initiating the processing
#
#     param_file = json_run_dir + '/' + label + '_' + prefix + '.json'
#
#     assert os.path.exists(param_file)
#
#     with open(param_file) as f:
#         outputparams = json.load(f)
#
#     expectedrender = dict(render_json)
#     expectedrender['render']['owner'] = inp_sel
#     expectedrender['render']['project'] = test_projname
#
#     assert outputparams['render'] == expectedrender['render']
#
#     assert outputparams['stack'] == test_stackname
#     assert outputparams['image_directory'] == os.getcwd()
#
#     assert outputparams['pxs'] == [10, 10, 20]
#
#     assert outputparams['close_stack'] == 'True'
