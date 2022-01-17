#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:24:32 2020

@author: schorb
"""

import params
from dash import dcc
from dash import html

import plotly.express as px

from utils import checks
from utils import helper_functions as hf

def init_store(storeinit,module):
    store=list()
    
    # store.append(html.Div(id={'component':'outfile','module':module},style={'display':'none'}))
    store.append(dcc.Store(id={'component':'name','module':module},data=module))
    
    newstore = params.default_store.copy()
    newstore.update(storeinit)

    for storeitem in newstore.keys():       
        store.append(dcc.Store(id={'component':'store_'+storeitem,'module':module}, storage_type='session',data=newstore[storeitem]))

    return store


def render_selector(module,header='Active stack:',owner=False,create=False,show=True):
    
    dst=dict(display='block')    

    
    new_proj_style = dict(display='none')
    new_stack_style =  dict(display='none')
    
    
    # determine which selectors to show
    own_style = dict(display='none')
    proj_style = dict(display='none')
    stack_style = dict(display='none')
    
    if show == True:
        own_style = dict(display='inline-block')
        proj_style = dict(display='inline-block')
        stack_style = dict(display='inline-block')
    elif not show: 
        dst = dict(display='none')
        own_style = dict(display='none')
        proj_style = dict(display='none')
        stack_style = dict(display='none')
    else:
        if type(show) is str: show = [show]
        
        if any(o in show for o in ['Owner','owner']):
            own_style = dict(display='inline-block')
        if any(p in show for p in ['Project','project']):    
            proj_style = dict(display='inline-block')
        if any(s in show for s in ['Stack','stack']):    
            stack_style = dict(display='inline-block')   
    
    # determine which creation elements to show
    
    if create == True:
        new_proj_style = {}
        new_stack_style =  {}
    elif not create: 
        new_proj_style = dict(display='none')
        new_stack_style =  dict(display='none')
    else:
        if type(create) is str: create = [create]
        
        if any(p in create for p in ['Project','project']):    
            new_proj_style = {}
        if any(s in create for s in ['Stack','stack']):    
            new_stack_style = {}
    
    
    # show owner selector or predetermine its value
    
    if owner in (False,''):
        owner = ''        
    else: own_style = dict(display='none')
    
    
    out = html.Div(id={'component':'r_sel_head','module':module},
                   children=[html.H4(header),
                             html.Table(html.Tr([
                                 
                        # Owner selection
                        html.Td([html.Table(html.Tr([
                            html.Td(html.Div('Owner:',style={'margin-right': '1em','margin-left': '2em'})),
                            html.Td(dcc.Dropdown(id={'component':'owner_dd','module':module},
                                                 className='dropdown_inline',
                                                 options=[],value=owner,
                                                 persistence=True,clearable=False))
                            ])),
                        html.Div(id={'component':'owner','module':module},
                                 style={'display':'none'}),            
                        ],style=own_style),
                                     
                        # Project selection
                        html.Td([html.Table(html.Tr([                        
                            html.Td(html.Div('Project:',style={'margin-left': '2em'})),
                            html.Td(html.A('(Browse)',id={'component':'browse_proj','module':module},
                                           target="_blank",style={'margin-left': '0.5em','margin-right': '1em'})),
                            html.Td(dcc.Dropdown(id={'component':'project_dd','module':module},
                                                 className='dropdown_inline',
                                                 persistence=True,clearable=False))
                            ])),
                            dcc.Store(id={'component':'project_store','module':module}),
                            
                        # creator
                        html.Div(html.Div(['Enter new project name: ',
                                           dcc.Input(id={'component':"proj_input",'module':module}, type="text", debounce=True,placeholder="new_project",persistence=False)
                                           ],
                                          id={'component':'render_project','module':module}
                                          ,style={'display':'none'})
                                 ,id={'component':'new_project_div','module':module}
                                 ,style=new_proj_style)
                        
                            ]
                            ,id={'component':'full_project_div','module':module}
                            ,style=proj_style),
                        
                        # Stack selection
                        html.Td([html.Table(html.Tr([
                            html.Td(html.Div('Stack:',style={'margin-left': '2em'})),
                            html.Td(html.A('(Browse)',id={'component':'browse_stack','module':module},
                                           target="_blank",style={'margin-left': '0.5em','margin-right': '1em'})),
                            html.Td(dcc.Dropdown(id={'component':'stack_dd','module':module},
                                                 className='dropdown_inline',
                                                 persistence=True,clearable=False))
                            ])),
                            dcc.Store(id={'component':'stacks','module':module}),
                            
                            # creator
                            html.Div(html.Div(['Enter new stack name: ',
                                               dcc.Input(id={'component':"stack_input",'module':module}, type="text", debounce=True,placeholder="new_stack",persistence=False)
                                               ],
                                              id={'component':'render_stack','module':module},style={'display':'none'})
                                     ,id={'component':'new_stack_div','module':module}
                                     ,style=new_stack_style)    
                            ]
                            ,id={'component':'full_stack_div','module':module}
                            ,style=stack_style)
                        ]))
                    ],style = dst)

    return out


def match_selector(module,newcoll=False):
    mc_owner_dd_options = list(dict())
    mc_dd_options = list(dict())
    
    mc_own = ''
    mcoll = ''
    
    if newcoll:
        mc_own = 'new_mc_owner'
        mc_owner_dd_options.append({'label':'new Match Collection Owner', 'value':'new_mc_owner'})
        mcoll = 'new_mc'
        mc_dd_options = [{'label':'new Match Collection', 'value':'new_mc'}]
        
        
    out = html.Div([html.H4("Select Match Collection:"),
                    dcc.Store(id={'component':'mc_new_enabled','module':module},data=str(newcoll)),
                    html.Div([html.Div('Match Collection Owner:',style={'margin-right': '1em','margin-left': '2em'}),
                          dcc.Dropdown(id={'component':'mc_owner_dd','module':module},
                                       persistence=True,clearable=False,className='dropdown_inline',
                                       options=mc_owner_dd_options, value=mc_own),
                          html.Div([html.Div('Enter new Match Collection Owner:',
                                             style={'margin-right': '1em','margin-left': '2em'}),
                                    dcc.Input(id={'component':"mcown_input",'module':module}, type="text",
                                                  style={'margin-right': '1em','margin-left': '3em'},
                                                  debounce=True,placeholder="new_mc_owner",persistence=False)],
                                id={'component':'new_mc_owner','module':module},
                                style={'display':'none'}),
                          html.Br(),
                          html.Div([html.Div('Match Collection:',style={'margin-right': '1em','margin-left': '2em'}),
                                    dcc.Dropdown(id={'component':'matchcoll_dd','module':module},persistence=True,
                                                 clearable=False,className='dropdown_inline',
                                                 options=mc_dd_options, value=mcoll),
                                    html.Br()],
                                   id={'component':'matchcoll','module':module},style={'display':'none'}),
                          html.Div([html.Div('Enter new Match Collection:',
                                             style={'margin-right': '1em','margin-left': '2em'}),
                                    dcc.Input(id={'component':"mc_input",'module':module}, type="text",
                                                  style={'margin-right': '1em','margin-left': '3em'},
                                                  debounce=True,placeholder="new_mc",persistence=False)],
                                   id={'component':'new_matchcoll','module':module},
                                   style={'display':'none'}),
                          html.Br()
                          ],style=dict(display='flex')),
                    html.Div(id={'component':'browse_mc_div','module':module},
                             children=[html.A('Explore Match Collection',
                                              id={'component':'browse_mc','module':module},
                                              target="_blank",style={'margin-left': '0.5em','margin-right': '1em'}),
                                       ],style={'display':'none'})
                ])

    return out


def compute_loc(module,c_options=params.comp_defaultoptions,c_default=params.comp_default):
    if len(c_options)<2:
        dispstyle={'display':'none'}
    else:
        dispstyle={}

    out = html.Div(html.Details([html.Summary('Compute location:'),
                        dcc.RadioItems(
                            options = hf.compset_radiobutton(c_options),
                            value = c_default,
                            labelStyle={'display': 'inline-block'},
                            id={'component':'compute_sel','module':module}
                            )
                        ],
                      id={'component':'compute','module':module}),
                   style=dispstyle)
    return out


def log_output(module):
    out = html.Div(children=[
                html.Br(),
                html.Div(id={'component': 'job-status', 'module': module},children=['Status of current processing run: ',
                                                          html.Div(id={'component': 'get-status', 'module': module},style={"font-family":"Courier New"},children=[
                                                              'not running']),
                                                          html.Button('cancel cluster job(s)',id={'component': "cancel", 'module': module},style={'display': 'none'}),
                                                          html.Div(id={'component': 'statuspage_div', 'module': module},
                                                                   children=['Processing ',
                                                                             html.A('status page', id={'component':'statuspage_link','module':module},
                                                                                    target="_blank")
                                                                       ], style={'display': 'none'})
                                                          ]),
                html.Br(),
                html.Details([
                    html.Summary('Console output:'),
                    html.Div(id={'component': "collapse", 'module': module},                 
                      children=[                         
                          html.Div(id={'component': 'div-out', 'module': module},children=['Log file: ',
                                                                 html.Div(id={'component': 'outfile', 'module': module},style={"font-family":"Courier New"},
                                                                          children=params.init_logfile)
                                                                 ]),
                          dcc.Textarea(id={'component': 'console-out', 'module': module},className="console_out",
                                      style={'width': '100%','height':200,"color":"#000"},disabled='True')                         
                          ])
                ])
            ],id={'component': 'consolebox', 'module': module})
    
    return out


def substack_sel(module,hidden=False):   
    dispstyle = {}
    if hidden:
        dispstyle = {'display':'none'}
    out = html.Div([html.Div(id={'component':'3Dslices', 'module': module},
                                        children=['range of sections to consider:  ',
                                                  dcc.Input(id={'component':'sec_input1', 'module': module},type='number',min=1,max=10,value=0)],
                                                      style={'display':'none'}),
                    html.Br(),
                    html.Details([html.Summary('Substack selection'),
                        html.Table([html.Tr([html.Td('Start slice: '),
                                             html.Td(dcc.Input(id={'component': 'startsection', 'module': module},type='number',min=0,value=0))]),
                                    html.Tr([html.Td('End slice: '),
                                             html.Td(dcc.Input(id={'component': 'endsection', 'module': module},type='number',min=0,value=1))])])
                                                            ])
                   ],
                   style=dispstyle)
                   
    
    return out


def boundingbox(module,hidden=False):   
    dispstyle = {}
    if hidden:
        dispstyle = {'display':'none'}
        
    inputs = []

    for dim in ['X','Y','Z']:
        inputs.append(html.Tr([html.Td('Start '+dim+': '),
                               html.Td(dcc.Input(id={'component': 'start'+dim, 'module': module},type='number',debounce=True,min=0,value=0)),
                               html.Td('End '+dim+': '),
                               html.Td(dcc.Input(id={'component': 'end'+dim, 'module': module},type='number',debounce=True,min=0,value=0))]))

    out = html.Div([html.Details([html.Summary('Volume region to consider:'),
                        html.Br(),
                        html.Table(inputs)
                        ])
                    ],
                    id={'component':'BBox', 'module': module},
                    style=dispstyle)
                   
    
    return out


def tile_view(module,numpanel=1,showlink=False,contrast=True,neighbours=True):

    if numpanel<2: neighbours=False

    out = list()
        
    linkstyle = {'display':'none'}
    contraststyle = {'display':'none'}
    
    if showlink:
        linkstyle = {}
        
    if contrast:
        contraststyle = {}

    if not neighbours:
        out.append(dcc.Dropdown(id={'component': 'tp_dd', 'module': module},style={'display':'none'}))

    out.append(html.Div(str(neighbours), id={'component': 'neighbours', 'module': module}, style={'display': 'none'}))
    out.append(dcc.Store(data=dict(),id={'component': 'lead_tile', 'module': module}))
        
    for idx in range(numpanel):
        idx_str = '_'+str(idx)
        if numpanel>1:            
            idx_title=' '+str(idx+1)
        else:
            idx_title=''

        out.append(html.Div([html.Details([html.Summary('Explore tile'+idx_title),
                                  html.Table([html.Tr([html.Div(
                                      [html.Td('Slice:'),
                                       html.Td(dcc.Input(id={'component': 'tileim_section_in'+idx_str, 'module': module},type='number',min=0,value=0))],
                                                               id={'component': 'tileim_section_div'+idx_str, 'module': module},
                                                               style={}),
                                                       html.Td('Tile'),
                                                       html.Td(dcc.Dropdown(id={'component': 'tile_dd'+idx_str, 'module': module},className='dropdown_inline'))])
                                              ]),
                                  html.Div(style=contraststyle,id={'component': 'tileim_contrastdiv'+idx_str, 'module': module},children=[
                                      'Contrast limits: ',
                                      dcc.RangeSlider(
                                            id={'component': 'tileim_contrastslider'+idx_str, 'module': module},
                                            min=0,
                                            max=500,
                                            value=[0, 255],
                                            allowCross=False,
                                            tooltip={"placement": "bottom"}
                                        )
                                      ]),
                                  dcc.Store(id={'component': 'tileim_urlset'+idx_str, 'module': module}, data={}),
                                  html.Div(style={'display':'none'},id={'component': 'tileim_imurl'+idx_str, 'module': module}),
                                  html.Div(style=linkstyle,id={'component': 'tileim_linkdiv'+idx_str, 'module': module},children=[
                                      'Link to Image specs:  ',
                                      html.Div(id={'component': 'tileim_link'+idx_str, 'module': module},style={'margin-left': '0.5em'})
                                      ]),
                                  html.Br(),
                                  html.Img(id={'component': 'tileim_image'+idx_str, 'module': module},width=params.im_width),
                                  # dcc.Graph(id={'component': 'tileim_image'+idx_str, 'module': module}),
                                  dcc.Store(data=dict(),id={'component': 'lead_tile'+idx_str, 'module': module}),
                                  html.Br()])
                    ]
                   )
                   )

    
    return html.Div(out)



def section_view(module,numpanel=1,contrast=True):
    
    out = list()    

    contraststyle = {'display':'none'}

    if contrast:
        contraststyle = {}

    for idx in range(numpanel):
        idx_str = '_'+str(idx)
        if numpanel>1:            
            idx_title=' '+str(idx+1)
        else:
            idx_title=''

        fig = px.imshow([[255,255],[255,255]])
        fig.update_layout(coloraxis_showscale=False)
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)

        out.append(html.Div([html.Details([html.Summary('Explore slice'+idx_title),
                                  html.Div(
                                      html.Table([html.Tr([html.Td('Slice:'),
                                                       html.Td(dcc.Input(id={'component': 'sliceim_section_in'+idx_str, 'module': module},type='number',min=0,value=0)),
                                                       ])
                                      ]),
                                      id={'component': 'sliceim_section_div'+idx_str, 'module': module},
                                      style={}),
                                  html.Div(style=contraststyle,id={'component': 'sliceim_contrastdiv'+idx_str, 'module': module},children=[
                                      'Contrast limits: ',
                                      dcc.RangeSlider(
                                            id={'component': 'sliceim_contrastslider'+idx_str, 'module': module},
                                            min=0,
                                            max=500,
                                            value=[0, 255],
                                            allowCross=False,
                                            tooltip={"placement": "bottom", "always_visible": True}
                                        )
                                      ]),
                                  dcc.Store(id={'component': 'sliceim_urlset'+idx_str, 'module': module}, data = {}),
                                  html.Div(style={'display':'none'},id={'component': 'sliceim_imurl'+idx_str, 'module': module}),
                                  # html.Img(id={'component': 'sliceim_image'+idx_str, 'module': module},width=params.im_width),
                                  dcc.Graph(id={'component': 'sliceim_image'+idx_str, 'module': module},figure=fig),
                                  html.Br(),
                                  # html.Div([html.Button('Zoom in',id={'component': 'slice_zoom', 'module': module}),' ',html.Button('Reset Zoom',id={'component': 'slice_reset', 'module': module})],
                                  #          style={'text-align':'left-inline'})
                                ])
                    ]
                   )
                   )

    out.append(dcc.Store(data='', id={'component': 'dummystore', 'module': module}))

    return html.Div(out)



def path_browse(module,tf_in = None,show_files=False,file_types=[]):
    
    if tf_in is None:
        tf_in = {'component': 'path_input', 'module': module} 
    
    tf_in = checks.makeinput(tf_in)

    fbdd = dcc.Dropdown(id={'component': 'browse_dd', 'module': module} ,searchable=True,className='dropdown_inline')

        
    fbrowse = html.Details([html.Summary('Browse'),fbdd])
    fbstore = html.Div([dcc.Store(id={'component': 'path_store', 'module': module}),
                        dcc.Store(id={'component': 'path_ext', 'module': module})])
    showfiles = dcc.Store(data=show_files,id={'component': 'path_showfiles', 'module': module})
    filetypes = dcc.Store(data=file_types,id={'component': 'path_filetypes', 'module': module})
    
    return html.Div([fbrowse,fbstore,showfiles,filetypes])

# if __name__ == '__main__':
    
