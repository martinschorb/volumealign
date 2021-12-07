#!/bin/bash

# Launcher for Spark on SLURM

runscript="./slurm-spark_test.sh"

# import Parameters

emaildomain=`../pyvar.sh ../../dash/params.py  email`
render_dir=`../pyvar.sh ../../dash/params.py  render_dir`


#Default values

MASTER_MEM="1"
MASTER_CPU="1"
TIME="00:10:00"
WORKER_NODES="1"
WORKER_CPU="1"
WORKER_MEMPERCPU="4"
EMAIL=`whoami`$emaildomain
LOGDIR=`pwd`
LOGFILE=sparkslurm-.out
ERRFILE=sparkslurm-.err
# PARSE COMMAND LINE ARGUMENTS

while [ "$1" != "" ]; do
    PARAM=`echo $1 | awk -F= '{print $1}'`
    VALUE=`echo $1 | awk -F= '{print $2}'`
    case $PARAM in
        --runscript)
            runscript=$VALUE
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
        --worker_mempercpu)
            runscript=$VALUE
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
        --java_home)
            JAVA_HOME=$VALUE
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



# Build SLURM submission script

mkdir $LOGDIR
cd $LOGDIR

export DISPLAY=""
export JAVA_HOME=`readlink -m $render_dir/deploy/jdk*`
export LOGDIR=`pwd`

# CLEAN LOGDIR

rm -f $LOGDIR/worker/*/*.jar

export SPARK_HOME=`../pyvar.sh ../../dash/params.py  spark_dir`
JOB="localspark"
export MASTER_URL="spark://$(hostname):7077"
export MASTER_WEB="http://$(hostname):8080"

CLASS="org.janelia.render.client.spark.SIFTPointMatchClient"
JARFILE="/g/emcf/software/render/render-ws-spark-client/target/render-ws-spark-client-2.3.1-SNAPSHOT-standalone.jar"
PARAMS="--baseDataUrl http://pc-emcf-16.embl.de:8080/render-ws/v1 --owner SBEM"

# PARSE COMMAND LINE ARGUMENTS

mkdir $LOGDIR/$JOB

# SET UP ENV for the spark run

echo $MASTER_WEB > $LOGDIR/$JOB/master

export SPARK_LOG_DIR="$LOGDIR/$JOB/logs"
export SPARK_WORKER_DIR="$LOGDIR/$JOB/worker"
export SPARK_LOCAL_DIRS="$TMPDIR/$JOB"


export SPARK_WORKER_CORES=$SLURM_CPUS_PER_TASK_HET_GROUP_1

export TOTAL_CORES=$(($SPARK_WORKER_CORES * $SLURM_JOB_NUM_NODES_HET_GROUP_1))

# export SPARK_DRIVER_MEM=$((4 * 1024))

export SPARK_MEM=$(( $SLURM_MEM_PER_CPU_HET_GROUP_1 * $SLURM_CPUS_PER_TASK_HET_GROUP_1))m
export SPARK_DAEMON_MEMORY=$SPARK_MEM
export SPARK_WORKER_MEMORY=$SPARK_MEM

# MAIN CALLS
#======================================



# start MASTER

$SPARK_HOME/sbin/start-master.sh

# sleep a tiny little bit to allow master to start
sleep 5s

#echo Starting slaves
$SPARK_HOME/bin/spark-class org.apache.spark.deploy.worker.Worker $MASTER_URL -d $SPARK_WORKER_DIR &

# again, sleep a tiny little bit
sleep 5s


sparksubmitcall="$SPARK_HOME/bin/spark-submit --master $MASTER_URL --driver-memory 2g --conf spark.default.parallelism=$TOTAL_CORES --conf spark.executor.cores=$SPARK_WORKER_CORES --executor-memory $SPARK_MEM --class $CLASS $JARFILE $PARAMS"

echo $sparksubmitcall
$sparksubmitcall

sleep infinity






# call the submission

# echo $runscript $PARAMS

sbatch $runscript $PARAMS
