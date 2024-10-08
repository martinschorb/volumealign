#!/bin/bash

# Launcher for Spark on SLURM

template="./spark_slurm_template.sh"
runscript="./test.sh"

#Default values

MASTER_MEM="2"
MASTER_CPU="1"
TIME="00:10:00"
WORKER_NODES="1"
WORKER_CPU="1"
WORKER_MEMPERCPU="4"
EMAIL=`whoami`'@domain'
LOGDIR=`pwd`
LOGFILE=sparkslurm-%j.out
ERRFILE=sparkslurm-%j.err
# PARSE COMMAND LINE ARGUMENTS

while [ "$1" != "" ]; do
    PARAM=`echo $1 | awk -F= '{print $1}'`
    VALUE=`echo $1 | awk -F= '{print $2}'`
    case $PARAM in
        --runscript)
            runscript=$VALUE
            shift
            ;;
        --template)
            template=$VALUE
            shift
            ;;
        --email)
            EMAIL=$VALUE
            shift
            ;;
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
        --logdir)
	          LOGDIR=$VALUE
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
     | sed "s/<SoS_MASTER_MEM>/${MASTER_MEM}G/" \
     | sed "s/<SoS_MASTER_CPU>/${MASTER_CPU}/" \
     | sed "s/<SoS_TIME>/${TIME}/" \
     | sed "s/<SoS_WORKER_NODES>/${WORKER_NODES}/" \
     | sed "s/<SoS_WORKER_MEMPERCPU>/${WORKER_MEMPERCPU}G/" \
     | sed "s/<SoS_EMAIL>/$EMAIL/" \
     | sed "s/<SoS_WORKER_CPU>/$WORKER_CPU/" \
     | sed "s#<SoS_LOGFILE>#$LOGFILE#" \
     | sed "s#<SoS_ERRFILE>#$ERRFILE#" \
    > $runscript

chmod +x $runscript

mkdir $LOGDIR
cd $LOGDIR

# call the submission

echo $runscript $PARAMS > $LOGFILE

sbatch $runscript $PARAMS
