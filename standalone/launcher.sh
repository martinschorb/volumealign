#!/bin/bash

source ./dash/utils/setup_py_environment.sh

echo "Launching Render standalone processing script on " `hostname`

echo python $rendermodules$1 --input_json $2

python $rendermodules$1 --input_json $2
