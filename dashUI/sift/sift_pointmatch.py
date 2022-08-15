#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:30:16 2020

@author: schorb
"""

import dash
from dash import dcc, html, callback, clientside_callback
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

import os
import glob
import json

from dashUI import params

from dashUI.utils import pages, matchTrial, launch_jobs

from dashUI.utils import helper_functions as hf

from dashUI.callbacks import runstate, comp_settings


# element prefix
label = "pointmatch_sift"
parent = "pointmatch"

page = []

storeinit = {'tpmatchtime': 1000}
store = pages.init_store(storeinit, label)

status_table_cols = ['stack',
                     'slices',
                     'tiles',
                     'tilepairs']

compute_table_cols = ['Num_CPUs',
                      # 'MemGB_perCPU',
                      'runtime_minutes']

compute_locations = ['sparkslurm', 'localspark', 'spark::render.embl.de']

compute_default = 'sparkslurm'

page1 = [html.Br(), pages.render_selector(label, show=False), html.Div(store)]

page2 = []

matchtrial = html.Div([html.Br(),
                       html.H4("Select appropriate Parameters for the SIFT search"),
                       html.Div(['Organism template: ',
                                 dcc.Dropdown(id=label + 'organism_dd', persistence=True,
                                              clearable=False),
                                 html.Br(),
                                 html.Div(["Select template Match Trial parameters."
                                           ],
                                          id=label + 'mt_sel'),
                                 dcc.Store(id=label + 'picks'),
                                 dcc.Dropdown(id=label + 'matchID_dd', persistence=True,
                                              clearable=False),
                                 html.Br(),
                                 html.Div(id=label + 'mtbrowse',
                                          children=[html.Button('Explore MatchTrial', id=label + 'mt_linkbutton'),
                                                    html.A('  - ',
                                                           id=label + 'mt_link',
                                                           target="_blank"),
                                                    dcc.Loading(
                                                        id=label + "link_loading",
                                                        type="dot",
                                                        children=html.Div('', id=label + 'mt_jscaller',
                                                                          style={'display': 'none'})
                                                    )
                                                    ]),
                                 html.Br(),

                                 html.Br(),
                                 html.Div(["Use this Match Trial as compute parameters:",
                                           dcc.Input(id=label + 'mtselect', type="text",
                                                     style={'margin-right': '1em', 'margin-left': '3em'},
                                                     debounce=True, placeholder="MatchTrial ID", persistence=False)],
                                          style={'display': 'flex'}),
                                 html.Br()
                                 ])
                       ])

page2.append(matchtrial)

#  =============================================
# Start Button

gobutton = html.Div(children=[html.Br(),
                              html.Button('Start PointMatch Client', id=label + "go"),
                              pages.compute_loc(label, c_options=compute_locations,
                                                c_default=compute_default),
                              html.Div(id=label + 'mtnotfound')
                              ],
                    style={'display': 'inline-block'})

page2.append(gobutton)

# # ===============================================
# Compute Settings

page2.append(pages.compute_settings(label, status_table_cols, compute_table_cols))

comp_settings.all_compset_callbacks(label, compute_table_cols)

# comp_settings callbacks

cs_params = comp_settings.compset_params(label, parent, status_table_cols)


@callback(cs_params,
          prevent_initial_call=True)
def sift_pointmatch_comp_settings(tilepairdir, matchtime, n_cpu, stack_sel, allstacks, status_table_cols, thispage):
    hf.is_url_active(thispage)

    if n_cpu is None:
        n_cpu = params.n_cpu_spark

    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    # n_cpu = int(n_cpu)

    out = dict()
    factors = dict()
    t_fields = [''] * len(status_table_cols)

    # numtp = 1

    if (not stack_sel == '-') and (allstacks is not None):
        stacklist = [stack for stack in allstacks if stack['stackId']['stack'] == stack_sel]
        stack = stack_sel

        if not stacklist == []:
            stackparams = stacklist[0]

            if 'None' in (stackparams['stackId']['owner'], stackparams['stackId']['project']):
                return dash.no_update

            out['zmin'] = stackparams['stats']['stackBounds']['minZ']
            out['zmax'] = stackparams['stats']['stackBounds']['maxZ']
            out['numtiles'] = stackparams['stats']['tileCount']
            out['numsections'] = stackparams['stats']['sectionCount']

            if tilepairdir is None or tilepairdir == '':
                numtp_out = 'no tilepairs'
                totaltime = None
            else:
                numtp = hf.tilepair_numfromlog(tilepairdir, stack_sel)

                if type(numtp) is int:
                    numtp_out = str(numtp)
                    totaltime = numtp * matchtime * params.n_cpu_standalone / 60000
                else:
                    numtp_out = 'no tilepairs'
                    totaltime = None

            t_fields = [stack, str(stackparams['stats']['sectionCount']), str(stackparams['stats']['tileCount']),
                        numtp_out]

            factors = {'runtime_minutes': totaltime}

    outlist = []  # ,out]
    outlist.extend(t_fields)
    outlist.append(factors)

    return outlist


@callback([Output(label + 'organism_dd', 'options'),
           Output(label + 'picks', 'data')],
          [Input({'component': 'tp_dd', 'module': parent}, 'value')],
          State('url', 'pathname'),
          prevent_initial_call=True)
def sift_pointmatch_organisms(tilepairdir, thispage):
    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    mT_jsonfiles = glob.glob(os.path.join(params.json_match_dir, '*.json'))

    organisms = list()

    picks = dict()

    for mT_file in mT_jsonfiles:
        with open(os.path.join(params.json_match_dir, mT_file), 'r') as f:
            indict = json.load(f)
            if indict['organism'] not in organisms:
                organisms.append(indict['organism'])
                picks[indict['organism']] = [indict['render']]
                picks[indict['organism']][0]['type'] = indict['type']
                picks[indict['organism']][0]['ID'] = indict['MatchTrial']
            else:
                picks[indict['organism']].append(indict['render'])
                picks[indict['organism']][-1]['type'] = indict['type']
                picks[indict['organism']][-1]['ID'] = indict['MatchTrial']

    dd_options = list(dict())

    for item in organisms:
        dd_options.append({'label': item, 'value': item})

    return dd_options, picks


@callback([Output(label + 'matchID_dd', 'options')],
          [Input(label + 'organism_dd', 'value'),
           Input(label + 'picks', 'data')],
          prevent_initial_call=True)
def sift_pointmatch_IDs(organism, picks):
    if not dash.callback_context.triggered:
        raise PreventUpdate

    dd_options = list(dict())

    if organism is not None:
        matchtrials = picks[organism]

        for item in matchtrials:
            ilabel = item['project'] + '-' + item['stack'] + '-' + item['type']
            dd_options.append({'label': ilabel, 'value': item['ID']})

    return [dd_options]


@callback([Output(label + 'mtselect', 'value'),
           Output(label + 'mt_link', 'href'),
           Output(label + 'mt_jscaller', 'children')],
          [Input(label + 'matchID_dd', 'value'),
           Input(label + 'mt_linkbutton', 'n_clicks'),
           Input({'component': 'matchcoll_dd', 'module': parent}, 'value')],
          [State({'component': 'tileim_link_0', 'module': parent}, 'children'),
           State({'component': 'tileim_link_1', 'module': parent}, 'children'),
           State({'component': 'tile_dd_1', 'module': parent}, 'value'),
           State({'component': 'tile_dd_1', 'module': parent}, 'options')]
          )
def sift_browse_matchTrial(matchID, buttonclick, matchcoll, link1, link2, tile2sel, tile2options):
    if None in (matchID, link1, link2):
        return dash.no_update

    trigger = hf.trigger()

    mc_url = params.render_base_url + 'view/match-trial.html?'

    for item in tile2options:
        if tile2sel in item['value']:
            tile2label = item['label']

    if 'button' in trigger:
        tile_clip = matchTrial.invert_neighbour(tile2label)

        matchtrial, matchID = matchTrial.new_matchtrial(matchID, [link1, link2], clippos=tile_clip)

        mc_url += 'matchTrialId=' + matchID

        return matchID, mc_url, str(buttonclick)

    mc_url += 'matchTrialId=' + matchID

    return matchID, mc_url, dash.no_update


clientside_callback(
    """
    function(trigger, url) {
        window.open(arguments[1]);
        return {}
    }
    """,
    Output(label + 'mt_linkbutton', 'style'),
    Input(label + 'mt_jscaller', 'children'),
    State(label + 'mt_link', 'href')
)


# =============================================

#  LAUNCH CALLBACK FUNCTION

# =============================================

# TODO! (#1) Fix store  outputs to enable additional modules

@callback([Output(label + 'go', 'disabled'),
           Output(label + 'mtnotfound', 'children'),
           Output({'component': 'store_launch_status', 'module': label}, 'data'),
           Output({'component': 'store_render_launch', 'module': label}, 'data'),
           Output({'component': 'store_tpmatchtime', 'module': label}, 'data')],
          [Input(label + 'go', 'n_clicks'),
           Input(label + 'mtselect', 'value'),
           Input({'component': 'matchcoll_dd', 'module': parent}, 'value')],
          [State({'component': 'compute_sel', 'module': label}, 'value'),
           State({'component': 'mc_owner_dd', 'module': parent}, 'value'),
           State({'component': 'tp_dd', 'module': parent}, 'value'),
           State({'component': 'store_owner', 'module': parent}, 'data'),
           State({'component': 'store_project', 'module': parent}, 'data'),
           State({'component': 'stack_dd', 'module': parent}, 'value'),
           State({'component': 'input_Num_CPUs', 'module': label}, 'value'),
           State({'component': 'input_runtime_minutes', 'module': label}, 'value'),
           State('url', 'pathname')],
          prevent_initial_call=True)
def sift_pointmatch_execute_gobutton(click, matchID, matchcoll, comp_sel, mc_owner, tilepairdir, owner, project, stack,
                                     n_cpu, timelim, thispage):
    thispage = thispage.lstrip('/')

    if thispage == '' or thispage not in hf.trigger(key='module'):
        raise PreventUpdate

    ctx = dash.callback_context

    trigger = ctx.triggered[0]['prop_id']

    try:
        mt_params = matchTrial.mt_parameters(matchID)
    except json.JSONDecodeError:
        return True, 'Could not find this MatchTrial ID!', dash.no_update, dash.no_update, dash.no_update
    except ValueError:
        return True, 'Could not find this MatchTrial ID!', dash.no_update, dash.no_update, dash.no_update

    if mt_params == {}:
        return True, 'No MatchTrial selected!', dash.no_update, dash.no_update, dash.no_update

    outstore = dict()
    outstore['owner'] = owner
    outstore['project'] = project
    outstore['stack'] = stack
    # outstore['mt_params'] = mt_params
    outstore['matchcoll'] = matchcoll
    outstore['mc_owner'] = mc_owner

    if tilepairdir == '':
        return True, 'No tile pair directory selected!', dash.no_update, outstore, dash.no_update

    if matchcoll in ('', 'new_mc', 'new_mcoll'):
        return True, 'No Match collection selected!', dash.no_update, outstore, dash.no_update

    if 'mtselect' in trigger:
        return False, '', dash.no_update, outstore, mt_params['ptime']
    elif 'matchcoll_dd' in trigger:
        return False, '', dash.no_update, outstore, mt_params['ptime']

    elif 'go' in trigger:
        if click is None:
            return dash.no_update

        # prepare parameters:
        run_prefix = launch_jobs.run_prefix()

        run_params = params.render_json.copy()
        run_params['render']['owner'] = owner
        run_params['render']['project'] = project

        run_params_generate = run_params.copy()

        # tilepair files:

        tp_dir = os.path.join(params.json_run_dir, tilepairdir)

        tp_json = os.listdir(tp_dir)

        tp_jsonfiles = [os.path.join(params.json_run_dir, tilepairdir, tpj) for tpj in tp_json]

        param_file = params.json_run_dir + '/' + parent + '_' + run_prefix + '.json'

        if comp_sel == 'standalone':
            # =============================

            # TODO - STANDALONE PROCEDURE NOT TESTED !!!!

            # =============================

            # TODO!  render-modules only supports single tilepair JSON!!!

            cv_params = {
                "ndiv": mt_params['siftFeatureParameters']['steps'],
                "downsample_scale": mt_params['scale'],

                "pairJson": os.path.join(params.json_run_dir, tp_json[0]),
                "input_stack": stack,
                "match_collection": matchcoll,

                "ncpus": params.ncpu_standalone,
                "output_json": params.render_log_dir + '/' + '_' + run_prefix + "_SIFT_openCV.json",
            }

            run_params_generate.update(cv_params)

            target_args = None
            run_args = None
            script = params.asap_dir + '/pointmatch/generate_point_matches_opencv.py'

        elif 'spark' in comp_sel:
            spsl_p = dict()

            spsl_p['--baseDataUrl'] = params.render_base_url + params.render_version.rstrip('/')
            spsl_p['--owner'] = mc_owner
            spsl_p['--collection'] = matchcoll
            spsl_p['--pairJson'] = tp_jsonfiles

            mtrun_p = dict()

            # some default values...

            mtrun_p['--matchMaxNumInliers'] = 200
            mtrun_p['--maxFeatureCacheGb'] = 6
            mtrun_p['--maxFeatureSourceCacheGb'] = 6

            # fill parameters

            mtrun_p['--renderScale'] = mt_params['scale']

            for item in mt_params['siftFeatureParameters'].items():
                mtrun_p['--SIFT' + item[0]] = item[1]

            for item in mt_params['matchDerivationParameters'].items():
                mtrun_p['--' + item[0]] = item[1]

            if 'clipPixels' in mt_params.keys():
                mtrun_p['--clipHeight'] = mt_params['clipPixels']
                mtrun_p['--clipWidth'] = mt_params['clipPixels']

            spark_args = {'--jarfile': params.render_sparkjar}

            spark_p = dict()

            if comp_sel == 'sparkslurm':
                spark_p['--time'] = '00:' + str(timelim) + ':00'

                spark_p['--worker_cpu'] = params.cpu_pernode_spark
                spark_p['--worker_nodes'] = hf.spark_nodes(n_cpu)
            else:
                spark_args['--cpu'] = launch_jobs.remote_params(comp_sel.split('::')[-1])['cpu']
                spark_args['--mem'] = launch_jobs.remote_params(comp_sel.split('::')[-1])['mem']

            run_params_generate = spsl_p.copy()
            run_params_generate.update(mtrun_p)

            target_args = spark_p.copy()
            run_args = run_params_generate.copy()

            script = 'org.janelia.render.client.spark.SIFTPointMatchClient'

        # generate script call...

        with open(param_file, 'w') as f:
            json.dump(run_params_generate, f, indent=4)

        log_file = params.render_log_dir + '/' + parent + '_' + run_prefix
        err_file = log_file + '.err'
        log_file += '.log'

        sift_pointmatch_p = launch_jobs.run(target=comp_sel,
                                            pyscript=script,
                                            jsonfile=param_file,
                                            run_args=run_args,
                                            target_args=target_args,
                                            special_args=spark_args,
                                            logfile=log_file, errfile=err_file)

        launch_store = dict()
        launch_store['logfile'] = log_file
        launch_store['status'] = 'running'
        launch_store['id'] = sift_pointmatch_p
        launch_store['type'] = comp_sel

        return True, '', launch_store, outstore, mt_params['ptime']


# =============================================
# Processing status

# initialized with store
# embedded from callbacks import runstate

# # =============================================
# # PROGRESS OUTPUT


collapse_stdout = pages.log_output(label)

# ----------------

# Full page layout:

page2.append(collapse_stdout)
