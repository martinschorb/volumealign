from dash import html

import dash

from pagestest.pages.side_bar import sidebar

dash.register_page(__name__)

def layout():
    return [sidebar(), html.Div("Topic 3 content", className='main')]
