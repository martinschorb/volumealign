#!/bin/bash
#SBATCH --job-name=spark-master      # create a short name for your job
#SBATCH --time=<SoS_TIME>         # total run time limit (HH:MM:SS)
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
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=<SoS_EMAIL>


export DISPLAY=""
export JAVA_HOME=`readlink -m /g/emcf/software/render/deploy/jdk*`
export LOGDIR=`pwd`

# CLEAN LOGDIR

rm -f $LOGDIR/$SLURM_JOB_NAME-*/worker/*/*.jar

export SPARK_HOME=/g/emcf/software/spark-3.0.0-bin-hadoop3.2
JOB="$SLURM_JOB_NAME-$SLURM_JOB_ID"
export MASTER_URL="spark://$(hostname):7077"
export MASTER_WEB="http://$(hostname):8080"

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

CLASS="org.janelia.render.client.spark.SIFTPointMatchClient"
JARFILE="/g/emcf/software/render/render-ws-spark-client/target/render-ws-spark-client-2.3.1-SNAPSHOT-standalone.jar"
PARAMS="--baseDataUrl http://pc-emcf-16.embl.de:8080/render-ws/v1 --owner SBEM_seaurchin --collection giovanna_test0_full --pairJson /g/emcf/schorb/render-output/tile_pairs_giovanna_test0_mipmaps_z_0_to_2348_dist_0_p000.json --pairJson /g/emcf/schorb/render-output/tile_pairs_giovanna_test0_mipmaps_z_0_to_2348_dist_0_p001.json
"
PARAMS=$PARAMS`cat /g/emcf/schorb/code/volumealign/JSON_parameters/SBEMImage/SIFTparams_2D`



# PARSE COMMAND LINE ARGUMENTS

while [ "$1" != "" ]; do
    PARAM=`echo $1 | awk -F= '{print $1}'`
    VALUE=`echo $1 | awk -F= '{print $2}'`
    case $PARAM in
        --java_home)
            JAVA_HOME=$VALUE
            ;;
        --logdir)
            LOGDIR=$VALUE
            ;;
        --class)
            CLASS=$VALUE
            ;;
        --jarfile)
            JARFILE=$VALUE
            ;;
        --params)
            PARAMS=$VALUE

        *)
            echo "ERROR: unknown parameter \"$PARAM\""
            usage
            exit 1
            ;;
    esac
    shift
done










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
