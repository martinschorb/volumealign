#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""

import pytest
import os
import time
import subprocess

from dashUI import params

@pytest.fixture(scope='session')
def startup_webui():
    outfile = os.path.join(params.base_dir,'test','webui_temp.out')

    p = subprocess.Popen(os.path.join(params.base_dir, 'WebUI.sh'), stdout=open(outfile, 'w'))

    # check for regular running
    time.sleep(8)

    assert p.errors is None

    assert p.returncode is None
    assert os.path.exists(outfile)

    yield outfile

    os.system('kill $(echo $(ps x -o "pid command" | grep "dashUI/app" |grep "sh -c python") | cut -d " " -f 1)')
    os.system('kill $(echo $(ps x -o "pid command" | grep "dashUI/app" |grep "python") | cut -d " " -f 1)')
    os.system('rm ' + outfile)
