#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 15:42:18 2021

@author: schorb
"""
import os

import dash

from app import app

from dash.exceptions import PreventUpdate

from dash.dependencies import Input, Output, State, MATCH, ALL
from utils import helper_functions as hf

startpath = os.getcwd()
# show_files = False
show_hidden = False


@app.callback([Output({'component': 'path_input', 'module': MATCH}, 'value'),
               Output({'component': 'path_dummy', 'module': MATCH}, 'data')],
              [Input({'component': 'path_store', 'module': MATCH}, 'data'),
               Input({'component': 'path_ext', 'module': MATCH}, 'data')],
              State({'component': 'newdir_sel', 'module': MATCH}, 'value'),
              prevent_initial_call=True)
def update_store(inpath, extpath, createdir_val):
    trigger = hf.trigger()
    createdir = createdir_val == ['Create new directory']

    # print('pathstore -- ')
    # print(trigger)
    outtrigger = dash.no_update
    if trigger == 'path_store':
        if os.path.exists(str(inpath)) or createdir:
            path = inpath
        else:
            path = startpath
    else:
        # print(extpath)
        path = extpath
        outtrigger = extpath

    return path, outtrigger


@app.callback([Output({'component': 'browse_dd', 'module': MATCH}, 'options'),
               Output({'component': 'path_store', 'module': MATCH}, 'data'),
               Output({'component': 'browse_dd', 'module': MATCH}, 'value')],
              [Input({'component': 'browse_dd', 'module': MATCH}, 'value'),
               Input({'component': 'path_input', 'module': MATCH}, 'n_blur'),
               Input({'component': 'path_dummy', 'module': MATCH}, 'modified_timestamp')],
              [State({'component': 'path_input', 'module': MATCH}, 'value'),
               State({'component': 'path_store', 'module': MATCH}, 'data'),
               State({'component': 'path_showfiles', 'module': MATCH}, 'data'),
               State({'component': 'path_filetypes', 'module': MATCH}, 'data'),
               State({'component': 'path_dummy', 'module': MATCH}, 'data'),
               State({'component': 'newdir_sel', 'module': MATCH}, 'value'),
               State('url', 'pathname')],
              prevent_initial_call=True)
def update_path_dd(filesel, intrig, trig2, inpath, path, show_files, filetypes, dummydata, createdir_val, thispage):
    if dash.callback_context.triggered:
        trigger = hf.trigger()
    else:
        trigger = '-'

    thispage = thispage.lstrip('/')
    createdir = createdir_val == ['Create new directory']

    if thispage == '' or thispage not in hf.trigger(key='module') or inpath is None:
        raise PreventUpdate

    if 'dummy' in trigger:
        path = dummydata

    path = inpath

    if os.path.isdir(str(inpath)):
        inpath = inpath
    elif os.path.exists(str(inpath)):
        inpath = os.path.dirname(inpath)
    else:
        if not createdir:
            path = startpath

    if not os.path.isdir(str(path)):
        if os.path.isdir(str(inpath)) or createdir:
            path = inpath
        else:
            path = startpath

    if trigger == 'path_input':
        if os.path.isdir(str(inpath)):
            path = inpath
            filesel = None

    outselect = dash.no_update

    if filesel == '..':
        outselect = ''

    if type(filetypes) is str:
        filetypes = [filetypes]

    if not filetypes == []:
        show_files = True

    for idx, filetype in enumerate(filetypes):
        filetypes[idx] = filetype.lower()
        if not filetype.startswith(os.path.extsep):
            filetypes[idx] = os.path.extsep + filetypes[idx]

    if filesel is None or filesel[0:2] == '> ' or filesel == '..':

        if filesel is not None:
            if filesel[0:2] == '> ':
                if os.path.exists(os.path.join(path, filesel[2:])):
                    path = os.path.join(path, filesel[2:])
            elif filesel == '..':
                path = os.path.abspath(os.path.join(path, filesel))

        if not os.path.isdir(str(path)):
            files = []
        else:
            files = os.listdir(path)

        dd_options = list(dict())

        dd_options.append({'label': '..', 'value': '..'})

        f_list = list(dict())

        files.sort()

        for item in files:
            # print(item)
            # print(os.path.isdir(os.path.join(path,item)))
            if os.path.isdir(os.path.join(path, item)):
                if item.startswith('.') and show_hidden or not item.startswith('.'):
                    dd_options.append({'label': '\u21AA ' + item, 'value': '> ' + item})
            else:
                if item.startswith('.') and show_hidden or not item.startswith('.'):

                    if not (len(filetypes) > 0 and os.path.splitext(item)[1].lower() not in filetypes):
                        f_list.append({'label': item, 'value': item})

        if show_files:
            dd_options.extend(f_list)

        return dd_options, path, outselect

    else:
        path = os.path.join(path, filesel)

        return dash.no_update, path, outselect
