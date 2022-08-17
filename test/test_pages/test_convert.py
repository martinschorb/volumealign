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

def test_convert(dash_duo):
    app = import_app("dashUI.app")
    dash_duo.start_server(app)
    wait = WebDriverWait(dash_duo.driver, 10)

    dash_duo.driver.get(dash_duo.server_url + '/' + module)

    # check input type dropdown -> subpage selection
    input_dd = dash_duo.find_element(module_selector('import_type_dd', module))

    inputtypes = ['SBEM', 'SerialEM', 'tifstack']

    check_subpages(inputtypes, input_dd, module, dash_duo)
