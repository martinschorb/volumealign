#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""
import os
import re
from dashUI.params import base_dir

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def css_escape(s):
    '''
    creates CSS compatible IDs for dash pattern-matching dictionary IDs

    :param str s: input string
    :return: CSS compatible ID string
    :rtype: str
    '''
    sel = re.sub("[\\{\\}\\\"\\'.:,]", lambda m: "\\" + m.group(0), s)
    return sel


def module_selector(component, module):
    selector = css_escape('#{"component":"' + component + '","module":"' + module + '"} input')
    return selector


def check_subpages(subpage_ids, input_dd, module, dashtest_el, sub_elements=None):
    '''
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
    '''

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
                    assert subpagedivs[checkidx].get_attribute('id') == '{"component":"page1","module":"' + inp_sel + '"}'
                    assert subpagedivs[checkidx].get_attribute('style') != 'display: none;'

                if 'console-out' in sub_elements:
                    assert logtextboxes[checkidx-1].get_attribute('id') ==\
                           '{"component":"console-out","module":"' + module + '_' + inp_sel + '"}'

            else:
                assert subpagedivs[checkidx].get_attribute('style') == 'display: none;'

        if 'compute_sel' in sub_elements:
            compute_loc = dashtest_el.find_element(module_selector('compute_sel',module + '_' + inp_sel))
            assert compute_loc.get_attribute('type') == 'radio'

def check_browsedir(thisdash, module):
    pathinputs = thisdash.driver.find_elements(By.XPATH, '//input[@class="dir_textinput"]')

    for p_input in pathinputs:
        if module in p_input.get_attribute('id'):
            break

    p_input.send_keys(Keys.META, 'A', Keys.BACKSPACE)
    p_input.send_keys(Keys.CONTROL, 'A', Keys.BACKSPACE)

    p_input.send_keys(base_dir,'test')

    dropdowns = thisdash.driver.find_elements(By.XPATH, '//div[@class="dash-dropdown"]')

    for dropdown in dropdowns:
        if module in dropdown.get_attribute('id') and 'browse_dd' in dropdown.get_attribute('id'):
            break

    sums = thisdash.driver.find_elements(By.XPATH,'//summary')

    for summary in sums:
        if 'Browse' == summary.text:
            break

    dropdown.click()

