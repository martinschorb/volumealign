#!/bin/bash

source /g/emcf/schorb/code/volumealign/dash/utils/setup_py_environment.sh

echo "Launching Render standalone processing script on " `hostname` ". Slurm job ID: " $SLURM_JOBID".

echo python $rendermodules$1 --input_json $2

python $rendermodules$1 --input_json $2
