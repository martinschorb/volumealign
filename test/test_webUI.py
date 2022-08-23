#!/usr/bin/env python
'''
tests the Web UI launcher
'''

import os
import subprocess
import time
import json
import requests

import pytest

from dashUI import params
from dashUI.start_webUI import prefix


@pytest.fixture(scope='session')
def startup_webui():
    outfile = os.path.join(params.base_dir,'test','webui_temp.out')

    p = subprocess.Popen(os.path.join(params.base_dir, 'WebUI.sh'), stdout=open(outfile, 'w'))

    # check for regular running
    time.sleep(4)

    assert p.errors is None

    assert p.returncode is None
    assert os.path.exists(outfile)

    yield outfile

    os.system('kill $(echo $(ps x -o "pid command" | grep "dashUI/app" |grep "sh -c python") | cut -d " " -f 1)')
    os.system('kill $(echo $(ps x -o "pid command" | grep "dashUI/app" |grep "python") | cut -d " " -f 1)')
    os.system('rm ' + outfile)


@pytest.mark.dependency()
def test_webUI(startup_webui):

    expected_stdout = "Starting Render WebUI.\n\nAs long as this window is open, you can access Render through:"
    assert os.path.exists(startup_webui)

    with open(startup_webui,'r') as outfile:
        stdout = outfile.read()

    assert stdout.startswith(expected_stdout)

    assert params.hostname in stdout

    port = stdout[stdout.find(params.hostname)+len(params.hostname)+1 : stdout.rfind('\n\n\n')]

    if os.path.exists(os.path.join(params.base_dir, 'dashUI', 'web_users.json')):
        with open(os.path.join(params.base_dir, 'dashUI', 'web_users.json')) as f:
            users = json.load(f)
        assert params.user in users.keys()
        expectedport = users[params.user]
    else:
        expectedport = 8050

    assert port == str(expectedport)

    response = requests.get(prefix + 'localhost:' + port, verify=False)

    assert response.status_code == 200



