#!/bin/bash

if [[ $# -lt 2 ]]; then
    echo "Need to provide script and variable"
    echo "Usage: $0 PYTHONSCRIPT VARIABLE_NAME"
    exit 1
fi

case "$1" in
  -h | --help)
    echo "Returns a string representation of a variable definition from a Python script."
    echo "Usage: $0 PYTHONSCRIPT VARIABLE_NAME"
    exit 0
    ;;
esac

if [[ ! -r $1 ]]; then
    echo "Not a readable script file"
    echo "Usage: $0 PYTHONSCRIPT VARIABLE_NAME"
    exit 1
fi


# extract

instring=`cat $1 | grep $2`

if [[ -z $instring ]]; then
  echo "no match"
  echo "Usage: $0 PYTHONSCRIPT VARIABLE_NAME"
  exit 1
fi

pystring=`echo $instring | tr -d \'\""\\ "`

outstring=${pystring#*=}

echo $outstring
