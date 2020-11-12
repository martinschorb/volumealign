#!/bin/bash

source ../dash/utils/setup_py_environment.sh

python $rendermodules --input_json $1
