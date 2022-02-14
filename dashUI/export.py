#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
from dash import dcc
from dash import html
from dash.dependencies import Input,Output,State
from dash.exceptions import PreventUpdate

import params

from app import app

from utils import pages
from utils import helper_functions as hf

from callbacks import runstate,render_selector,boundingbox,match_selector,tile_view


from filetypes import N5_export


module='export'



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
                               value='N5')
                  ])                                

page.append(page2)


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