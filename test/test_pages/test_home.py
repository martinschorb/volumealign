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
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from dashUI.index import title_header, home_title, menu_items
from dashUI import params

from helpers import check_link

@pytest.mark.dependency(depends=["webUI"],
                        scope='session')
def test_home(thisdash, startup_webui):
    # need to be generous with timeouts due to large images being requested
    wait = WebDriverWait(thisdash.driver, 30)

    navbar_elem = thisdash.find_element("#navbar")

    # check title
    assert navbar_elem.text == title_header

    # check help link
    helplink = navbar_elem.find_element(By.CSS_SELECTOR, '#helplink_image')

    check_link(thisdash, helplink, params.doc_url)

    titles = []
    for page in menu_items:
        with open(os.path.join(params.base_dir, 'dashUI', 'pages', page + '.py')) as f:
            psource = f.read()
            titles.append(psource.split("  name='")[1].split("')\n")[0])

    # check all subpages
    for submenu, subpagetitle in zip(menu_items, titles):
        menubutton = thisdash.driver.find_element(By.LINK_TEXT, subpagetitle)
        menubutton.click()

        wait.until(EC.title_is(subpagetitle))

        assert thisdash.driver.current_url.endswith(submenu)

    # check top link back to home page

    navbar_elem.click()

    time.sleep(0.5)

    assert thisdash.driver.current_url == thisdash.server_url + '/'

    assert thisdash.driver.title == home_title
