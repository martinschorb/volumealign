#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
import os
import glob
import params

from app import app

from utils import launch_jobs,pages
from callbacks import runstate,render_selector,substack_sel,match_selector


from sift import sift_pointmatch


module='pointmatch'



storeinit = {}            
store = pages.init_store(storeinit, module)

store.append(dcc.Store(id={'component':'runstep','module':module},data='generate'))

for storeitem in params.match_store.keys():       
        store.append(dcc.Store(id={'component':'store_'+storeitem,'module':module}, storage_type='session',data=params.match_store[storeitem]))
    

main=html.Div(id={'component': 'main', 'module': module},children=html.H3("Generate TilePairs for Render stack"))

intervals = html.Div([dcc.Interval(id={'component': 'interval1', 'module': module}, interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Interval(id={'component': 'interval2', 'module': module}, interval=params.idle_interval,
                                       n_intervals=0)
                      ])


page = [intervals,main]



# # ===============================================
#  RENDER STACK SELECTOR

# Pre-fill render stack selection from previous module

us_out,us_in,us_state = render_selector.init_update_store(module,'tilepairs')

@app.callback(us_out,us_in,us_state,
              prevent_initial_call=True)
def mipmaps_update_store(*args): 
    return render_selector.update_store(*args)

page1 = pages.render_selector(module)


page.append(page1)


page2 = pages.match_selector(module,newcoll=True)

       
page.append(page2)       


# ===============================================
       
page3 = html.Div([html.H4("Choose type of PointMatch determination:"),
                  dcc.Dropdown(id=module+'dropdown1',persistence=True,
                               options=[{'label': 'SIFT', 'value': 'SIFT'}],
                               value='SIFT'),                          
                  html.Div([html.H4("Select Tilepair source directory:"),
                            dcc.Dropdown(id=module+'tp_dd',persistence=True,
                                         clearable=False),
                            html.Br(),
                            html.Div(id=module+'tp_prefix',style={'display':'none'})                              
                            ])
              ])


page.append(page3)  


@app.callback([Output(module+'tp_dd','options'),
                Output(module+'tp_dd','value')],
              Input({'component': 'stack_dd', 'module': module},'value'))
def pointmatch_tp_dd_fill(stack):
   
    tp_dirlist = [d_item for d_item in glob.glob(params.json_run_dir+'/tilepairs_'+params.user+'*'+stack+'*') if os.path.isdir(d_item)]
    tpdir_dd_options=list(dict())
    
    
    if tp_dirlist == []:
        tpdir_dd_options.append({'label':'no tilepairs found for selected stack', 'value': ''})
    else:
        for tp_dir in tp_dirlist:
            tpdir_dd_options.append({'label':os.path.basename(tp_dir), 'value':tp_dir})
    
    

    return tpdir_dd_options,tpdir_dd_options[-1]['value']



# =============================================
# # Page content for specific pointmatch client


page4 = html.Div(id=module+'page1')

page.append(page4)


@app.callback([Output(module+'page1', 'children')],
                Input(module+'dropdown1', 'value'))
def pointmatch_output(value):
    
    if value=='SIFT':
        return [sift_pointmatch.page]
    
    else:
        return [[html.Br(),'No method type selected.']]



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