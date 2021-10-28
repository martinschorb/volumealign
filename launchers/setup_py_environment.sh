#!/bin/bash

conda_init=`./pyvar.sh ../dash/params.py  conda_dir`"/etc/profile.d/conda.sh"

source $conda_init
conda init bash > /dev/null

conda activate render

# echo render environment activated

# path to excecutables and python client scripts

rendermodules_dir=`./pyvar.sh ../dash/params.py  rendermodules_dir`

export rendermodules=$rendermodules_dir
