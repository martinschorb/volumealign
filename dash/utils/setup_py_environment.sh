#!/bin/bash

conda_init=`./utils/pyvar.sh ../params.py  conda_dir`"/etc/profile.d/conda.sh"

source $conda_init
conda init bash > /dev/null

conda activate render

# echo render environment activated


# path to excecutables and python client scripts

rendermodules_dir=`./utils/pyvar.sh ../params.py  rendermodules_dir`

# echo $rendermodules_dir

export rendermodules=$rendermodules_dir
