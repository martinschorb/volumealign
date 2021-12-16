#!/bin/bash

source ./setup_render.sh

echo "Launching Render standalone processing script on " `hostname`

echo python $rendermodules$1 --input_json $2

python $rendermodules$1 --input_json $2
