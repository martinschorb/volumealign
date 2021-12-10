 #!/bin/bash

export RUNDIR=$1

shift

cd $RUNDIR

source ./setup_render.sh

$*