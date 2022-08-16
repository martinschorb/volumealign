from dash import html

import dash

from dashUI.pages.side_bar import sidebar
from dashUI.index import home_title

dash.register_page(
    __name__,
    path="/",
    top_nav=True,
    name=home_title
)

content = html.Div('This is the Web interface to run EM alignment processing.', id='startpage_main')

def layout():
    return [sidebar(),
            html.Div([html.H3('Welcome to the Render-based alignment suite.'), content],
                     id={'component': 'page', 'module': 'start'}, className='main')]



