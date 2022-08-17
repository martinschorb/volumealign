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

from dashUI.index import title_header, home_title, menu_items
from dashUI import params

def test_home(thisdash):
    
    wait = WebDriverWait(thisdash.driver, 10)

    navbar_elem = thisdash.find_element("#navbar")

    # check title
    assert navbar_elem.text == title_header

    # check help link
    helplink = navbar_elem.find_element(By.CSS_SELECTOR,'#helplink_image')

    #check if image is loaded properly
    help_imlink = helplink.get_attribute('src')
    response = requests.get(help_imlink, stream=True)

    assert response.status_code == 200

    #check if help redirect works

    # Store the ID of the original window
    original_window = thisdash.driver.current_window_handle

    # Check we don't have other windows open already
    assert len(thisdash.driver.window_handles) == 1

    # click the link to open the help page
    helplink.click()

    # Wait for the new window or tab
    wait.until(EC.number_of_windows_to_be(2))

    for window_handle in thisdash.driver.window_handles:
        if window_handle != original_window:
            thisdash.driver.switch_to.window(window_handle)

            assert thisdash.driver.current_url == params.doc_url
            response = requests.get(thisdash.driver.current_url)

            assert response.status_code == 200

            thisdash.driver.close()
            thisdash.driver.switch_to.window(original_window)


    reg = list(dash.page_registry.values())

    paths = []
    for page in reg:
        paths.append(page["path"].strip('/'))

    # check all subpages
    for submenu in menu_items:
        subpagetitle = reg[paths.index(submenu)]["name"]
        menubutton = thisdash.driver.find_element(By.LINK_TEXT, subpagetitle)
        menubutton.click()

        wait.until(EC.title_is(subpagetitle))

        assert thisdash.driver.current_url.endswith(submenu)

    #check top link back to home page

    navbar_elem.click()

    time.sleep(0.5)

    assert thisdash.driver.current_url == thisdash.server_url + '/'

    assert thisdash.driver.title == home_title
