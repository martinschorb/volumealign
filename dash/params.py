#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# dash volume EM interface global parameters:

import json   
import os 
    
refresh_interval = 1000   # ms
disp_lines = 50          # output lines to display

json_template_dir = '/Volumes/emcf/schorb/code/JSON_parameters/templates'

v_base_url = '/render-ws/'
render_version = 'v1/'


# Choose Render parameters
with open(os.path.join(json_template_dir,'render.json'),'r') as f:
    render_json = json.load(f)


render_base_url = 'http://' + render_json['render']['host']
render_base_url += ':' + str(render_json['render']['port'])
render_base_url += v_base_url
