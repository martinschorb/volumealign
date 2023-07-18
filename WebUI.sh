#!/bin/bash

scriptpath=$(dirname "$0")               # relative path
scriptpath=$(cd "$scriptpath" && pwd)    # absolute and normalized path
if [[ -z "$scriptpath" ]] ; then
  exit 1
fi

cd "$scriptpath"

cstring=$(cat ./dashUI/params.py | grep conda_dir)

export condapath=${cstring##*dir = }

condapath=${condapath#\'}
condapath=${condapath%\'}

eval "$($condapath/bin/conda shell.bash hook)"

conda activate dash-new

python -u dashUI/start_webUI.py

