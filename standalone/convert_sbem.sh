#!/bin/bash

source ../dash/utils/setup_py_environment.sh

python $rendermodules/rendermodules/dataimport/generate_EM_tilespecs_from_SBEMImage.py --input_json $1
