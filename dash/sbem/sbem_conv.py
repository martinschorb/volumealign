#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 08:42:12 2020

@author: schorb
"""
import dash_core_components as dcc
import dash_html_components as html
import subprocess
import sys
import os
from dash.dependencies import Input,Output

from app import app
from params import *


# SELECT input directory

# get user name and main group to pre-polulate input directory

p=subprocess.Popen('id -gn',stdout=subprocess.PIPE,shell=True)
group = p.communicate()[0].decode(encoding='utf8').strip("\n")

directory_sel = html.Div(children=[html.H4("Select dataset root directory:"),
                          dcc.Input(id="conv_input1", type="text", debounce=True,placeholder="/g/"+group,persistence=True),
                          html.Button('Browse',id="conv_browse1"),' graphical browsing works on cluster login node ONLY!',
                          html.Div(id='warning-popup')])



# Choose Render parameters








consolefile = './out.txt'
    
f = open(consolefile, 'w')
f.close() 
    

# code block to insert the python/slurm console output:    

outfile=os.path.abspath(consolefile)
label = "-sbem_convert"

orig_stdout = sys.stdout
f = open(outfile, 'a')
sys.stdout = f

# CODE EXECUTION GOES HERE!!!

# print('Intervals Passed: ' + str(n))
sys.stdout = orig_stdout
f.close()



collapse_stdout = html.Div([
    html.Br(),
    html.Details([
                html.Summary('Console output:'),
                html.Div(id="collapse"+label,                 
                     children=[
                         dcc.Interval(id='interval1'+label, interval= refresh_interval,
                                      n_intervals=0),
                         html.Div(id='div-out'+label,children='Console output logged into: '+outfile),
                         dcc.Textarea(id='console-out'+label,
                                      style={'width': '100%','height':200},disabled='True'),
                         html.Div(id='outfile'+label,children=outfile,style={'display':'none'})
                         ])
                ])
            ])


@app.callback(Output('div-out'+label,'children'),
    [Input('interval1'+label, 'n_intervals'),Input('outfile'+label,'children')])
def update_interval(n,outfile):    
    return 'Console output logged into: '+outfile

@app.callback(Output('console-out'+label,'value'),
    [Input('interval1'+label, 'n_intervals'),Input('outfile'+label,'children')])
def update_output(n,outfile):
    file = open(outfile, 'r')
    data=''
    lines = file.readlines()
    if lines.__len__()<=disp_lines:
        last_lines=lines
    else:
        last_lines = lines[-disp_lines:]
    for line in last_lines:
        data=data+line
    file.close()    
    
        
    return data





# ---- page layout

page = html.Div([directory_sel,collapse_stdout])