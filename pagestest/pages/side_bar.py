import dash
from dash import html, callback
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State, MATCH, ALL

style_active = {"background-color": "#077", "color": "#f1f1f1"}

def sidebar():

    menu = list()

    for page in dash.page_registry.values():
        print(page)
        if page["path"] != '/':
            menu.append(dbc.NavLink(
                        [
                            html.Div(page["name"], className="ms-2"),
                        ],
                        id = {'component': 'menu', 'module':  page["path"]},
                        href = page["path"],
                        active = "partial",
                    ))
            menu.append(html.Br())




    return html.Div(
        dbc.Nav(menu,
            vertical=True,
            pills=True,
            className="sidebar",
        )
    )

@callback(Output({'component': 'menu', 'module': MATCH}, 'active'),
          Input('url', 'pathname'))
def pointmatch_mcown_dd_sel(thispage):

    cc = dash.ctx

    if thispage!='/' and thispage in cc.outputs_list['id']['module']:
        print(thispage)
        return True

    else:
        return False

