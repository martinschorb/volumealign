#!/usr/bin/env python
'''
tests the Web UI launcher
'''

import os
from dashUI import params

dash_env = 'dash-new'

dashpath = params.base_dir

assert os.path.exists(dashpath)

