#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 14:52:17 2021

@author: schorb
"""

import dash

from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

import requests

from dash import callback

from dashUI import params
from dashUI.utils import checks
from dashUI.utils import helper_functions as hf

new_project_style = {'margin-left': '2em'}
new_stack_style = {'margin-left': '11em'}
fullitem_style = {'display': 'inline-block'}


# Update init parameters from previous module


def init_update_store(thismodule, prevmodule, comp_in='store_render_launch', comp_out='store_init_render'):
    dash_out = Output({'component': comp_out, 'module': thismodule}, 'data')
    dash_in = Input({'component': comp_in, 'module': prevmodule}, 'data')
    dash_state = [State({'component': 'store_init_render', 'module': thismodule}, 'data'),
                  State('url', 'pathname')]

    return dash_out, dash_in, dash_state


def update_store(prevstore, thisstore):
    if not dash.callback_context.triggered:
        raise PreventUpdate
    if None in (prevstore, thisstore):
        raise PreventUpdate
    # print(thisstore,prevstore)

    thisstore.update(prevstore)

    return thisstore


def subpage_launch(module, subpages):
    # subpages can be list of strings or list of dicts (dcc.Dropdown)

    if subpages == []:
        return [], []

    if type(subpages) is not list:
        raise TypeError('subpages need to be list')

    c_in = list()
    c_out = Output({'component': 'store_render_launch', 'module': module}, 'data')
    sbstrings = list()

    if type(subpages[0]) is dict:
        for item in subpages:
            sbstrings.append(item['value'])
    elif type(subpages[0]) is str:
        sbstrings = subpages

    for subpage in sbstrings:
        sublabel = module + '_' + subpage
        c_in.append(Input({'component': 'store_render_launch', 'module': sublabel}, 'data'))

    return c_in, c_out


# Update owner dropdown:


@callback([Output({'component': 'owner_dd', 'module': MATCH}, 'options'),
           Output({'component': 'owner_dd', 'module': MATCH}, 'value')
           ],
          [Input({'component': 'store_init_render', 'module': MATCH}, 'data'),
           Input('url', 'pathname')],
          State({'component': 'owner_dd', 'module': MATCH}, 'options')
          )
def update_owner_dd(init_in, thispage, dd_options_in):

    thispage = thispage.lstrip('/')

    if thispage in (None, '') or thispage not in hf.trigger(key='module') and dd_options_in is not None:
        raise PreventUpdate

    dd_options = list(dict())

    allowners = params.render_owners

    for item in allowners:
        dd_options.append({'label': item, 'value': item})

    init_owner = init_in['owner']

    if init_owner == '':
        init_owner = allowners[0]

    return dd_options, init_owner


#  SELECT STACK TO WORK....
# ============================================================

# Update projects dropdown and browse link

@callback([Output({'component': 'browse_project', 'module': MATCH}, 'href'),
           Output({'component': 'project_dd', 'module': MATCH}, 'options'),
           Output({'component': 'project_dd', 'module': MATCH}, 'value'),
           Output({'component': 'project_store', 'module': MATCH}, 'data')
           ],
          [Input({'component': 'owner_dd', 'module': MATCH}, 'value'),
           Input({'component': 'store_init_render', 'module': MATCH}, 'data'),
           Input({'component': 'project_input', 'module': MATCH}, 'value'),
           Input('url', 'pathname')],
          [State({'component': 'store_project', 'module': MATCH}, 'data'),
           State({'component': 'project_dd', 'module': MATCH}, 'options'),
           State({'component': 'new_project_div', 'module': MATCH}, 'style')
           ],
          prevent_initial_call=True)
def update_proj_dd(owner_sel, init_store, newproj_in, thispage, store_proj, dd_options_in, newp_visible):
    if not dash.callback_context.triggered:
        raise PreventUpdate

    if thispage in (None, ''):
        raise PreventUpdate

    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    trigger = hf.trigger()

    if thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    if owner_sel == '' or owner_sel is None:
        raise PreventUpdate

    out_project = ''

    href_out = params.render_base_url + 'view/stacks.html?renderStackOwner=' + owner_sel

    # get list of projects on render server
    url = params.render_base_url + params.render_version + 'owner/' + owner_sel + '/projects'

    projects = requests.get(url).json()

    store = {}
    store['allprojects'] = projects

    if 'store_init_render' in trigger or init_store['owner'] == owner_sel:
        if 'project' in init_store.keys() and init_store['project'] not in (None, ''):
            out_project = init_store['project']

    # assemble dropdown
    dd_options = list(dict())

    if not newp_visible == {'display': 'none'}:
        dd_options.append({'label': 'Create new Project', 'value': 'newproj'})
        out_project = 'newproj'

    for item in projects:
        if item == store_proj:
            out_project = item
        dd_options.append({'label': item, 'value': item})

    if trigger == 'project_input':
        newproj_in = checks.clean_render_name(newproj_in)
        dd_options.append({'label': newproj_in, 'value': newproj_in})
        out_project = newproj_in
        store = dash.no_update

    if out_project == '':
        out_project = projects[0]

    return href_out, dd_options, out_project, store


# Update stack dropdown and browse link


@callback([Output({'component': 'browse_stack', 'module': MATCH}, 'href'),
           Output({'component': 'stack_dd', 'module': MATCH}, 'options'),
           Output({'component': 'stack_dd', 'module': MATCH}, 'value'),
           Output({'component': 'store_allstacks', 'module': MATCH}, 'data'),
           Output({'component': 'full_stack_div', 'module': MATCH}, 'style'),
           Output({'component': 'render_project', 'module': MATCH}, 'style')],
          [Input({'component': 'store_init_render', 'module': MATCH}, 'data'),
           Input({'component': 'owner_dd', 'module': MATCH}, 'value'),
           Input({'component': 'project_dd', 'module': MATCH}, 'value'),
           Input({'component': 'stack_input', 'module': MATCH}, 'value')],
          [State({'component': 'store_stack', 'module': MATCH}, 'data'),
           State({'component': 'stack_dd', 'module': MATCH}, 'options'),
           State({'component': 'project_store', 'module': MATCH}, 'data'),
           State({'component': 'new_stack_div', 'module': MATCH}, 'style'),
           State('url', 'pathname')],
          prevent_initial_callback=True
          )
def update_stack_dd(init_store, own_sel, proj_sel, newstack_in, store_stack, dd_options_in, proj_store, news_visible,
                    thispage):
    if not dash.callback_context.triggered:
        raise PreventUpdate

    stackdiv_style = fullitem_style

    if thispage in (None, ''):
        raise PreventUpdate

    thispage = thispage.lstrip('/')

    trigger = hf.trigger()

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    if proj_sel is None or proj_sel == '':
        return [dash.no_update] * 6

    elif proj_sel == 'newproj':
        out = [dash.no_update] * 2
        if dd_options_in in (None, '', []):
            out.append('newstack')
        else:
            out.append(dd_options_in[0]['value'])
        out.append(dash.no_update)
        out.append(dict(display='none'))
        out.append(new_project_style)

        return out

    elif trigger != 'stack_input' and proj_sel not in proj_store['allprojects']:
        dd_options = [{'label': 'Create new Stack', 'value': 'newstack'},
                      {'label': 'Create new Stack', 'value': 'newstack'}]
        return dash.no_update, dd_options, 'newstack', dash.no_update, stackdiv_style, {'display': 'none'}

    else:

        href_out = params.render_base_url + 'view/stacks.html?renderStackOwner=' + own_sel \
                   + '&renderStackProject=' + proj_sel
        # get list of projects on render server
        url = params.render_base_url + params.render_version + 'owner/' + own_sel + '/project/' + proj_sel + '/stacks'

        stacks = requests.get(url).json()
        out_stack = ''

        # assemble dropdown
        dd_options = list(dict())

        if not news_visible == {'display': 'none'}:
            dd_options.append({'label': 'Create new Stack', 'value': 'newstack'})
            out_project = 'newstack'

        for item in stacks:
            if 'stack' in init_store.keys():
                if item['stackId']['stack'] == init_store['stack']:
                    out_stack = item['stackId']['stack']

            dd_options.append({'label': item['stackId']['stack'], 'value': item['stackId']['stack']})

        if 'store_init_render' in trigger:
            if 'stack' in init_store.keys() and init_store['stack'] not in (None, ''):
                out_stack = init_store['stack']

        if trigger == 'stack_input':
            newstack_in = checks.clean_render_name(newstack_in)
            dd_options.append({'label': newstack_in, 'value': newstack_in})
            out_stack = newstack_in

        if out_stack == '':
            out_stack = stacks[0]['stackId']['stack']

        return href_out, dd_options, out_stack, stacks, stackdiv_style, {'display': 'none'}


@callback(Output({'component': 'render_stack', 'module': MATCH}, 'style'),
          Input({'component': 'stack_dd', 'module': MATCH}, 'value'))
def sbem_conv_update_stack_browse(stack_state):
    if stack_state == 'newstack':
        return new_stack_style
    else:
        return {'display': 'none'}


# Update render store fields:


@callback([Output({'component': 'store_owner', 'module': MATCH}, 'data'),
           Output({'component': 'store_project', 'module': MATCH}, 'data'),
           ],
          Input({'component': 'project_dd', 'module': MATCH}, 'value'),
          State({'component': 'owner_dd', 'module': MATCH}, 'value'),
          prevent_initial_callback=True)
def update_render_store(proj_sel, own_sel):
    if not dash.callback_context.triggered:
        raise PreventUpdate

    return own_sel, proj_sel  # ,stack_sel
