#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""
import os
import re
import time
import requests
import json

from dash._utils import AttributeDict

from dashUI.params import base_dir, render_base_url, render_version, render_owners

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
    """
    Returns the CSS label from a pattern-matching dash ID

    :param str component: Component name
    :param str module: Module name
    :return: CSS compatible ID string
    :rtype: str
    """
    selector = css_escape('#{"component":"' + component + '","module":"' + module + '"} input')
    return selector


def make_elid(el_id):
    """
    expands a tuple describing component/module

    :param str or tuple el_id: Dash element ID. Tuple -> component/module dict
    :return: component/module dict
    :rtype: dict or str
    """
    if type(el_id) is tuple:
        assert len(el_id) == 2
        return {"component": el_id[0], "module": el_id[1]}
    elif type(el_id) is list:
        return [make_elid(el) for el in el_id]
    else:
        return el_id


def get_renderparams(rp={}):
    """
    Gets the render parameters for the first (or defined) stack found on the render server.

    :param dict rp: a stackID dictionary {'owner': str, 'project': str, 'stack': str}
    :return: a dictionary describing the stack, the renderparameters dictionary
    :rtype: (dict, dict, list)
    """

    if 'owner' in rp.keys() and rp['owner'] in render_owners:
        render_owners[0] = rp['owner']

    p_url0 = render_base_url + render_version + 'owner/' + render_owners[0]

    p_url = p_url0 + '/projects'

    projects = requests.get(p_url).json()

    if 'project' in rp.keys() and rp['project'] in projects:
        projects[0] = rp['project']

    st_url = p_url0 + '/project/' + projects[0] + '/stacks'

    stacks = requests.get(st_url).json()

    sel_stack = stacks[0]['stackId']

    if 'stack' in rp.keys() and rp['stack'] in [stack['stackId']['stack'] for stack in stacks]:
        sel_stack = rp

    tile_url = st_url.rstrip('s') + '/' + sel_stack['stack'] + '/tileIds'

    tiles = requests.get(tile_url).json()

    rp_url = tile_url.rstrip('Ids') + '/' + tiles[0] + '/render-parameters'

    renderparams = requests.get(rp_url).json()

    return sel_stack, renderparams, stacks


def set_stack(thisdash, module, stackdict):
    """
    Sets all render selector dropdowns to the desired values.

    :param dash.testing.composite.DashComposite thisdash: the dash testing instance
    :param str module: the name of the current module
    :param dict stackdict: The stackID dictionary {'owner': str, 'project': str, 'stack': str}
    """
    for component, value in stackdict.items():

        sel_dd = thisdash.driver.find_element(By.XPATH, '//div[@class="dash-dropdown" and contains(@id,"' +
                                              component + '") and contains(@id,"' + module + '")]')

        thisdash.select_dcc_dropdown(sel_dd, value=value)


def select_radioitem(element, idx=None):
    """
    Finds selected radio elements and allows to define them.
    If multi-select is disabled, the last item of a provided list will stay active.

    :param selenium.webdriver.remote.webelement.WebElement element: the radio element
    :param idx: index to select (if non-integer or not a list, only returns selected buttons)
    :return: list of selected buttons
    :rtype: list
    """
    inputs = element.find_elements(By.XPATH, './/input')
    outs = []

    if type(idx) is int:
        inputs[idx].click()
    elif type(idx) is list:
        for idx0 in idx:
            inputs[idx0].click()

    for r_idx, r_i in enumerate(inputs):
        if r_i.is_selected():
            outs.append(r_idx)

    return outs


def set_callback_context(el_id, value, valkey='value', context='triggered_inputs'):
    """
    Generates a compatible dictionary for filling context_value.

    :param str or tuple el_id: Dash element ID. Tuple -> component/module dict
    :param value: value of the element
    :param str or list valkey: dash key of the value (element-specific)
    :param str context: the context attribute for the callback
    :return: Attribute dict to be fed into context
    """

    if type(el_id) in (tuple, str):
        el_id = make_elid(el_id)
        el_ids = [el_id]
    else:
        el_ids = make_elid(list(el_id))

    if '_list' in context:
        if type(valkey) is list and type(value) is list:
            assert len(valkey) == len(value) == len(el_ids)
            outlist = [{'id': el, 'property': vkey, vkey: val}
                       for el, vkey, val in zip(el_ids, value.keys(), value.values())]
        elif type(value) is list:
            assert len(value) == len(el_ids)
            if all([type(val) == dict for val in value]):
                outlist = [{'id': el, 'property': vkey, vkey: val}
                           for el, vkey, val in zip(el_ids, value.keys(), value.values())]
            else:
                outlist = [{'id': el, 'property': valkey, valkey: val}
                           for el, val in zip(el_ids, value)]

        elif len(el_ids) == 1:
            outlist = [{'id': el_id, 'property': valkey, valkey: value}]

        else:
            raise TypeError

        return AttributeDict(**{context: outlist})

    elif context in ['inputs', 'states']:
        if type(valkey) is list and type(value) is list:
            assert len(valkey) == len(value) == len(el_ids)
            out = {json.dumps(el) + '.' + vkey: val
                   for el, vkey, val in zip(el_ids, valkey, value)}

        elif type(value) is list:
            assert len(value) == len(el_ids)
            if all([type(val) == dict for val in value]):
                out = {json.dumps(el) + '.' + vkey: val
                       for el, vkey, val in zip(el_ids, value.keys(), value.values())}
            else:
                out = {json.dumps(el) + '.' + valkey: val
                       for el, val in zip(el_ids, value)}

        elif len(el_ids) == 1:
            out = {json.dumps(el_id) + '.' + valkey: value}

        else:
            raise TypeError

        return AttributeDict(**{context: out})

    else:
        if type(value) is dict:
            valkey = list(value.keys())[0]
            value = value[valkey]

        return AttributeDict(**{context: [{'prop_id': json.dumps(el_id) + '.' + valkey, valkey: value}
                                          for el_id in el_ids]})

# ===========================
# Need to wait for dash-testing dev!
def multi_context(*inputs):
    pass
#     out = dict()
#     for indict in inputs:
#         print(type(indict))
#         indict=dict(indict)
#         print(indict)
#         print(type(indict))
#         out[list(indict.keys())[0]] = list(indict.values())[0]
#     print(out)
#     return AttributeDict(**out)


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


def check_link(thisdash, link, target, urlmatch=''):
    """
    Check if a hyperlink on a page points to the desired target and if that web page can be reached.

    :param dash.testing.composite.DashComposite thisdash: the dash testing instance
    :param selenium.webdriver.remote.webelement.WebElement link: the link element
                (HTML a, HTML img: tests as well if the source image is accessible).
    :param str target: target address to test
    :param str split: string to split the address URL to cut off parameters etc.
    """

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
            if urlmatch == '':
                wait.until(EC.url_to_be(target))
            else:
                wait.until(EC.url_matches(urlmatch))

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

    dd_area = dropdown.find_element(By.CLASS_NAME, 'Select-placeholder')
    dd_area.click()

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


def check_renderselect(thisdash, module, components={'owner': False, 'project': False, 'stack': False}):
    """
    Checks a render selector page element

    :param dash.testing.composite.DashComposite thisdash: the dash testing instance
    :param str module: The module label.
    :param dict components: The Selector components to be checked.
            - String values -> no check but set the value
            - False -> check the selector
            - True -> check selector and creation input for new entries
    :rtype: None
    """

    if type(components) is not dict:
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

            assert len(options) > 0

            # menu.find_elements(By.CSS_SELECTOR, "div.VirtualizedSelectOption")
            if 'Create new' in options[0]:
                selection[component] = options[-1]
            else:
                selection[component] = options[0]

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

        if not component == 'owner':
            # there is no browse link at the owner level
            browselink = thisdash.driver.find_element(
                By.XPATH, '//a[contains(@id,"' + component + '") and contains(@id,"' + module + '")]')

            assert browselink.text == '(Browse)'

            check_link(thisdash, browselink, target.strip('&'))

    thisdash.select_dcc_dropdown(sel_dd, index=-1)


def check_matchselect(thisdash, module, stackdict, components={'mc_owner': False, 'matchcoll': False}):
    """
    Checks a render match selector page element

    :param dash.testing.composite.DashComposite thisdash: the dash testing instance
    :param str module: The module label.
    :param dict stackdict: The stackID dictionary {'owner': str, 'project': str, 'stack': str}
    :param dict components: The Selector components to be checked.
            - String values -> no check but set the value
            - False -> check the selector
            - True -> check selector and creation input for new entries
    :rtype: None
    """

    if type(components) is not dict:
        raise TypeError('components need to be dict')

    selection = {}

    for component in components.keys():

        sel_dd = thisdash.driver.find_element(By.XPATH, '//div[@class="dash-dropdown" and contains(@id,"' +
                                              component + '") and contains(@id,"' + module + '")]')

        if type(components[component]) is str:
            selection[component] = components[component]
        else:
            sel_dd.click()
            menu = sel_dd.find_element(By.CSS_SELECTOR, "div.Select-menu-outer")
            options = menu.text.split("\n")

            if teststring in options:
                options.remove(teststring)

            assert len(options) > 0

            # menu.find_elements(By.CSS_SELECTOR, "div.VirtualizedSelectOption")
            if 'new Match' in options[0]:
                selection[component] = options[-1]
            else:
                selection[component] = options[0]

            assert 'new Match' not in selection[component]

        if components[component] is True:
            thisdash.select_dcc_dropdown(sel_dd, index=0)
            assert sel_dd.text.startswith('new Match')
            sel_inp = sel_dd.find_element(By.XPATH, '//input[contains(@id,"' +
                                          component + '") and contains(@id,"' + module + '")]')

            sel_inp.clear()
            sel_inp.send_keys(teststring)
            sel_inp.send_keys(Keys.RETURN)

            time.sleep(0.4)

            assert sel_dd.text == clean_render_name(teststring)

            thisdash.select_dcc_dropdown(sel_dd, index=-2)
            thisdash.select_dcc_dropdown(sel_dd, index=-2)

        if not component == 'mc_owner':
            # there is no browse link at the MC owner level
            urlmatch = ''
            target = render_base_url + 'view/point-match-explorer.html?'
            urlmatch += '[view/point.match.explorer.html]*'

            target += 'matchCollection=' + selection['matchcoll']
            urlmatch += '[matchCollection=' + selection['matchcoll'] +']*'

            target += '&matchOwner=' + selection['mc_owner'] + '&'
            urlmatch += '[matchOwner=' + selection['mc_owner'] + ']*'

            target += '&renderStack=' + stackdict['stack']
            urlmatch += '[renderStack=' + stackdict['stack'] + ']*'

            target += '&renderStackOwner=' + stackdict['owner']
            urlmatch += '[renderStackOwner=' + stackdict['owner'] + ']*'

            target += '&renderStackProject=' + stackdict['project']
            urlmatch += '[renderStackProject=' + stackdict['project'] + ']*'

            target += '&startZ=0'
            target += '&endZ=100'

            browselink = thisdash.driver.find_element(
                By.XPATH, '//a[contains(@id,"browse_mc") and contains(@id,"' + module + '")]')

            assert browselink.text == 'Explore Match Collection'

            check_link(thisdash, browselink, target, urlmatch=urlmatch)

    thisdash.select_dcc_dropdown(sel_dd, index=-1)


def check_inputvalues(element, vals):
    """
    Checks the validity of values in a text input (type, range, etc.). Assume initial value is valid.

    :param selenium.webdriver.remote.webelement.WebElement element: the input element
    :param dict vals: Expected behaviour in the format: {value: valid(bool)}
    """

    orig_val = element.get_attribute('value')
    validstyle = element.value_of_css_property('outline')
    assert type(vals) is dict

    for testval, valid in vals.items():
        element.clear()
        element.send_keys(testval)
        assert (element.value_of_css_property('outline') == validstyle) is valid

    element.clear()
    element.send_keys(orig_val)


def check_substackselect(thisdash, module, switch=None):

    subst_div = thisdash.driver.find_element(By.XPATH, '//div[contains(@id,"3Dslices")'
                                                       ' and contains(@id,"' + module + '")]')

    rangesel = subst_div.find_element(By.XPATH, './input')

    assert rangesel.get_attribute('value') == '1'

    testvalues = {'2': True, '0': False, 'abc': False}
    check_inputvalues(rangesel, testvalues)

    stackparams = get_renderparams()[-1][0]

    set_stack(thisdash, module, stackparams['stackId'])

    minz = stackparams['stats']['stackBounds']['minZ']
    maxz = stackparams['stats']['stackBounds']['maxZ']

    subsel_div = thisdash.driver.find_element(By.XPATH, '//div[contains(@id,"3Dselection")'
                                                        ' and contains(@id,"' + module + '")]')

    selection = subsel_div.find_element(By.XPATH, './/details')
    selection.click()

    slicesels = selection.find_elements(By.XPATH, './/input')

    # check min input
    testvalues = {str(int((maxz-minz)/2)): True,
                  str(minz): True,
                  str(maxz): True,
                  str(minz-1): False,
                  str(maxz+1): False,
                  'abc': False}

    check_inputvalues(slicesels[0], testvalues)

    # check max input

    check_inputvalues(slicesels[1], testvalues)

def check_tiles(thisdash, module):


    pass