from dash import html
import dash

from pagestest.pages.side_bar import sidebar

dash.register_page(
    __name__,
    name="Topics"
)

def layout():
    return [sidebar(), html.Div("Topics Home Page", className='main')]
