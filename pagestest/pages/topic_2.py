from dash import html
import dash

from pagestest.pages.side_bar import sidebar

dash.register_page(
    __name__,
    name='T2 Name!',
)

def layout():
    return [sidebar(), html.Div("Topic 2 content", className='main')]

