from dash import html
import dash

import dash_bootstrap_components as dbc

from pagestest.pages.side_bar import sidebar

dash.register_page(__name__)


def layout():
    return dbc.Row(
        [dbc.Col(sidebar(), width=2), dbc.Col(html.Div("ABOOUUUUT", className='main'), width=10)]
    )
