#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 15:26:45 2020

@author: schorb
"""


from dash import html, dcc, __version__


from dashUI import params


menu_items = [
            'convert',
            # 'mipmaps',
            'tilepairs',
            'pointmatch',
            'solve',
            'export',
            'finalize'
            ]


navbar = html.Div(id='navbar',className='header', children= html.H1([dcc.Link(href='/', children='Volume EM alignment with Render'),
                                                        html.A(html.Img(src='assets/help.svg'), href=params.doc_url,
                                                               target="_blank")
                                                        ], className='header'))
