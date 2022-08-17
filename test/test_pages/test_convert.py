#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""

from dash.testing.application_runners import import_app
import dash

import requests
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from dashUI.callbacks.pages_cb.cb_convert import convert_output

from helpers import css_escape, module_selector, check_subpages

module = 'convert'

def test_convert(thisdash):

    thisdash.driver.get(thisdash.server_url + '/' + module)

    # check input type dropdown -> subpage selection
    input_dd = thisdash.find_element(module_selector('import_type_dd', module))

    inputtypes = ['SBEM', 'SerialEM', 'tifstack']

    check_subpages(inputtypes, input_dd, module, thisdash)


def test_conv_SBEM(thisdash):
    inp_sel = 'SBEM'

    thisdash.driver.get(thisdash.server_url + '/' + module)

    # check input type dropdown -> subpage selection
    input_dd = thisdash.find_element(module_selector('import_type_dd', module))

    input_dd.clear()
    input_dd.send_keys(inp_sel, Keys.RETURN)

    pathinputs = thisdash.driver.find_elements(By.XPATH, '//input[@class="dir_textinput"]')

    for p_input in pathinputs:
        if inp_sel in p_input.get_attribute('id'):
            break

    p_input.send_keys(Keys.META, 'A', Keys.BACKSPACE)
    p_input.send_keys(Keys.CONTROL, 'A', Keys.BACKSPACE)







