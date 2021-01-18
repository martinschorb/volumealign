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
    
    store.append(html.Div(id=module+'outfile',style={'display':'none'}))
    store.append(dcc.Store(id=module+'name',data=module.rstrip('_')))
    
    newstore = params.default_store.copy()
    newstore.update(storeinit)
    
    for storeitem in newstore.keys():       
        store.append(dcc.Store(id=module+'store_'+storeitem, storage_type='session',data=newstore[storeitem]))
    
    return store



def render_selector(module):
    out = html.Div(id=module+'page1',children=[html.H4('Current active stack:'),
                                             html.Div([html.Div('Owner:',style={'margin-right': '1em','margin-left': '2em'}),
                                                       dcc.Dropdown(id=module+'owner_dd',className='dropdown_inline',options=[{'label':'1','value':'1'}],style={'width':'120px'},
                                                          persistence=True,
                                                          clearable=False),
                                                       html.Div(id=module+'owner',style={'display':'none'}),
                                                       html.Div('Project',style={'margin-left': '2em'}),
                                                       html.A('(Browse)',id=module+'browse_proj',target="_blank",style={'margin-left': '0.5em','margin-right': '1em'}),
                                                       dcc.Dropdown(id=module+'project_dd',className='dropdown_inline',
                                                          persistence=True,
                                                          clearable=False),
                                                       html.Div(id=module+'proj',style={'display':'none'}),
                                                       html.Div('Stack',style={'margin-left': '2em'}),
                                                       html.A('(Browse)',id=module+'browse_stack',target="_blank",style={'margin-left': '0.5em','margin-right': '1em'}),
                                                       dcc.Dropdown(id=module+'stack_dd',className='dropdown_inline',
                                                          persistence=True,
                                                          clearable=False),
                                                       dcc.Store(id=module+'stacks'),
                                             
                                             ],style=dict(display='flex'))
                                             ])

    return out



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
                                                                 html.Div(id=module+'outfile',style={"font-family":"Courier New"})
                                                                 ]),
                          dcc.Textarea(id=module+'console-out',className="console_out",
                                      style={'width': '100%','height':200,"color":"#000"},disabled='True')                         
                          ])
                ])
            ],id=module+'consolebox')
    
    return out
     
# if __name__ == '__main__':
    
