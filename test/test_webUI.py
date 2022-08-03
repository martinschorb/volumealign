#!/usr/bin/env python
'''
tests the Web UI launcher
'''

import os
import subprocess
import time

from dashUI import params

dash_env = 'dash-new'

dashpath = params.base_dir

assert os.path.exists(dashpath)

expected_stdout = "Starting Render WebUI.\n\nAs long as this window is open, you can access Render through:"

p = subprocess.Popen('./WebUI.sh', stdout='webui_temp.out')

# check for regular running
time.sleep(5)

assert p.errors is None

assert p.returncode is None

with open('webui_temp.out','r') as outfile:
    stdout = outfile.read()

assert stdout.startswith(expected_stdout)

assert params.hostname in stdout

port = stdout[stdout.find(params.hostname)+len(params.hostname)+1 : stdout.rfind('\n\n\n')]


