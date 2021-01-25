#!/bin/bash

# Launcher for Spark on SLURM

template="/g/emcf/schorb/code/volumealign/spark_slurm_template.sh"
runscript="/g/emcf/software/render-logs/runscripts/slurm-spark_test.sh"

#Default values

MASTER_MEM="1"
MASTER_CPU="1"
TIME="00:10:00"
WORKER_NODES="1"
WORKER_CPU="1"
WORKER_MEMPERCPU="4"
EMAIL=`whoami`"@embl.de"
LOGFILE=slurm-%j.out
ERRFILE=slurm-%j.err
# PARSE COMMAND LINE ARGUMENTS

while [ "$1" != "" ]; do
    PARAM=`echo $1 | awk -F= '{print $1}'`
    VALUE=`echo $1 | awk -F= '{print $2}'`
    case $PARAM in
        --master_mem)
            MASTER_MEM=$VALUE
            shift
            ;;
        --master_cpu)
            MASTER_CPU=$VALUE
            shift
            ;;
        --time)
            TIME=$VALUE
            shift
            ;;
        --worker_nodes)
            WORKER_NODES=$VALUE
            shift
            ;;
        --worker_cpu)
            WORKER_CPU=$VALUE
            shift
            ;;
        --worker_mempercpu)
            WORKER_MEMPERCPU=$VALUE
            shift
            ;;
        --worker_mempercpu)
            runscript=$VALUE
            shift
            ;;
        --logfile)
            LOGFILE=$VALUE
            shift
            ;;
        --errfile)
            ERRFILE=$VALUE
            shift
            ;;
        --scriptparams)
            shift
            PARAMS=$@
            break
            ;;
        *)
            echo "ERROR: unknown parameter \"$PARAM\""
            usage
            exit 1
            ;;
    esac
done


# Build SLURM submission script

cat "${template}" \
     | sed "s/<SoS_MASTER_MEM>/${MASTER_MEM}G/g" \
     | sed "s/<SoS_MASTER_CPU>/${MASTER_CPU}/g" \
     | sed "s/<SoS_TIME>/${TIME}/g" \
     | sed "s/<SoS_WORKER_NODES>/${WORKER_NODES}/g" \
     | sed "s/<SoS_WORKER_MEMPERCPU>/${WORKER_MEMPERCPU}G/g" \
     | sed "s/<SoS_EMAIL>/$EMAIL/g" \
     | sed "s/<SoS_WORKER_CPU>/$WORKER_CPU/g" \
     | sed "s/<SoS_LOGFILE>/$LOGFILE/g" \
     | sed "s/<SoS_ERRFILE>/$ERRFILE/g" \
    > $runscript

chmod +x $runscript

# call the submission

echo $runscript $PARAMS
sbatch $runscript $PARAMS
