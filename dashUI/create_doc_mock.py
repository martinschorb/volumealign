#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 15:26:45 2020

@author: schorb

This script auto-generates a list of imported Python modules for all code files in the source directory.
These are then set to be treated as mock for generating an automated documentation.


"""


import findimports
import glob
import sys
from unittest.mock import MagicMock as mock

src_dir = 'dashUI'


flist = glob.glob(src_dir+'/**/*.py',recursive=True)

imp_list=['unittest.mock.MagicMock','sys']

for cfile in flist:
    c_imps = findimports.find_imports(cfile)

    for imp in c_imps:
        if imp.name not in imp_list:
            imp_list.append(imp.name)
            sys.modules[imp.name] = mock()
