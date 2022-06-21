#!/usr/bin/env python
'''
tests for functionality in dashUI.utils.launch_jobs
'''

import os
import pytest
from dashUI.utils.launch_jobs import *


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


# test status of local tasks
def test_status():
