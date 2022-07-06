#!/usr/bin/env python
'''
tests for functionality in dashUI.utils.launch_jobs
'''

import os
import pytest
import time
from dashUI.utils.launch_jobs import *

run_state0 = dict(status='running',
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


# test launcher and status calls
def test_run():
    # run launcher test

    rs1 = dict(run_state0)

    # check wrong compute target type
    with pytest.raises(TypeError):
        run(target=123)

    # check target not implemented
    with pytest.raises(NotImplementedError):
        run(target='somefancycloudthatdoesnotexits')

    # test wrong compute target type check
    rs1['id'] = ['this is an invalid jobID']
    with pytest.raises(TypeError):
        checkstatus(rs1)

    c_options = params.comp_options
    c_options.append({'label':'Dummy remote launch and status.','value':'localhost'})

    # check all available target types
    for computeoption in c_options:

        target = computeoption['value']

        print('Testing ' + computeoption['label'] + '.')

        rs1['type'] = target

        if not 'spark' in target:
            # check wrong script
            rs1['status'] = 'launch'
            rs1['logfile'] = os.path.join(params.render_log_dir, 'tests', 'test_render_wrongscript.log')
            rs1['id'] = run(pyscript='/thisscriptclearlydoesnotexist', logfile=rs1['logfile'], target=target)
            time.sleep(5)

            print(rs1)

            while status(rs1)[0] == 'pending':
                print('Wait for test job to start on ' + computeoption['label'] + '.')
                time.sleep(10)

            assert status(rs1)[0] == 'Error while excecuting ' + str(rs1['id']) + '.'

            # check successful run of test script
            rs1['status'] = 'launch'
            rs1['logfile'] = os.path.join(params.render_log_dir, 'tests', 'test_render_run.log')
            rs1['id'] = run(logfile=rs1['logfile'], target=target)

            time.sleep(5)

            while status(rs1)[0] == 'pending':
                print('Wait for test job to start on ' + computeoption['label'] + '.')
                time.sleep(10)

            assert status(rs1)[0] == 'running'

            time.sleep(35)
            assert status(rs1)[0] == 'done'

def test_canceljobs():

    rs1 = dict(run_state0)

    c_options = params.comp_clustertypes

    # check all available target types
    for computeoption in c_options:

        target = computeoption['value']

        print('Testing cancel' + computeoption['label'] + '.')

        rs1['type'] = target

        rs1['status'] = 'launch'
        rs1['logfile'] = os.path.join(params.render_log_dir, 'tests', 'test_render_cancel.log')
        rs1['id'] = run(logfile=rs1['logfile'], target=target)

        time.sleep(3)

        canceljobs(rs1)

        time.sleep(3)

        assert str(rs1['id']) + ' cancelled.' in status(rs1)[0]

def test_localsparkjobs():
    rs1 = dict(run_state0)

    c_options = params.comp_options
    c_options.append({'label':'Dummy remote launch and status.','value':'localhost'})

    # check all available target types
    for computeoption in c_options:
        if 'spark' in target:
            target = computeoption['value']

            print('Testing ' + computeoption['label'] + '.')

            rs1['type'] = target
            rs1['status'] = 'launch'
            rs1['logfile'] = os.path.join(params.render_log_dir, 'tests', 'test_localspark.log')

            spark_args = {'--jarfile': params.render_sparkjar}

            spark_args['--cpu'] = remote_params(target.split('::')[-1])['cpu']
            spark_args['--mem'] = remote_params(target.split('::')[-1])['mem']

            rs1['id'] = run(pyscript='org.janelia.render.client.spark.n5.N5Client',
                            logfile=rs1['logfile'],
                            target=target,
                            special_args=spark_args,
                            )
            time.sleep(5)

            print(rs1)

    assert True

# test status of local tasks
def test_find_activejob():
    rs1 = dict(run_state0)
    rs1['id'] = {'par': [1, 2, 3, 4]}
    rs1['status'] = 'launch'

    # check for sequential jobs
    with pytest.raises(TypeError):
        find_activejob(rs1)

    rs1['id'] = run()
