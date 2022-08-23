#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""
import os
import pytest
import json
import requests

from dash._callback_context import context_value

from dashUI import params
from dashUI.callbacks.pages_cb.cb_mipmaps import mipmaps_stacktodir

from helpers import check_browsedir, \
    get_renderparams, \
    check_renderselect, \
    set_callback_context

module = 'mipmaps'


@pytest.mark.dependency(depends=["webUI"],
                        scope='session')
def test_mipmaps(thisdash, startup_webui):
    thisdash.driver.get(thisdash.server_url + '/' + module)
    # check_renderselect(thisdash, module)

    check_browsedir(thisdash, module)

    # check directory extraction from render metadata

    sel_stack, renderparams, allstacks = get_renderparams()

    datadir = os.path.abspath(
        renderparams['tileSpecs'][0]['mipmapLevels']['0']['imageUrl'].lstrip('file:'))

    expected_dir = os.path.join(os.sep, *datadir.split(os.sep)[:-params.datadirdepth[sel_stack['owner']] - 1])

    stack_el = ("stack_dd", module)
    stack_val = sel_stack['stack']

    context_value.set(set_callback_context(stack_el, stack_val))

    result = mipmaps_stacktodir(sel_stack['stack'], sel_stack['owner'], sel_stack['project'],sel_stack['stack'],
                                    allstacks, '/mipmaps')

    assert result[0] == expected_dir

