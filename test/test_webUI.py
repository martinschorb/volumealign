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


@pytest.mark.dependency(name='webUI', scope='session')
def test_webUI(startup_webui):
    if startup_webui == 'server is already running':
        return

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



