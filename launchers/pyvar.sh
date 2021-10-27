#!/bin/bash
#
# Extracts the string representation of a variable define in a Python script
# returns it to the stdout.
# If multiple variables or declaration statements are found, the last match will be used.




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

# choose last match 
instring=${instring##*$2}

# clean string delimiters and white spaces
pystring=`echo $instring | tr -d \'\""\\ "`

# split string to remove the variable declaration
outstring=${pystring#*=}

echo $outstring
