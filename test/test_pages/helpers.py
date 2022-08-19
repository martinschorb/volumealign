#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""
import os
import re
import time
import requests

from dashUI.params import base_dir, render_base_url
from dashUI.utils.checks import clean_render_name

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

teststring = 'randomstringthatshouldbe;;nowherelse' + time.asctime()


def css_escape(s):
    """
    creates CSS compatible IDs for dash pattern-matching dictionary IDs

    :param str s: input string
    :return: CSS compatible ID string
    :rtype: str
    """
    sel = re.sub("[\\{\\}\\\"\\'.:,]", lambda m: "\\" + m.group(0), s)
    return sel


def module_selector(component, module):
    selector = css_escape('#{"component":"' + component + '","module":"' + module + '"} input')
    return selector


def check_subpages(subpage_ids, input_dd, module, dashtest_el, sub_elements=None):
    """
    checks a page containing subpages for properly displaying the following elements for each selected value

    - nullpage
    - page1
    - console-out
    - compute_sel

    :param list subpage_ids: list of subpage labels to check
    :param selenium.webdriver.remote.webelement.WebElement input_dd: the dropdown element to trigger subpage selection
    :param str module: the name of the current module
    :param dash.testing.composite.DashComposite dashtest_el: the dash testing instance
    :param list sub_elements: optional list of elements to test (from list above)
    """

    if sub_elements is None:
        sub_elements = ['nullpage', 'page1', 'console-out', 'compute_sel']

    for spidx, inp_sel in enumerate(subpage_ids):
        input_dd.clear()
        input_dd.send_keys(inp_sel, Keys.RETURN)

        seldiv = dashtest_el.driver.find_element(By.CLASS_NAME, 'subpage')
        subpagedivs = seldiv.find_elements(By.XPATH, './div')

        if 'nullpage' in sub_elements:
            assert subpagedivs[0].get_attribute('id') == module + '_nullpage'

        if 'console-out' in sub_elements:
            logtextboxes = dashtest_el.driver.find_elements(By.XPATH, '//textarea')

        for checkidx in range(len(subpage_ids) + 1):
            if checkidx == spidx + 1:
                if 'page1' in sub_elements:
                    assert subpagedivs[checkidx].get_attribute(
                        'id') == '{"component":"page1","module":"' + inp_sel + '"}'
                    assert subpagedivs[checkidx].get_attribute('style') != 'display: none;'

                if 'console-out' in sub_elements:
                    assert logtextboxes[checkidx - 1].get_attribute('id') == \
                           '{"component":"console-out","module":"' + module + '_' + inp_sel + '"}'

            else:
                assert subpagedivs[checkidx].get_attribute('style') == 'display: none;'

        if 'compute_sel' in sub_elements:
            compute_loc = dashtest_el.find_element(module_selector('compute_sel', module + '_' + inp_sel))
            assert compute_loc.get_attribute('type') == 'radio'


def checklink(thisdash, link, target):
    wait = WebDriverWait(thisdash.driver, 10)

    # check if link image is loaded properly
    if link.tag_name == 'img':
        imlink = link.get_attribute('src')
        response = requests.get(imlink, stream=True, verify=False)

        assert response.status_code == 200

    # check if help redirect works

    # Store the ID of the original window
    original_window = thisdash.driver.current_window_handle

    # Check we don't have other windows open already
    assert len(thisdash.driver.window_handles) == 1

    # click the link to open the help page
    link.click()

    # Wait for the new window or tab
    wait.until(EC.number_of_windows_to_be(2))

    for window_handle in thisdash.driver.window_handles:
        if window_handle != original_window:
            thisdash.driver.switch_to.window(window_handle)
            wait.until(EC.url_to_be(target))

            response = requests.get(thisdash.driver.current_url, verify=False)

            assert response.status_code == 200

            thisdash.driver.close()
            thisdash.driver.switch_to.window(original_window)


def check_browsedir(thisdash, module):
    """
    Checks functionality of a directory browse element

    :param dash.testing.composite.DashComposite thisdash: the dash testing instance
    :param str module: the name of the current module
    """

    pathinputs = thisdash.driver.find_elements(By.XPATH, '//input[@class="dir_textinput"]')

    for p_input in pathinputs:
        if module in p_input.get_attribute('id'):
            break

    p_input.send_keys(Keys.META, 'A', Keys.BACKSPACE)
    p_input.send_keys(Keys.CONTROL, 'A', Keys.BACKSPACE)

    p_input.send_keys(os.path.abspath(os.path.join(base_dir, 'test')))

    sums = thisdash.driver.find_elements(By.XPATH, '//summary')

    for summary in sums:
        if 'Browse' == summary.text:
            break

    summary.click()

    dropdowns = thisdash.driver.find_elements(By.XPATH, '//div[@class="dash-dropdown"]')

    for dropdown in dropdowns:
        if module in dropdown.get_attribute('id') and 'browse_dd' in dropdown.get_attribute('id'):
            break

    dropdown.click()

    menu = dropdown.find_element(By.CSS_SELECTOR, "div.Select-menu-outer")
    options = menu.find_elements(By.CSS_SELECTOR, "div.VirtualizedSelectOption")

    assert len(options) > 1
    assert options[0].text == '..'

    testdirs = []

    for browseitem in options[1:]:
        # check if all items are directories
        assert browseitem.text.startswith('↪')

        currdir = ' '.join((browseitem.text.split(' ')[1:]))

        assert os.path.exists(os.path.join(base_dir, 'test', currdir))

        testdirs.append(currdir)

    assert 'test_files' in testdirs

    summary.click()


def check_renderselect(thisdash, module, components=None):
    if components is None:
        # all three selectors without creating new items
        components = {'owner': False, 'project': False, 'stack': False}

    elif type(components) is not dict:
        raise TypeError('components need to be dict')

    selection = {}

    for component in components.keys():

        sel_dd = thisdash.driver.find_element(By.XPATH, '//div[@class="dash-dropdown" and contains(@id,"' +
                                              component + '") and contains(@id,"' + module + '")]')

        target = render_base_url + 'view/stacks.html?'

        if 'owner' in selection.keys():
            target += 'renderStackOwner=' + selection['owner'] + '&'

        if 'project' in selection.keys():
            target += 'renderStackProject=' + selection['project']

        if type(components[component]) is str:
            selection[component] = components[component]
        else:
            sel_dd.click()
            menu = sel_dd.find_element(By.CSS_SELECTOR, "div.Select-menu-outer")
            options = menu.text.split("\n")

            if teststring in options:
                options.remove(teststring)

            # menu.find_elements(By.CSS_SELECTOR, "div.VirtualizedSelectOption")
            selection[component] = options[-1]
            assert 'Create new' not in selection[component]

        if components[component] is True:
            thisdash.select_dcc_dropdown(sel_dd, index=0)
            assert sel_dd.text.startswith('Create new')
            sel_inp = sel_dd.find_element(By.XPATH, '//input[contains(@id,"' +
                                          component + '") and contains(@id,"' + module + '")]')

            sel_inp.clear()
            sel_inp.send_keys(teststring)
            sel_inp.send_keys(Keys.RETURN)

            time.sleep(0.4)

            assert sel_dd.text == clean_render_name(teststring)

            thisdash.select_dcc_dropdown(sel_dd, index=-2)

            # # close dropdown
            # minarrow = sel_dd.find_element(By.XPATH, './/span[@class="Select-arrow-zone"]')
            #
            # minarrow.click()


        if not component == 'owner':
            # there is no browse link at the owner level
            browselink = thisdash.driver.find_element(By.XPATH,'//a[contains(@id,"' + component + '")]')

            assert browselink.text == '(Browse)'

            checklink(thisdash, browselink, target.rstrip('&'))

    thisdash.select_dcc_dropdown(sel_dd, index=-2)
