#!/bin/bash

source ./setup_gc3.sh
export PYTHONPATH=`pwd`

python ./grun.py $*
