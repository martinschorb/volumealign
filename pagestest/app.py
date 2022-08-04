import dash

from dash import html, dcc

import dash_bootstrap_components as dbc


app = dash.Dash(
    __name__,
    use_pages=True,
)


navbar = html.Div(className='header', children= html.H1([dcc.Link(href='/', children='Volume EM alignment with Render'),
                                                        html.A(html.Img(src='assets/help.svg'), href='https://ewgrdsvedsfg.dw',
                                                               target="_blank")
                                                        ], className='header'))



app.layout = dbc.Container(
    [navbar, dash.page_container, dcc.Location(id='url')],
    fluid=True,
)


if __name__ == "__main__":
    app.run_server(debug=True)
