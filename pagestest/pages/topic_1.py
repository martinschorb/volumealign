from dash import html

import dash
import dash_bootstrap_components as dbc

from .side_bar import sidebar

dash.register_page(
    __name__,
    name="Topics",
    top_nav=True,
)


def layout():
    return [sidebar(), html.Div("Topics Home Page", className='main')]
