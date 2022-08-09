import dash
from dash import html, dcc, callback

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
            menu.append(dcc.Link(
                        [
                            html.Div(reg[paths.index(m_item)]["name"]),
                        ],
                        id = {'component': 'menu', 'module':  m_item},
                        href = '/' + m_item
                    ))
            menu.append(html.Br())

    return html.Nav(menu,
                id='sidenav',
                className="sidebar"
        )


menu_cb_out = []
for m_item in menu_items:
    menu_cb_out.append(Output({'component': 'menu', 'module':  m_item}, 'style'))


@callback(menu_cb_out,
              [Input('url', 'pathname')],
              prevent_initial_call=True)
def display_page(pathname):
    """


    Parameters
    ----------
    pathname : TYPE
        DESCRIPTION.

    Returns
    -------
    outlist : TYPE
        DESCRIPTION.

    """
    s1 = style_active
    menu_styles = [{}] * len(menu_items)

    outlist = []

    for m_ind, m_item in enumerate(menu_items):
        if pathname == "/" + m_item:
            menu_styles[m_ind] = s1

    outlist.extend(menu_styles)
    print(outlist)

    return outlist
#
#
# @callback(Output({'component': 'menu', 'module': ALL}, 'active'),
#           Input('url', 'pathname'))
# def pointmatch_mcown_dd_sel(thispage):
#
#     cc = dash.ctx
#
#     print(cc.outputs_list)
#
#     if cc.triggered_id is None:
#         raise dash.exceptions.PreventUpdate
#
#     out = [False] * len(cc.outputs_list)
#     print(out)
#
#     for idx,output in enumerate(cc.outputs_list):
#         page =   output['id']['module']
#
#         if thispage!='/' and thispage in page:
#             out[idx] = True
#
#     print(out)
#
#     return out


