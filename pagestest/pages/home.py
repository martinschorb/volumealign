from dash import html

import dash
import dash_bootstrap_components as dbc

from pagestest.pages.side_bar import sidebar

dash.register_page(
    __name__,
    path="/",
    top_nav=True,
)

content = html.Div('This is the Web interface to run EM alignment processing.')

def layout():
    return dbc.Row(
        [dbc.Col(sidebar(), width=2), dbc.Col(html.Div([html.H3('Welcome to the Render-based alignment suite.'),
                      content], id={'component': 'page', 'module': 'start'}, className='main'))]
    )



