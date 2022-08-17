#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""

import dash
from dash.exceptions import PreventUpdate

from dashUI.utils import helper_functions as hf


def convert_output(dd_value, thispage):
    """
    Populates the page with subpages.

    :param str dd_value: value of the "import_type_dd" dropdown.
    :param str thispage: current page URL
    :return: List of style dictionaries to determine which subpage content to display.<Br>
             Additionally: the page's "store_render_init" store (setting owner).
    :rtype: (list of dict, dict)
    """

    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    outputs = dash.callback_context.outputs_list
    outstyles = [{'display': 'none'}] * (len(outputs) - 1)

    modules = [m['id']['module'] for m in outputs[1:]]

    for ix, mod in enumerate(modules):

        if mod == dd_value:
            outstyles[ix + 1] = {'display': 'block'}

    if dd_value not in modules:
        outstyles[0] = {}

    # if dd_value in (None,''):
    #     dd_value = 'SBEM'
    outstore = dict()
    outstore['owner'] = dd_value

    out = outstyles
    out.append(outstore)

    return out