#!/bin/bash
#SBATCH --job-name=spark-master      # create a short name for your job
#SBATCH --time=<SoS_TIME>         # total run time limit (HH:MM:SS)
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=<SoS_EMAIL>
#SBATCH -o <SoS_LOGFILE>
#SBATCH -e <SoS_ERRFILE>
# #  --- Master resources ---
#SBATCH --mem-per-cpu=<SoS_MASTER_MEM>
#SBATCH --cpus-per-task=<SoS_MASTER_CPU>
#SBATCH --ntasks-per-node=1
# # --- Worker resources ---
#SBATCH hetjob
#SBATCH --job-name spark-worker
#SBATCH --nodes=<SoS_WORKER_NODES>
#SBATCH --mem-per-cpu=<SoS_WORKER_MEMPERCPU>
#SBATCH --cpus-per-task=<SoS_WORKER_CPU>
#SBATCH --ntasks-per-node=1

# import Parameters


export DISPLAY=""
export LOGDIR=`pwd`

# PARSE COMMAND LINE ARGUMENTS

while [ "$1" != "" ]; do
    PARAM=`echo $1 | awk -F= '{print $1}'`
    VALUE=`echo $1 | awk -F= '{print $2}'`
    case $PARAM in
        --java_home)
            JAVA_HOME=$VALUE
            shift
            ;;
        --render_dir)
            RENDER_DIR=$VALUE
            shift
            ;;
        --logdir)
            LOGDIR=$VALUE
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
            exit 1
            ;;
    esac
done


if [ -z $JAVA_HOME ] ; then
  export JAVA_HOME=`readlink -m $RENDER_DIR/deploy/*jdk*`
fi

# CLEAN LOGDIR
shopt -s globstar
rm -f $LOGDIR/../**/worker/**/*.jar 2> /dev/null

JOB="$SLURM_JOB_NAME-$SLURM_JOB_ID"
export MASTER_URL="spark://$(hostname):7077"
export MASTER_HOST=`hostname`
export MASTER_IP=`host $MASTER_HOST | sed 's/^.*address //'`
export MASTER_WEB="http://$MASTER_IP:8080"

#JARFILE=$RENDER_DIR"/render-ws-spark-client/target/render-ws-spark-client-3.0.0-SNAPSHOT-standalone.jar"

mkdir $LOGDIR
mkdir $LOGDIR/$JOB

# SET UP ENV for the spark run

echo $MASTER_IP > $LOGDIR/$JOB/master

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

# wait for master to start

wait=1

while [ $wait -gt 0 ]
  do
    { # try
      curl "$MASTER_WEB" > /dev/null && wait=0 && echo "Found spark master, will submit tasks."
    } || { # catch
      sleep 10 && echo "Waiting for spark master to become available."
    }
  done

#echo Starting slaves
srun --het-group=1 $SPARK_HOME/bin/spark-class org.apache.spark.deploy.worker.Worker $MASTER_URL -d $SPARK_WORKER_DIR &

# again, sleep a tiny little bit
sleep 5s


sparksubmitcall="$SPARK_HOME/bin/spark-submit --master $MASTER_URL --driver-memory 2g --conf spark.default.parallelism=$TOTAL_CORES --conf spark.executor.cores=$SPARK_WORKER_CORES --executor-memory $SPARK_MEM --class $CLASS $JARFILE $PARAMS"

echo $sparksubmitcall
$sparksubmitcall

while [ ! -f $LOGDIR.log.done ]
do
  sleep 5s
done

#rm $LOGDIR.log.done

#sleep infinity
