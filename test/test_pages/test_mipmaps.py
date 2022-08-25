#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""
import os
import pytest
import time
import json
import requests

import dash
from dash._callback_context import context_value

from dashUI import params
from dashUI.index import menu_items
from dashUI.callbacks.pages_cb.cb_mipmaps import (mipmaps_stacktodir,
                                                  mipmaps_gobutton,
                                                  mipmaps_store_compute_settings)
from dashUI.callbacks.substack_sel import stacktoparams

from helpers import check_browsedir, \
    get_renderparams, \
    check_renderselect, \
    set_callback_context, \
    multi_context

module = 'mipmaps'


@pytest.mark.skipif(module not in menu_items, reason="module not included")
@pytest.mark.dependency(depends=["webUI"],
                        scope='session')
def test_mipmaps(thisdash, startup_webui):
    thisdash.driver.get(thisdash.server_url + '/' + module)
    # check_renderselect(thisdash, module)
    time.sleep(2)
    check_browsedir(thisdash, module)

    # check directory extraction from render metadata
    sel_stack, renderparams, allstacks = get_renderparams()

    stack_el = ("stack_dd", module)
    stack_val = sel_stack['stack']

    context_value.set(set_callback_context(stack_el, stack_val))

    # check skip states

    # wrong page
    with pytest.raises(dash.exceptions.PreventUpdate):
        result = mipmaps_stacktodir('stack', 'owner', 'project', 'stack', [1, 2, 3], '/wrongpage')

    # empty page
    with pytest.raises(dash.exceptions.PreventUpdate):
        result = mipmaps_stacktodir('stack', 'owner', 'project', 'stack', [1, 2, 3], '')

    # empty stack
    result = mipmaps_stacktodir('-', 'owner', 'project', 'stack', [1, 2, 3], '/mipmaps')
    assert result == ['', 'stack', '', '', '', '', 1, 1, 1]

    # empty stacklist
    result = mipmaps_stacktodir('stack', 'owner', 'project', 'stack', [], '/mipmaps')
    assert result == ['', 'stack', '', '', '', '', 1, 1, 1]

    # check correct parameters

    datadir = os.path.abspath(
        renderparams['tileSpecs'][0]['mipmapLevels']['0']['imageUrl'].lstrip('file:'))

    expected_dir = os.path.join(os.sep, *datadir.split(os.sep)[:-params.datadirdepth[sel_stack['owner']] - 1])

    result = mipmaps_stacktodir(sel_stack['stack'], sel_stack['owner'], sel_stack['project'], sel_stack['stack'],
                                allstacks, '/mipmaps')

    assert result[0] == expected_dir
    for r in result[1:3]:
        assert r == sel_stack['stack']

    for r in result[3:6]:
        assert type(r) is str

    for r in result[3:]:
        try:
            float(r)
        finally:
            pass

    # check go callback
    inp_el = ("path_input", module)
    inp_val = os.path.abspath(os.path.join(params.base_dir, 'test'))

    context_value.set(set_callback_context(inp_el, inp_val))

    in_status = {'logfile': 'out.txt', 'status': 'input'}

    # check empty dir
    result = mipmaps_gobutton('', 1, 2, in_status, 'test', 'rs_in', 'owner', 'project', 'stack',
                              {}, {}, True, [], '', {})

    assert result[:3] == (True, [], 'rs_in')
    assert type(result[3]) == dash._callback.NoUpdate
    assert result[4] == {}

    result = mipmaps_gobutton(None, 1, 2, in_status, 'test', 'rs_in', 'owner', 'project', 'stack',
                              {}, {}, True, [], '', {})

    assert result[:3] == (True, [], 'rs_in')
    assert type(result[3]) == dash._callback.NoUpdate
    assert result[4] == {}

    # check existing dir
    os.system('mkdir ' + os.path.join(inp_val, params.mipmapdir))

    result = mipmaps_gobutton(inp_val, 1, 2, in_status, 'test', 'rs_in', 'owner', 'project', 'stack',
                              {}, {}, True, [], '', {})

    assert result[0] == False

    assert type(result[1]) == dash.dcc.ConfirmDialog
    assert result[1].message == 'Warning: there already exists a MipMap directory. Will overwrite it.'
    assert result[1].id == {'component': 'danger-novaliddir', 'module': 'mipmaps'}
    assert result[1].displayed == True

    assert result[2] == 'rs_in'
    assert type(result[3]) == dash._callback.NoUpdate
    assert result[4] == {}

    os.system('rm -r '+ os.path.join(inp_val, params.mipmapdir))

    # enable go button

    result = mipmaps_gobutton(inp_val, 1, 2, in_status, 'test', 'rs_in', 'owner', 'project', 'stack',
                              {}, {}, True, [], '', {})

    assert result[:3] == (False, [], 'rs_in')
    assert type(result[3]) == dash._callback.NoUpdate
    assert result[4] == {}

    # do not check for sequential run state, this needs to be re-done in the call!

    # check for initial launch call

    go_el = ("go", module)
    go_val = 1

    context_value.set(set_callback_context(go_el, go_val))

    stackparams = stacktoparams(sel_stack['stack'], allstacks, '/mipmaps')

    context_value.set(multi_context(set_callback_context(go_el, 1, context='inputs'), set_callback_context(go_el, 1)))

    compset = mipmaps_store_compute_settings(1,2,3,'/mipmaps')

    result = mipmaps_gobutton(inp_val, 1, 2, in_status, 'test', 'rs_in', 'owner', 'project', 'stack',
                              stackparams, {}, True, [], '', {})

