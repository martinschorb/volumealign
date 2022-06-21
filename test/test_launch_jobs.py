#!/usr/bin/env python
'''
tests for functionality in dashUI.utils.launch_jobs
'''

import os
import pytest
import time
from dashUI.utils.launch_jobs import *

run_state0 = dict(status='',
                  type='standalone',
                  logfile='log.log',
                  id=0)

# test conversion of argstrings
def test_args2string():
    # test Type Error
    with pytest.raises(TypeError):
        # number
        args2string(5)
        # module
        args2string(os)

    inlist = [1, 'a', 'f']
    expectedargs = ' 1 a f '

    assert args2string(inlist) == expectedargs

    indict = {'arg1': 5, 'arg2': 'content', 'arg3': [1, 2, 3]}
    expectedargs = ' arg1=5 arg2=content arg3=1 arg3=2 arg3=3 '

    assert args2string(indict) == expectedargs


# test launcher
def test_run():
    # run launcher test

    rs1 = dict(run_state0)
    rs1['id'] = run()
    rs1['status'] = 'launch'

    time.sleep(5)
    assert status(rs1)[0] == 'running'

    time.sleep(35)
    assert status(rs1)[0] == 'done'

    # check wrong script
    rs1['status'] = 'launch'
    rs1['logfile'] = os.path.join(params.render_log_dir, 'tests', 'test_render.log')
    rs1['id'] = run(pyscript='/thisscriptclearlydoesnotexist',logfile=rs1['logfile'])
    time.sleep(5)
    assert status(rs1)[0] == 'Error while excecuting ' + str(rs1['id']) + '.'



# test status of local tasks
def test_find_activejob():

    rs1 = dict(run_state0)
    rs1['id'] = {'par':[1,2,3,4]}
    rs1['status'] = 'launch'

    # check for sequential jobs
    with pytest.raises(TypeError):
        find_activejob(rs1)

    rs1['id'] = run()





