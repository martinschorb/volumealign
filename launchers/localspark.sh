#!/bin/bash

# Launcher for local Spark


# PARSE COMMAND LINE ARGUMENTS

while [ "$1" != "" ]; do
    PARAM=$(echo "$1" | awk -F= '{print $1}')
    VALUE=$(echo "$1" | awk -F= '{print $2}')
    case $PARAM in
        --cpu)
            WORKER_CPU=$VALUE
            shift
            ;;
        --mem)
            SPARK_MEM=$VALUE
            shift
            ;;
        --scriptparams)
            shift
            PARAMS=$@
            break
            ;;
        --java_home)
            JAVA_HOME=$VALUE
            shift
            ;;
        --render_dir)
            RENDER_DIR=$VALUE
            shift
            ;;
        --class)
            CLASS=$VALUE
            shift
            ;;
        --jarfile)
            JARFILE=$VALUE
            shift
            ;;
        --spark_home)
            SPARK_HOME=$VALUE
            shift
            ;;
        --params)
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


export DISPLAY=""

if [ -z "$JAVA_HOME" ] ; then
  export JAVA_HOME=$(readlink -m "$RENDER_DIR"/deploy/*jdk*)
fi

export MASTER_URL="local[$WORKER_CPU]"

# MAIN CALLS
#======================================

sparksubmitcall="$SPARK_HOME/bin/spark-submit --master $MASTER_URL --conf spark.default.parallelism=$WORKER_CPU --conf spark.executor.cores=$WORKER_CPU --executor-memory $SPARK_MEM --class $CLASS $JARFILE $PARAMS"

echo "$sparksubmitcall"
$sparksubmitcall
