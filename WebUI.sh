#!/bin/bash

eval "$(/g/emcf/software/python/miniconda/bin/conda shell.bash hook)"
conda activate dash

dashpath=./dashUI

cd $dashpath

python start_webUI.py
