#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 15:26:45 2020

@author: schorb
"""

import dash
from dash import html, dcc, __version__

from dashUI import params

title_header = 'Volume EM alignment with Render'

menu_items = [
    'convert',
    # 'mipmaps',
    'tilepairs',
    'pointmatch',
    'solve',
    'export',
    'finalize'
]

home_title = 'VolumeAlign WebUI'

menu_titles = {'convert': 'Convert & upload',
               'mipmaps': 'Generate MipMaps',
               'tilepairs': 'Find Tile Pairs',
               'pointmatch': 'Find Point Matches',
               'solve': 'Solve Positions',
               'export': 'Export aligned volume',
               'finalize': 'Final post-processing'
               }

navbar = html.Div(id='navbar', className='header', children=html.H1([dcc.Link(href='/', children=title_header),
                                                                     html.A(html.Img(src='assets/help.svg',
                                                                                     id="helplink_image"),
                                                                            href=params.doc_url,
                                                                            target="_blank")
                                                                     ], className='header'))

globalstore = html.Div([dcc.Store(id='render_store', data=params.default_store['init_render'], storage_type='session')
                        ])
