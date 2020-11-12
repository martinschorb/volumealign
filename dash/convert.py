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


from app import app

from sbem import sbem_conv


module='convert_'


main = html.Div([html.H4("Import volume EM datasets - Choose type:",id='conv_head'),dcc.Dropdown(
        id=module+'dropdown1',persistence=True,
        options=[
            {'label': 'SBEMImage', 'value': 'SBEMImage'}            
        ],
        value='SBEMImage'
        )
    
    ])

page1 = html.Div(id=module+'page1')



@app.callback(Output(module+'page1', 'children'),
    [Input(module+'dropdown1', 'value')])
def convert_output(value):
    if value=='SBEMImage':
        return sbem_conv.page
    else:
        return [html.Br(),'No data type selected.']


# sbem = sbem_conv.page


# =============================================
# PROGRESS OUTPUT


consolefile = params.render_log_dir+'/out.txt'
    
# f = open(consolefile, 'w')
# f.close() 
    

# code block to insert the python/slurm console output:    

outfile=os.path.abspath(consolefile)


# orig_stdout = sys.stdout
# f = open(outfile, 'a')
# sys.stdout = f
# f.close()
# CODE EXECUTION GOES HERE!!!


collapse_stdout = html.Div(children=[
                html.Br(),
                html.Details([
                    html.Summary('Console output:'),
                    html.Div(id=module+"collapse",                 
                     children=[
                         dcc.Interval(id=module+'interval1', interval=10000,
                                      n_intervals=0),
                         html.Div(id=module+'div-out',children=['Log file: ',html.Div(id=module+'outfile',style={"font-family":"Courier New"},children=outfile)]),
                         dcc.Textarea(id=module+'console-out',className="console_out",
                                      style={'width': '100%','height':200,"color":"#000"},disabled='True')                         
                         ])
                ])
            ],id=module+'consolebox')



@app.callback(Output(module+'console-out','value'),
    [Input(module+'interval1', 'n_intervals'),Input(module+'outfile','children')])
def update_output(n,outfile):
    data=''
    
    if outfile is not None:
        file = open(outfile, 'r')    
        lines = file.readlines()
        if lines.__len__()<=params.disp_lines:
            last_lines=lines
        else:
            last_lines = lines[-params.disp_lines:]
        for line in last_lines:
            data=data+line
        file.close()    
        
    return data






# Full page layout:
    
page = []
page.append(page1)
page.append(collapse_stdout)

