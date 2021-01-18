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
    
    store.append(html.Div(id={'component':'outfile','module':module},style={'display':'none'}))
    store.append(dcc.Store(id={'component':'name','module':module},data=module))
    
    newstore = params.default_store.copy()
    newstore.update(storeinit)

    
    for storeitem in newstore.keys():       
        store.append(dcc.Store(id={'component':'store_'+storeitem,'module':module}, storage_type='session',data=newstore[storeitem]))
    
    return store



def render_selector(module):
    out = html.Div(id={'component':'r_sel_head','module':module},
                   children=[html.H4('Current active stack:'),
                             html.Div([html.Div('Owner:',style={'margin-right': '1em','margin-left': '2em'}),
                                       dcc.Dropdown(id={'component':'owner_dd','module':module},
                                                    className='dropdown_inline',
                                                    options=[{'label':'1','value':'1'}],
                                                    style={'width':'120px'},
                                                    persistence=True,clearable=False),
                                       html.Div(id={'component':'owner','module':module},
                                                style={'display':'none'}),
                                       html.Div('Project',style={'margin-left': '2em'}),
                                       html.A('(Browse)',id={'component':'browse_proj','module':module},
                                              target="_blank",style={'margin-left': '0.5em','margin-right': '1em'}),
                                       dcc.Dropdown(id={'component':'project_dd','module':module},
                                                    className='dropdown_inline',
                                                    persistence=True,clearable=False),
                                       html.Div(id={'component':'project','module':module},
                                                style={'display':'none'}),
                                       html.Div('Stack',style={'margin-left': '2em'}),
                                       html.A('(Browse)',id={'component':'browse_stack','module':module},
                                              target="_blank",style={'margin-left': '0.5em','margin-right': '1em'}),
                                       dcc.Dropdown(id={'component':'stack_dd','module':module},className='dropdown_inline',
                                                    persistence=True,clearable=False),
                                       dcc.Store(id={'component':'stacks','module':module})
                                       ],style=dict(display='flex'))
                             ])

    return out



def compute_loc(module):
    out = html.Details([html.Summary('Compute location:'),
                        dcc.RadioItems(
                            options=[
                                {'label': 'Cluster (slurm)', 'value': 'slurm'},
                                {'label': 'locally (this submission node)', 'value': 'standalone'}
                                ],
                            value='slurm',
                            labelStyle={'display': 'inline-block'},
                            id={'component':'compute_sel','module':module}
                            )
                        ],
                      id={'component':'compute','module':module})
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
    
