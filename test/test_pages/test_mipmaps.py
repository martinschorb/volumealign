#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""

import dash

import time
import os
import pytest

from selenium.webdriver.common.by import By

from helpers import check_browsedir, \
    check_renderselect, \
    set_callback_context

module = 'mipmaps'

@pytest.mark.dependency(depends=["webUI"],
                        scope='session')
def test_mipmaps(thisdash, startup_webui):
    thisdash.driver.get(thisdash.server_url + '/' + module)
    check_renderselect(thisdash, module)

