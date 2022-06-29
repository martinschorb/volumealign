#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:24:32 2020

@author: schorb
"""
import json

import requests

import params


def mt_parameters(matchID, owner=params.mt_owner, raw=False):
    out_params = dict()
    if matchID is not None:
        url = params.render_base_url + params.render_version + 'owner/' + owner + '/matchTrial/' + matchID

        matchtrial = requests.get(url).json()

        if raw:
            return matchtrial

        out_params = matchtrial['parameters']['featureAndMatchParameters']

        out_params['scale'] = matchtrial['parameters']['pRenderParametersUrl'].partition('scale=')[2].partition('&')[0]

        # get processing time for one pair 

        timekeys = ['pFeatureDerivationMilliseconds',
                    'qFeatureDerivationMilliseconds',
                    'matchDerivationMilliseconds',
                    'matchQualityMilliseconds']

        out_params['ptime'] = 0

        for tk in timekeys:
            out_params['ptime'] += matchtrial['stats'][tk]

    return out_params


def new_matchtrial(matchID, urls, clippos='LEFT', owner=params.mt_owner, ):
    if not type(urls) is list:
        raise TypeError('URLs need to be provided as list.')

    if not len(urls) == 2:
        raise TypeError('URL list needs to be of length two.')

    matchtrial = mt_parameters(matchID, raw=True)

    matchtrial['matches'] = []
    matchtrial['stats'] = {}

    if clippos == 'NO CLIP':
        if 'pClipPosition' in matchtrial['parameters']['featureAndMatchParameters'].keys():
            matchtrial['parameters']['featureAndMatchParameters'].pop('pClipPosition')
            matchtrial['parameters']['featureAndMatchParameters'].pop('clipPixels')

    else:
        matchtrial['parameters']['featureAndMatchParameters']['pClipPosition'] = clippos
        if 'clipPixels' not in matchtrial['parameters']['featureAndMatchParameters'].keys():
            matchtrial['parameters']['featureAndMatchParameters']['clipPixels'] = 400

    matchtrial['parameters']['pRenderParametersUrl'] = urls[0]
    matchtrial['parameters']['qRenderParametersUrl'] = urls[1]

    # json.dump(matchtrial['parameters'],open('test.json','w'),indent=3)

    url = params.render_base_url + params.render_version + 'owner/' + owner + '/matchTrial/'

    res = {}

    # try:
    res = requests.post(url, json=matchtrial['parameters']).json()
    # except json.decoder.JSONDecodeError:
    #     print('Error while parsing MatchTrial')

    if 'id' in res.keys():
        matchtrial = res['parameters']
        matchID = res['id']

    return matchtrial, matchID


def invert_neighbour(tilelabel):
    o_loc = ['LEFT', 'RIGHT', 'TOP', 'BOTTOM']
    inv_loc = ['RIGHT', 'LEFT', 'BOTTOM', 'TOP']

    for p_loc, q_loc in zip(o_loc, inv_loc):
        if p_loc in tilelabel:
            return q_loc

    return 'NO CLIP'
