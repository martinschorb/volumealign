#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:24:32 2020

@author: schorb
"""

import dash
import requests

import params

def mt_parameters(matchID):
    out_params = dict()
    
    url = params.render_base_url + params.render_version + 'owner/flyTEM/matchTrial/' + matchID
    
    matchtrial = requests.get(url).json()
    
    
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