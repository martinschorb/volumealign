#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:24:32 2020

@author: schorb
"""

import params
import dash_core_components as dcc
import dash_html_components as html


def init_store(storeinit,module):
    store=list()
    
    store.append(dcc.Store(id=module+'name',data=module.rstrip('_')))
    
    newstore = params.default_store.copy()
    newstore.update(storeinit)
    
    for storeitem in newstore.keys():       
        store.append(dcc.Store(id=module+'store_'+storeitem, storage_type='session',data=newstore[storeitem]))
    
    return store



def log_output(module):
    out = html.Div(children=[
                html.Br(),
                html.Div(id=module+'job-status',children=['Status of current processing run: ',
                                                          html.Div(id=module+'get-status',style={"font-family":"Courier New"},children=[
                                                              'not running']),
                                                          html.Button('cancel cluster job(s)',id=module+"cancel",style={'display': 'none'})                                                         
                                                          ]),
                html.Br(),
                html.Details([
                    html.Summary('Console output:'),
                    html.Div(id=module+"collapse",                 
                      children=[                         
                          html.Div(id=module+'div-out',children=['Log file: ',
                                                                 html.Div(params.render_log_dir + '/out.txt',
                                                                          id=module+'outfile',style={"font-family":"Courier New"})
                                                                 ]),
                          dcc.Textarea(id=module+'console-out',className="console_out",
                                      style={'width': '100%','height':200,"color":"#000"},disabled='True')                         
                          ])
                ])
            ],id=module+'consolebox')
    
    return out
     
# if __name__ == '__main__':
    
