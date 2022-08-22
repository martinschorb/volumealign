#!/bin/bash

scriptpath=$(dirname "$0")               # relative path
scriptpath=$(cd "$scriptpath" && pwd)    # absolute and normalized path
if [[ -z "$scriptpath" ]] ; then
  exit 1
fi

cd "$scriptpath"

condapath=$(conda info --base)

eval "$($condapath/bin/conda shell.bash hook)"

conda activate dash-new

python dashUI/start_webUI.py
