#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 14:52:17 2021

@author: schorb
"""

import dash
from dash import callback
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

import requests

import plotly.express as px
from skimage import io
import re

from dashUI import params
from dashUI.utils import helper_functions as hf

for idx in range(params.max_tileviews):
    idx_str = '_' + str(idx)

    # init slice selector
    for imtype in ['sliceim', 'tileim']:

        inputs = [Input({'component': 'stack_dd', 'module': MATCH}, 'value')]
        states = [State({'component': 'store_allstacks', 'module': MATCH}, 'data'),
                  State({'component': 'owner_dd', 'module': MATCH}, 'value'),
                  State({'component': 'project_dd', 'module': MATCH}, 'value'),
                  State({'component': imtype + '_section_in' + idx_str, 'module': MATCH}, 'value')]

        if imtype == 'tileim':
            inputs.append(Input({'component': 'lead_tile', 'module': MATCH}, 'modified_timestamp'))
            inputs.append(Input({'component': 'tp_dd', 'module': MATCH}, 'value'))
            states.extend([
                State({'component': 'neighbours', 'module': MATCH}, 'children'),
                State({'component': 'lead_tile', 'module': MATCH}, 'data')
            ])
        else:
            inputs.extend([Input({'component': 'dummystore', 'module': MATCH}, 'modified_timestamp')] * 2)
            states.extend([State({'component': 'dummystore', 'module': MATCH}, 'modified_timestamp')] * 2)

        states.append(State('url', 'pathname'))


        @callback([Output({'component': imtype + '_section_in' + idx_str, 'module': MATCH}, 'value'),
                   Output({'component': imtype + '_section_in' + idx_str, 'module': MATCH}, 'min'),
                   Output({'component': imtype + '_section_in' + idx_str, 'module': MATCH}, 'max'),
                   Output({'component': imtype + '_section_div' + idx_str, 'module': MATCH}, 'style'),
                   Output({'component': imtype + '_contrastslider' + idx_str, 'module': MATCH}, 'max'),
                   Output({'component': imtype + '_contrastslider' + idx_str, 'module': MATCH}, 'value')],
                  inputs,
                  states,
                  prevent_initial_call=True)
        def stacktoslice(stack_sel, lead_trigger, tilepairdir, allstacks, owner, project, orig_sec, neighbours,
                         lead_tile, thispage):
            stacklist = []
            slicestyle = {}

            thispage = thispage.lstrip('/')

            if thispage == '' or thispage not in hf.trigger(key='module'):
                raise PreventUpdate


            trigger = hf.trigger()

            ol = dash.callback_context.outputs_list

            thisimtype = ol[0]['id']['component'].split('_')[0]

            tileim_idx = ol[0]['id']['component'].split('_')[-1]

            if (not stack_sel == '-') and (allstacks is not None):
                stacklist = [stack for stack in allstacks if stack['stackId']['stack'] == stack_sel]
                # stack = stack_sel

            if not stacklist == []:
                stackparams = stacklist[0]

                if 'None' in (stackparams['stackId']['owner'], stackparams['stackId']['project']):
                    raise PreventUpdate

                if 'stats' not in stackparams.keys():
                    raise PreventUpdate

                o_min = stackparams['stats']['stackBounds']['minZ']
                o_max = stackparams['stats']['stackBounds']['maxZ']

                if orig_sec < o_min:
                    orig_sec = o_min
                if orig_sec > o_max:
                    orig_sec = o_max

                if neighbours == 'True' and tileim_idx != '0' and tilepairdir not in ('', None):
                    if type(lead_tile) is not dict:
                        raise PreventUpdate

                    if 'tile' in lead_tile.keys():

                        tp_jsonfiles = hf.jsonfiles(tilepairdir)

                        tiles, slices, positions = hf.neighbours_from_json(tp_jsonfiles, lead_tile['tile'])

                        if tiles in (None, []):
                            raise PreventUpdate

                        slices = list(map(int, slices))

                        o_val = min(slices)

                        slicestyle = {'display': 'none'}

                if trigger in ('stack_dd', 'dummystore'):
                    o_val = int((o_max - o_min) / 2) + o_min
                else:
                    o_val = orig_sec

                if o_min == o_max:
                    slicestyle = {'display': 'none'}

                if owner == 'FIBSEM' and thisimtype == 'tileim':
                    slicestyle = {'display': 'none'}

                url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project \
                      + '/stack/' + stack_sel
                url1 = url + '/tileIds'

                tile = requests.get(url1).json()[0]

                url2 = url + '/tile/' + tile
                url2 += '/render-parameters'

                tilespec = requests.get(url2).json()

                max_int = int(tilespec['tileSpecs'][0]['maxIntensity'])

                return o_val, o_min, o_max, slicestyle, max_int, [0, max_int]

            else:
                raise PreventUpdate

    # init tile selector
    @callback([Output({'component': 'tile_dd' + idx_str, 'module': MATCH}, 'options'),
               Output({'component': 'tile_dd' + idx_str, 'module': MATCH}, 'value')],
              [Input({'component': 'tileim_section_in' + idx_str, 'module': MATCH}, 'value'),
               Input({'component': 'tp_dd', 'module': MATCH}, 'value')],
              [State({'component': 'owner_dd', 'module': MATCH}, 'value'),
               State({'component': 'project_dd', 'module': MATCH}, 'value'),
               State({'component': 'stack_dd', 'module': MATCH}, 'value'),
               State({'component': 'tile_dd' + idx_str, 'module': MATCH}, 'value'),
               State({'component': 'neighbours', 'module': MATCH}, 'children'),
               State({'component': 'lead_tile', 'module': MATCH}, 'data'),
               State('url', 'pathname')],
              prevent_initial_call=True)
    def slicetotiles(slicenum, tilepairdir, owner, project, stack, prev_tile, neighbours, lead_tile, thispage):
        """
        Fills the tile selection dropdown with the tiles found for the selected slice.

        :param int slicenum: value of the slice selector "tileim_section_in"
        :param str tilepairdir: value of the tilepair dropdown. "tp_dd"
        :param str owner:
        :param str project:
        :param str stack:
        :param str prev_tile: current value of the tile selector dropdown
        :param list neighbours: neighbouring tiles if available "neighbours" <i>children</i>
        :param dict lead_tile: data of the "lead_tile" Store
        :param str thispage: current page URL
        :return: options and value of tile dropdown "tile_dd"
        :rtype: (list of dict, str)
        """

        if None in (slicenum, owner, project, stack, neighbours):
            raise PreventUpdate

        if 'None' in (owner, project, stack):
            raise PreventUpdate

        thispage = thispage.lstrip('/')

        if thispage not in hf.trigger(key='module'):
            raise PreventUpdate

        ol = dash.callback_context.outputs_list
        tileim_index = ol[0]['id']['component'].split('_')[-1]

        url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project \
              + '/stack/' + stack
        url += '/tileIds?matchPattern='

        if owner in params.slicenumformat.keys():
            url += params.slicenumformat[owner] % slicenum

        tiles = requests.get(url).json()

        if tiles == []:
            raise PreventUpdate

        t_labels = tiles.copy()
        tile = tiles[int(len(tiles) / 2 + int(tileim_index)) - 1]

        if prev_tile is None:
            prev_tile = tile

        if lead_tile in (None, {}, ''):
            lead_tile = dict(tile=prev_tile)

        if 'stack' not in lead_tile.keys() or lead_tile['stack'] != stack:
            lead_tile = dict(tile=prev_tile, stack=stack)

        lead_tile['slice'] = slicenum

        if neighbours == 'True' and tileim_index != '0' and tilepairdir not in ('', None):

            tp_jsonfiles = hf.jsonfiles(tilepairdir)
            if 'tile' in lead_tile.keys():
                tiles, slices, positions = hf.neighbours_from_json(tp_jsonfiles, lead_tile['tile'])
                t_labels = tiles.copy()

                if tiles == []:
                    raise PreventUpdate

                tile = tiles[-1]

            if owner in params.tile_display.keys() and len(slices) == len(t_labels):
                t_labels, tile0 = params.tile_display[owner](tiles, prev_tile, slicenum)

                for t_idx, label in enumerate(t_labels):
                    if len(slices) > 1:
                        slicestr = 'Slice ' + str(slices[t_idx]) + ' - '
                    else:
                        slicestr = ''

                    t_labels[t_idx] = slicestr + label

            for t_idx, label in enumerate(t_labels):
                t_labels[t_idx] = t_labels[t_idx] + ' ' + positions[t_idx]

        elif owner in params.tile_display.keys():
            t_labels, tile = params.tile_display[owner](tiles, prev_tile, slicenum)

        if None in (t_labels, tile):
            raise PreventUpdate

        # assemble dropdown
        dd_options = list(dict())
        for t_idx, item in enumerate(tiles):
            dd_options.append({'label': t_labels[t_idx], 'value': item})

        if tileim_index == '0' and lead_tile['tile'] in tiles:
            tile = lead_tile['tile']

        return dd_options, tile


    @callback([Output({'component': 'tileim_imurl' + idx_str, 'module': MATCH}, 'children'),
               Output({'component': 'tileim_link' + idx_str, 'module': MATCH}, 'children'),
               Output({'component': 'lead_tile' + idx_str, 'module': MATCH}, 'data')],
              [Input({'component': 'tile_dd' + idx_str, 'module': MATCH}, 'value'),
               Input({'component': 'store_render_launch', 'module': MATCH}, 'data')],
              [State({'component': 'owner_dd', 'module': MATCH}, 'value'),
               State({'component': 'project_dd', 'module': MATCH}, 'value'),
               State({'component': 'stack_dd', 'module': MATCH}, 'value'),
               State({'component': 'tileim_section_in' + idx_str, 'module': MATCH}, 'value'),
               State({'component': 'lead_tile' + idx_str, 'module': MATCH}, 'data'),
               State('url', 'pathname')
               ], prevent_initial_call=True)
    def im_view_url(tile, runstore, owner, project, stack, section, lead_tile, thispage):
        """
        Generates the link to the tile image to display.

        :param str tile: value of tile dropdown "tile_dd"  <b>&#8592; slicetotiles</b>
        :param dict runstore: data of "store_render_launch"
        :param str owner:
        :param str project:
        :param str stack:
        :param int section: value of the slice selector "tileim_section_in"
        :param str thispage: current page URL
        :return: "tileim_imurl" - str pointing to the tile image to fetch <Br>
                 "tileim_link" - str link to the tile specs for further use (MatchTrial)<Br>
                 "lead_tile" - dict Store data to determine lead tile (if index 0)
        :rtype: (str,str,dict)
        """

        if not dash.callback_context.triggered:
            raise PreventUpdate
        # print('tile is now: '+ tile)
        # print('stack is now: '+ stack)

        thispage = thispage.lstrip('/')

        if thispage not in hf.trigger(key='module'):
            raise PreventUpdate

        if None in (tile, runstore, owner, project, stack):
            raise PreventUpdate

        if 'None' in (owner, project, stack):
            raise PreventUpdate

        url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project \
              + '/stack/' + stack
        url += '/tile/' + tile

        url1 = url + '/render-parameters'

        try:
            tilespec = requests.get(url1).json()
        except:
            raise PreventUpdate

        scale = float(params.im_width) / float(tilespec['width'])

        out_scale = '%0.2f' % scale

        imurl = url + '/jpeg-image?scale=' + out_scale

        if runstore is None or 'mt_params' not in runstore.keys():
            scale1 = params.default_tile_scale
        else:
            scale1 = runstore['mt_params']['scale']

        if 'FIBSEM' in owner:
            filter= 'false'
        else:
            filter = 'true'

        url1 += '?filter=' + filter

        normalize = False

        if 'normalize' in lead_tile.keys():
            normalize = lead_tile['normalize']
            url1 += '&normalizeForMatching=true'

        url1 += '&scale=' + str(scale1)

        leadtile = dict(tile=tile, section=section, stack=stack, normalize=normalize)

        return imurl, url1, leadtile

    # init tile image display
    @callback(Output({'component': 'tileim_image' + idx_str, 'module': MATCH}, 'src'),
              [Input({'component': 'tileim_contrastslider' + idx_str, 'module': MATCH}, 'value'),
               Input({'component': 'tileim_imurl' + idx_str, 'module': MATCH}, 'children')],
              [State({'component': 'lead_tile' + idx_str, 'module': MATCH}, 'data'),
               State('url', 'pathname')]
              )
    def im_view(c_limits, imurl, lead_tile, thispage):
        """
        Generate the tile view.

        :param list of int c_limits: Contrast slider values "tileim_contrastslider"
        :param str imurl: initial tile image URL "tileim_imurl" <b>&#8592; im_view_url</b>
        :param str thispage: current page URL
        :param dict lead_tile: Store dict containing the "normalize" switch
        :return: Final URL to the Render image-API "tileim_image" <i>src</i>
        :rtype: str
        """
        if not dash.callback_context.triggered:
            raise PreventUpdate

        thispage = thispage.lstrip('/')

        if thispage not in hf.trigger(key='module'):
            raise PreventUpdate

        if None in (c_limits, imurl):
            raise PreventUpdate

        if 'None' in (c_limits, imurl):
            raise PreventUpdate

        normstr = ''

        if type(lead_tile) is dict:
            if 'normalize' in lead_tile.keys():
                if lead_tile['normalize']:
                    normstr = '&normalizeForMatching=true'

        imurl += '&minIntensity=' + str(c_limits[0]) + '&maxIntensity=' + str(c_limits[1]) + normstr

        return imurl

    # init slice image display
    @callback([Output({'component': 'sliceim_image' + idx_str, 'module': MATCH}, 'figure'),
               Output({'component': 'sliceim_image' + idx_str, 'module': MATCH}, 'config'),
               Output({'component': 'sliceim_params' + idx_str, 'module': MATCH}, 'data'),
               Output({'component': 'sliceim_image' + idx_str, 'module': MATCH}, "relayoutData")],
              [Input({'component': 'sliceim_section_in' + idx_str, 'module': MATCH}, 'value'),
               Input({'component': 'slice_zoom', 'module': MATCH}, 'n_clicks'),
               Input({'component': 'slice_reset', 'module': MATCH}, 'n_clicks'),
               Input({'component': 'sliceim_contrastslider' + idx_str, 'module': MATCH}, 'value'),
               Input({'component': 'store_stackparams', 'module': MATCH}, 'data'),
               Input({'component': 'stack_dd', 'module': MATCH}, 'value')],
              [State({'component': 'owner_dd', 'module': MATCH}, 'value'),
               State({'component': 'project_dd', 'module': MATCH}, 'value'),
               State({'component': 'sliceim_params' + idx_str, 'module': MATCH}, 'data'),
               State({'component': 'sliceim_rectsel' + idx_str, 'module': MATCH}, 'data'),
               State('url', 'pathname')
               ], prevent_initial_call=True)
    def slice_view(section, zoomclick, resetclick, c_limits, thisstore, stack, owner, project, imparams,
                   rectsel, thispage):
        """
        Generates/populates the slice viewer.

        :param int section: value of the slice selector "sliceim_section_in"
        :param int zoomclick: "slice_zoom" button click trigger
        :param int resetclick: "slice_reset" button click trigger
        :param list of int c_limits: Contrast slider values "sliceim_contrastslider"
        :param dict thisstore: data of "store_stackparams"
        :param str owner:
        :param str project:
        :param str stack:
        :param dict imparams: previous state of data "sliceim_params"
        :param dict rectsel: rectangular selection from annotation <b>&#8592; paramstoouterlimits</b>
        :param str thispage: current page URL
        :return: "sliceim_image" <i>figure</i> figure element to draw <Br>
                 "sliceim_image" <i>config</i> plotly figure config <Br>
                 "sliceim_params" - parameters to describe the current slice image <Br>
                 "sliceim_image" <i>relayoutData</i>  annotations on top of the figure

        :rtype: (array, dict, dict, dict)
        """
        if not dash.callback_context.triggered:
            raise PreventUpdate

        trigger = hf.trigger()

        thispage = thispage.lstrip('/')

        if thispage == '' or thispage not in hf.trigger(key='module'):
            raise PreventUpdate

        if None in (section, owner, project, stack):
            raise PreventUpdate

        if 'None' in (owner, project, stack):
            raise PreventUpdate

        scale = imparams['scale']

        url = params.render_base_url + params.render_version + 'owner/' + owner + '/project/' + project \
              + '/stack/' + stack

        url += '/z/' + str(section)

        if 'imurl' not in imparams.keys():
            imparams['imurl'] = url + '/jpeg-image?scale=' + str(scale)

        if 'zoom' in trigger:
            if rectsel == {}:
                raise PreventUpdate

            xmin = rectsel['X'][0]
            ymin = rectsel['Y'][0]
            width = int(rectsel['X'][1] - rectsel['X'][0])
            height = int(rectsel['Y'][1] - rectsel['Y'][0])

            bounds = dict()
            bounds['minX'] = xmin
            bounds['minY'] = ymin
            bounds['maxX'] = rectsel['X'][1]
            bounds['maxY'] = rectsel['Y'][1]
            imparams.update(bounds)

            scale = float(params.im_width) / float(width)
            scale = round(scale, 4)
            out_scale = '%0.4f' % scale

            url += '/box/' + ','.join(map(str, [xmin, ymin, width, height, scale]))
            imurl = url + '/jpeg-image?scale=' + out_scale

        elif 'contrast' in trigger:
            imurl = imparams['imurl']

        elif 'section' in trigger:
            imurl = re.sub('/z/[0-9]*', '/z/' + str(section), imparams['imurl'])

        else:
            fullbounds = thisstore['stackparams']['stats']['stackBounds']
            url1 = url + '/bounds'

            bounds = requests.get(url1).json()

            imwidth = bounds['maxX'] - bounds['minX']

            scale = float(params.im_width) / float(imwidth)
            imparams.update(fullbounds)
            imparams['slicebounds'] = bounds
            imparams['fullbounds'] = fullbounds
            imparams['maxZ'] = fullbounds['maxZ']
            imparams['minZ'] = fullbounds['minZ']

            scale = round(scale, 4)
            out_scale = '%0.4f' % scale
            imurl = url + '/jpeg-image?scale=' + out_scale

        imparams['scale'] = scale

        imparams['imurl'] = imurl

        imurl += '&minIntensity=' + str(c_limits[0]) + '&maxIntensity=' + str(c_limits[1])

        try:
            img = io.imread(imurl)
        except:
            fig = px.line()
            fig.update_xaxes(showticklabels=False, showgrid=False)
            fig.update_yaxes(showticklabels=False, showgrid=False)
            fig.add_annotation(x=2, y=2,
                               text="Stack or slice cannot be found...")

            return fig, {}, imparams, None

        fig = px.imshow(img, binary_string=True)
        fig.update_layout(dragmode="drawrect")
        fig.update_layout(coloraxis_showscale=False)
        fig.update_layout(newshape=dict(opacity=0.3, fillcolor='#EB9', line=dict(color='#053')))
        fig.update_layout(height=params.im_width, margin=dict(l=0, r=0, b=0, t=0))
        fig.update_xaxes(showticklabels=False, showgrid=False)
        fig.update_yaxes(showticklabels=False, showgrid=False)

        config = {'responsive': False,
                  'displaylogo': False,
                  'modeBarButtons': [['drawrect', 'eraseshape']],
                  'showAxisDragHandles': False

                  }
        return fig, config, imparams, None


    @callback(Output({'component': 'sliceim_rectsel' + idx_str, 'module': MATCH}, 'data'),
              Input({'component': 'sliceim_image' + idx_str, 'module': MATCH}, "relayoutData"),
              [State({'component': 'sliceim_params' + idx_str, 'module': MATCH}, 'data'),
               State({'component': 'sliceim_details' + idx_str, 'module': MATCH}, 'open'),
               State({'component': 'sliceim_details' + idx_str, 'module': MATCH}, 'nclicks')],
              )
    def paramstoouterlimits(annotations, imparams, open, click):
        """
        Generates the bounding box values from the image annotation rectangle(s).

        :param dict annotations: <i>relayoutData</i> from "sliceim_image" containing the annotation regions
        :param dict imparams: "sliceim_params" <b>&#8592; slice_view</b>
        :return: "sliceim_rectsel" bounding box values
        :rtype: dict
        """
        if not dash.callback_context.triggered:
            raise PreventUpdate

        if 'minX' not in imparams.keys():
            raise PreventUpdate

        outdims = dict()
        scale = imparams['scale']

        for dim in ['X', 'Y']:
            minval = imparams['min' + dim]
            maxval = imparams['max' + dim]

            # adjust rectangle position in case slice does not cover full volume bounds
            if imparams['min' + dim] == imparams['fullbounds']['min' + dim]:
                minval_im = imparams['slicebounds']['min' + dim]
                # maxval_im = imparams['slicebounds']['max' + dim]
            else:
                minval_im = imparams['min' + dim]
                # maxval_im = imparams['max' + dim]

            if annotations in ([], None):
                outdims[dim] = [minval, maxval]
            else:
                if "shapes" in annotations:
                    if annotations["shapes"] == []:
                        minv = 0
                        maxv = maxval - minval
                        scale = 1
                    else:
                        last_shape = annotations["shapes"][-1]
                        minv = int(last_shape[dim.lower() + '0'])
                        maxv = int(last_shape[dim.lower() + '1'])

                elif any(["shapes" in key for key in annotations]):
                    minv = int([annotations[key] for key in annotations if dim.lower() + '0' in key][0])
                    maxv = int([annotations[key] for key in annotations if dim.lower() + '1' in key][0])

                else:
                    minv = 0
                    maxv = maxval - minval
                    scale = 1

                if minv > maxv:
                    minv, maxv = maxv, minv

                minval, maxval = int(minv / scale + minval_im), int(maxv / scale + minval_im)

                outdims[dim] = [minval, maxval].copy()

        return (outdims)


@callback(Output({'component': 'lead_tile', 'module': MATCH}, 'data'),
          Input({'component': 'lead_tile_0', 'module': MATCH}, 'data'))
def collect_leadtiles(lead_in):
    # print(lead_in)
    return lead_in
