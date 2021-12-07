#!/bin/bash
#SBATCH --job-name=spark-master      # create a short name for your job
#SBATCH --time=<SoS_TIME>         # total run time limit (HH:MM:SS)
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=<SoS_EMAIL>
#SBATCH -o <SoS_LOGFILE>
#SBATCH -e <SoS_ERRFILE>
# #  --- Master resources ---
#SBATCH --nodes=1
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

render_dir=`../pyvar.sh ../../dash/params.py  render_dir`



export DISPLAY=""
export JAVA_HOME=`readlink -m $render_dir/deploy/jdk*`
export LOGDIR=`pwd`

# CLEAN LOGDIR

rm -f $LOGDIR/$SLURM_JOB_NAME-*/worker/*/*.jar

export SPARK_HOME=`../pyvar.sh ../../dash/params.py  spark_dir`
JOB="$SLURM_JOB_NAME-$SLURM_JOB_ID"
export MASTER_URL="spark://$(hostname):7077"
export MASTER_WEB="http://$(hostname):8080"

CLASS="org.janelia.render.client.spark.SIFTPointMatchClient"
JARFILE=$render_dir"/render-ws-spark-client/target/render-ws-spark-client-2.3.1-SNAPSHOT-standalone.jar"
PARAMS="--baseDataUrl http://render.embl.de:8080/render-ws/v1 --owner SBEM"

# PARSE COMMAND LINE ARGUMENTS

while [ "$1" != "" ]; do
    PARAM=`echo $1 | awk -F= '{print $1}'`
    VALUE=`echo $1 | awk -F= '{print $2}'`
    case $PARAM in
        --java_home)
            JAVA_HOME=$VALUE
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

mkdir $LOGDIR
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
srun --pack-group=1 $SPARK_HOME/bin/spark-class org.apache.spark.deploy.worker.Worker $MASTER_URL -d $SPARK_WORKER_DIR &

# again, sleep a tiny little bit
sleep 5s


sparksubmitcall="$SPARK_HOME/bin/spark-submit --master $MASTER_URL --driver-memory 2g --conf spark.default.parallelism=$TOTAL_CORES --conf spark.executor.cores=$SPARK_WORKER_CORES --executor-memory $SPARK_MEM --class $CLASS $JARFILE $PARAMS"

echo $sparksubmitcall
$sparksubmitcall

sleep infinity
