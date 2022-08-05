import dash
from dash import html, callback
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State, MATCH, ALL

from pagestest.index import menu_items

style_active = {"background-color": "#077", "color": "#f1f1f1"}

def sidebar():

    menu = list()
    reg = list(dash.page_registry.values())

    paths = []
    for page in reg:
        paths.append(page["path"].strip('/'))

    for m_item in menu_items:

        # print(page)
        if m_item in paths:
            menu.append(dbc.NavLink(
                        [
                            html.Div(reg[paths.index(m_item)]["name"]),
                        ],
                        id = {'component': 'menu', 'module':  m_item},
                        href = '/' + m_item,
                        active = "partial",
                    ))
            menu.append(html.Br())




    return html.Div(
        dbc.Nav(menu,
                id='sidenav',
                vertical=True,
                pills=True,
                className="sidebar",
        )
    )

@callback(Output({'component': 'menu', 'module': MATCH}, 'active'),
          Input('url', 'pathname'))
def pointmatch_mcown_dd_sel(thispage):

    cc = dash.ctx
    # print(thispage)

    if thispage!='/' and thispage in cc.outputs_list['id']['module']:

        return True

    else:
        return False

