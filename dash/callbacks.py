#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 15:38:09 2020

@author: schorb
"""
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output


#for file browsing dialogs
import tkinter
from tkinter import filedialog



from app import app
import convert


@app.callback(Output('convert-page1', 'children'),
    [Input('conv_dropdown1', 'value')])
def convert_output(value):
    if value=='SBEMImage':
        return convert.sbem
    else:
        return [html.Br(),'No data type selected.']


@app.callback(Output('conv_input1', 'value'),
    [Input('conv_browse1', 'n_clicks')])
def convert_filebrowse1(click):   
    root = tkinter.Tk()
    root.withdraw()
    conv_inputdir = filedialog.askdirectory()
    root.destroy()
    return conv_inputdir



# --------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)