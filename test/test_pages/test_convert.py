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
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_convert(dash_duo):
    app = import_app("dashUI.app")
    dash_duo.start_server(app)
    wait = WebDriverWait(dash_duo.driver, 10)

    dash_duo.driver.get(dash_duo.server_url + '/convert')
