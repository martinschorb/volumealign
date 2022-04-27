#!/bin/bash

eval "$(/g/emcf/software/python/miniconda/bin/conda shell.bash hook)"
conda activate dash

dashpath=/g/emcf/software/volumealign/dashUI

cd $dashpath

python start_webUI.py
