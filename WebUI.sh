#!/bin/bash

eval "$(/g/emcf/software/python/miniconda/bin/conda shell.bash hook)"
conda activate dash-new

dashpath=/g/emcf/software/volumealign

cd $dashpath

python dashUI/start_webUI.py
