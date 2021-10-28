#!/bin/bash

source ./setup_py_environment.sh

echo "Launching Render standalone processing script on " `hostname`

sleep 25

echo hahahaha > /g/emcf/schorb/code/snakemake.txt

echo python $rendermodules$1 --input_json $2

#python $rendermodules$1 --input_json $2
