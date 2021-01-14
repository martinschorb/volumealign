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
import params
import subprocess

from app import app

# from sbem import sbem_conv
from utils import launch_jobs, pages

from callbacks import runstate

module='convert_'

storeinit={}            

store = pages.init_store(storeinit, module)



main = html.Div(children=[html.H3("Import volume EM datasets - Choose type:",id='conv_head'),dcc.Dropdown(
        id=module+'dropdown1',persistence=True,
        options=[
            {'label': 'SBEMImage', 'value': 'SBEMImage'}            
        ],
        value='SBEMImage'
        )    
    ])


intervals = html.Div([dcc.Interval(id=module+'interval1', interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Interval(id=module+'interval2', interval=params.idle_interval,
                                       n_intervals=0),
                      dcc.Store(id=module+'tmpstore'),
                      dcc.Store(id=module+'stack')
                      ])

junk = html.Div(id=module+'junk')

page1 = html.Div(id=module+'page1')


# =============================================
# # Page content

@app.callback([Output(module+'page1', 'children'),
               Output(module+'store_owner','data')],
                Input(module+'dropdown1', 'value'))
def convert_output(dd_value):
    # if dd_value=='SBEMImage':
    #     thisstore='SBEM'
    #     return sbem_conv.page, thisstore
    
    # else:
        return [html.Br(),'No data type selected.'],None



# =============================================
# Processing status

cus_out,cus_in,cus_state = runstate.init_update_status(module)

@app.callback(cus_out,cus_in,cus_state)
def convert_update_status(*args): 
    print(*args)
    return runstate.update_status(*args)



cgs_out,cgs_in,cgs_state = runstate.init_get_status(module)

@app.callback(cgs_out,cgs_in,cgs_state)
def convert_get_status(*args):
    return runstate.get_status(*args)


# # =============================================
# # PROGRESS OUTPUT

collapse_stdout = html.Div(children=[
                html.Br(),
                html.Div(id=module+'job-status',children=['Status of current processing run: ',
                                                          html.Div(id=module+'get-status',style={"font-family":"Courier New"},children=[
                                                              'not running',
                                                              html.Button('cancel cluster job(s)',id=module+"cancel",style={'display': 'none'})
                                                              ])
                                                          ]),
                html.Br(),
                html.Details([
                    html.Summary('Console output:'),
                    html.Div(id=module+"collapse",                 
                      children=[                         
                          html.Div(id=module+'div-out',children=['Log file: ',html.Div(id=module+'outfile',style={"font-family":"Courier New"})]),
                          dcc.Textarea(id=module+'console-out',className="console_out",
                                      style={'width': '100%','height':200,"color":"#000"},disabled='True')                         
                          ])
                ])
            ],id=module+'consolebox')


# @app.callback(Output(module+'console-out','value'),
#     [Input(module+'interval1', 'n_intervals'),Input(module+'outfile','children')])
# def convert_update_output(n,outfile):    
#     data=''
    
#     if outfile is not None:
#         if os.path.exists(outfile):
#             file = open(outfile, 'r')    
#             lines = file.readlines()
#             if lines.__len__()<=params.disp_lines:
#                 last_lines=lines
#             else:
#                 last_lines = lines[-params.disp_lines:]
#             for line in last_lines:
#                 data=data+line
#             file.close()
        
#     return data





# @app.callback(Output(module+'outfile', 'children'),
#               [Input(module+'page1', 'children'),
#                 Input(module+'store', 'data')]
#               )
# def convert_update_outfile(update,data):           
#     return data['log_file']




# Full page layout:
    
page = []
page.append(intervals)
page.append(page1)
page.append(collapse_stdout)

