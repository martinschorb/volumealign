#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 14:52:17 2021

@author: schorb
"""

import dash
from dash import callback
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

import requests


from dashUI import params
from dashUI.utils import checks
from dashUI.utils import helper_functions as hf


# Update mc_owner dropdown:

@callback([Output({'component': 'mc_owner_dd', 'module': MATCH}, 'options'),
           Output({'component': 'mc_owner_dd', 'module': MATCH}, 'value')
           ],
          [Input({'component': 'store_init_render', 'module': MATCH}, 'data'),
           Input({'component': 'mc_owner_input', 'module': MATCH}, 'value'),
           Input('url', 'pathname')],
          State({'component': 'mc_owner_dd', 'module': MATCH}, 'options')
          )
def update_mc_owner_dd(init_in, new_owner, thispage, dd_own_in):
    if not dash.callback_context.triggered:
        trigger = 'init'
    else:
        trigger = hf.trigger()

    if thispage in (None, ''):
        raise PreventUpdate

    thispage = thispage.lstrip('/')

    if thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    dd_options = list()
    if 'init' in trigger or 'url' in trigger:
        if len(dd_own_in) > 0:
            if dd_own_in[0]['value'] == 'new_mc_owner':
                dd_options.extend(dd_own_in)

        if 'all_mc_owners' in init_in.keys():
            dd_options.append(init_in['all_mc_owners'])

        else:

            url = params.render_base_url + params.render_version + 'matchCollectionOwners'

            mc_owners = requests.get(url).json()

            for item in mc_owners:
                dd_options.append({'label': item, 'value': item})

        if 'mc_owner' in init_in.keys():
            mc_owner = init_in['mc_owner']
        else:
            mc_owner = dd_options[0]['value']

    elif 'input' in trigger:
        dd_options = dd_own_in.copy()
        new_owner = checks.clean_render_name(new_owner)
        dd_options.append({'label': new_owner, 'value': new_owner})
        mc_owner = new_owner
    else:
        raise PreventUpdate

    return dd_options, mc_owner


# Update match collection dropdown 
@callback([Output({'component': 'new_mc_owner', 'module': MATCH}, 'style'),
           Output({'component': 'matchcoll_dd', 'module': MATCH}, 'options'),
           Output({'component': 'matchcoll_dd', 'module': MATCH}, 'value'),
           Output({'component': 'matchcoll', 'module': MATCH}, 'style'),
           Output({'component': 'store_all_matchcolls', 'module': MATCH}, 'data')],
          [Input({'component': 'mc_owner_dd', 'module': MATCH}, 'value'),
           Input({'component': 'matchcoll_input', 'module': MATCH}, 'value')],
          [State({'component': 'matchcoll_dd', 'module': MATCH}, 'options'),
           State({'component': 'store_init_render', 'module': MATCH}, 'data'),
           State('url', 'pathname'),
           State({'component': 'mc_new_enabled', 'module': MATCH}, 'data')],
          prevent_initial_call=True)
def mcown_dd_sel(mc_own_sel, new_mc, mc_dd_opt, init_match, thispage, new_enabled='False'):
    all_mcs = dash.no_update

    thispage = thispage.lstrip('/')

    trigger = hf.trigger()

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    if None in [mc_own_sel, mc_dd_opt, init_match]:
        raise PreventUpdate


    if 'mc_owner_dd' in trigger:

        if mc_own_sel == '':
            raise PreventUpdate

        if mc_own_sel == 'new_mc_owner' and new_enabled == 'True':

            div1style = {}

            mc_dd_opt = [{'label': 'new Match Collection', 'value': 'new_mc'}]
            mc_dd_val = 'new_mc'

            mc_style = {'display': 'none'}

        else:
            div1style = {'display': 'none'}

            url = params.render_base_url + params.render_version + 'owner/' + mc_own_sel + '/matchCollections'
            mcolls = requests.get(url).json()

            all_mcs = list()

            # assemble dropdown
            if new_enabled == 'True':
                mc_dd_opt = [{'label': 'new Match Collection', 'value': 'new_mcoll'}]
                mc_dd_val = 'new_mcoll'
            else:
                mc_dd_opt = []
                mc_dd_val = ''

            init_mc = None

            if 'matchcoll' in init_match.keys():
                init_mc = init_match['matchcoll']

            for item in mcolls:
                all_mcs.append(item['collectionId']['name'])
                mc_dd_opt.append({'label': item['collectionId']['name'], 'value': item['collectionId']['name']})
                if init_mc == item['collectionId']['name']:
                    mc_dd_val = init_mc

            mc_style = {'display': 'flex'}

    elif 'matchcoll_input' in trigger:
        div1style = {'display': 'none'}
        new_mc = checks.clean_render_name(new_mc)
        mc_dd_opt.append({'label': new_mc, 'value': new_mc})
        mc_dd_val = new_mc
        mc_style = {'display': 'flex'}
    else:
        raise PreventUpdate

    return div1style, mc_dd_opt, mc_dd_val, mc_style, all_mcs


# initiate new mc input
@callback([Output({'component': 'new_matchcoll', 'module': MATCH}, 'style'),
           Output({'component': 'browse_mc_div', 'module': MATCH}, 'style'),
           Output({'component': 'browse_mc', 'module': MATCH}, 'href')],
          [Input({'component': 'matchcoll_dd', 'module': MATCH}, 'value'),
           Input({'component': 'stack_dd', 'module': MATCH}, 'value')],
          [State({'component': 'mc_owner_dd', 'module': MATCH}, 'value'),
           State({'component': 'owner_dd', 'module': MATCH}, 'value'),
           State({'component': 'project_dd', 'module': MATCH}, 'value'),
           State({'component': 'store_all_matchcolls', 'module': MATCH}, 'data')],
          prevent_initial_call=True)
def new_matchcoll(mc_sel, stack, mc_owner, owner, project, all_mcs):

    if not dash.callback_context.triggered:
        raise PreventUpdate

    if None in [mc_sel, stack, mc_owner, owner, project, all_mcs]:
        raise PreventUpdate

    if stack is None:
        stack = ''

    if mc_sel == 'new_mcoll':
        return {'display': 'flex'}, {'display': 'none'}, ''
    elif mc_sel in [None, 'new_mc']:
        return {'display': 'none'}, {'display': 'none'}, ''
    else:
        if mc_sel in all_mcs:

            mc_url = params.render_base_url + 'view/point-match-explorer.html?'
            mc_url += 'matchCollection=' + mc_sel
            mc_url += '&matchOwner=' + mc_owner
            mc_url += '&renderStack=' + stack
            mc_url += '&renderStackOwner=' + owner
            mc_url += '&renderStackProject=' + project
            mc_url += '&startZ=0'
            mc_url += '&endZ=100'

            return {'display': 'none'}, {}, mc_url
        else:
            return {'display': 'none'}, {'display': 'none'}, ''
