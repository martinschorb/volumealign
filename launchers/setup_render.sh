#!/bin/bash

conda_init=`./pyvar.sh ../dash/params.py  conda_dir`"/etc/profile.d/conda.sh"

source $conda_init

conda init bash > /dev/null

conda activate `./pyvar.sh ../dash/params.py  render_envname`

source ./env_vars
