#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input,Output,State
from dash.exceptions import PreventUpdate

import os
import requests

import params

from app import app

from utils import pages
from utils import helper_functions as hf

from callbacks import (render_selector,
                       boundingbox,tile_view,
                       substack_sel,filebrowse)


from filetypes import N5_export


module='export'

subpages = [{'label': 'BigDataViewer (BDV) XML', 'value': 'BDV'},
            {'label': 'Add to MoBIE project', 'value': 'MoBIE'}]

submodules = [
    'filetypes.MoBIE_finalize',
    'filetypes.BDV_finalize'
]


storeinit = {}            
store = pages.init_store(storeinit, module)


main=html.Div(id={'component': 'main', 'module': module},children=html.H3("Export Render stack to volume"))


page = [main]



# # ===============================================
#  RENDER STACK SELECTOR

# Pre-fill render stack selection from previous module

us_out,us_in,us_state = render_selector.init_update_store(module,'solve')

@app.callback(us_out,us_in,us_state,
              prevent_initial_call=True)
def export_update_store(*args):
    thispage = args[-1]
    args = args[:-1]
    thispage = thispage.lstrip('/')

    if thispage == '' or not thispage in hf.trigger(key='module'):
        raise PreventUpdate

    return render_selector.update_store(*args)

page1 = pages.render_selector(module)


page.append(page1)


# ===============================================

slice_view = pages.section_view(module,bbox=True)

page.append(slice_view)


# ==============================

page.append(pages.boundingbox(module))



# ===============================================
       
page2 = html.Div([html.H4("Choose output type."),
                  dcc.Dropdown(id=module+'dropdown1',persistence=True,
                               options=[{'label': 'N5', 'value': 'N5'}],
                               value='N5'),
                  html.Br()
                  ])                                

page.append(page2)

page3 = html.Div(id={'component': 'page2', 'module': module}, children=[html.H4('Output path'),
                                                                       dcc.Input(id={'component': "path_input",
                                                                                     'module': module}, type="text",
                                                                                 debounce=True, persistence=True,
                                                                                 className='dir_textinput'),
                                                                       # dcc.Input(id={'component': "path_input", 'module': label}, type="text",style={'display': 'none'})
                                                                       # html.Button('Browse',id={'component': "browse1", 'module': label}),
                                                                       # 'graphical browsing works on cluster login node ONLY!',
                                                                       # html.Br()
                                                                       ])

page.append(page3)

pathbrowse = pages.path_browse(module)

page.append(pathbrowse)

# callback for output

@app.callback(Output({'component': 'path_ext', 'module': module},'data'),
              [Input({'component': "path_input", 'module': module},'n_blur'),
               Input({'component': "path_input", 'module': module},'n_submit'),
               Input({'component': 'stack_dd', 'module': module}, 'value')],
              [State({'component': 'store_owner', 'module': module}, 'data'),
               State({'component': 'store_project', 'module': module}, 'data'),
               State({'component': 'store_allstacks', 'module': module}, 'data'),
               State({'component': "path_input", 'module': module},'value')
               ]
               )
def export_stacktodir(dir_trigger,trig2,stack_sel,owner,project,allstacks,browsedir):
    dir_out = browsedir
    trigger = hf.trigger()

    if (not stack_sel == '-') and (not allstacks is None):
        stacklist = [stack for stack in allstacks if stack['stackId']['stack'] == stack_sel]
        stack = stack_sel

        if not trigger == 'path_input':
            if not stacklist == []:
                stackparams = stacklist[0]

                if 'None' in (stackparams['stackId']['owner'], stackparams['stackId']['project']):
                    return dash.no_update

                url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project + '/stack/' + stack + '/z/' + str(int(
                    (stacklist[0]['stats']['stackBounds']['maxZ']-stacklist[0]['stats']['stackBounds']['minZ'])/2)) + '/render-parameters'

                tiles0 = requests.get(url).json()

                tilefile0 = os.path.abspath(tiles0['tileSpecs'][0]['mipmapLevels']['0']['imageUrl'].strip('file:'))

                dir_out = os.path.join(os.sep,*tilefile0.split(os.sep)[:-params.datadirdepth[owner]-1])

    return dir_out

# =============================================
# # Page content for specific export call


page3 = html.Div(id=module+'page1')

page.append(page3)


@app.callback([Output(module+'page1', 'children')],
                Input(module+'dropdown1', 'value'))
def export_output(value):
    
    if value=='N5':
        return [N5_export.page]
    
    else:
        return [[html.Br(),'No output type selected.']]



# =============================================
# Processing status

# initialized with store
# embedded from callbacks import runstate

# # =============================================
# # PROGRESS OUTPUT


collapse_stdout = pages.log_output(module)

# ----------------

# Full page layout:
    

page.append(collapse_stdout)