#!/bin/bash

conda_init="/g/emcf/software/python/miniconda/etc/profile.d/conda.sh"

source $conda_init
conda init bash > /dev/null

conda activate render
# echo render environment activated


# path do excecutables and python client scripts

export rendermodules="/g/emcf/schorb/code/render-modules/"
export hotknife="/g/emcf/schorb/code/hot-knife/"
