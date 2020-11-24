#!/bin/bash
#SBATCH --job-name=spark-master      # create a short name for your job
#SBATCH --time=00:10:00          # total run time limit (HH:MM:SS)
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=schorb@embl.de
# #  --- Master resources ---
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=1G
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1
# # --- Worker resources ---
#SBATCH packjob
#SBATCH --job-name spark-worker
#SBATCH --nodes=25
#SBATCH --mem-per-cpu=4G
#SBATCH --cpus-per-task=10
#SBATCH --ntasks-per-node=1



#module load Java/1.8.0_221
#module load X11
source /g/emcf/schorb/code/volumealign/dash/utils/setup_py_environment.sh

export DISPLAY=""
export JAVA_HOME=`readlink -m /g/emcf/software/render/deploy/jdk*`


export SPARK_HOME=/g/emcf/software/spark-3.0.0-bin-hadoop3.2
JOB="$SLURM_JOB_NAME-$SLURM_JOB_ID"
export MASTER_URL="spark://$(hostname):7077"

#export MASTER=$(hostname -f):7077

#echo $MASTER > ./$JOB/master
export SPARK_LOG_DIR="./$JOB/logs"
export SPARK_WORKER_DIR="./$JOB/worker"
export SPARK_LOCAL_DIRS="$TMPDIR/$JOB"


export SPARK_WORKER_CORES=$SLURM_CPUS_PER_TASK_PACK_GROUP_1

# export SPARK_DRIVER_MEM=$((4 * 1024))

export SPARK_MEM=$(( $SLURM_MEM_PER_CPU_PACK_GROUP_1 * $SLURM_CPUS_PER_TASK_PACK_GROUP_1))m
export SPARK_DAEMON_MEMORY=$SPARK_MEM
export SPARK_WORKER_MEMORY=$SPARK_MEM


PY_FILE=$rendermodules"/rendermodules/pointmatch/generate_point_matches_spark.py"
INPUT_JSON="/g/emcf/schorb/code/volumealign/JSON_parameters/SBEMImage/SIFTpointmatch_test1_2D.json"


# start MASTER

$SPARK_HOME/sbin/start-master.sh

# sleep a tiny little bit to allow master to start
sleep 5s

#echo Starting slaves
srun --pack-group=1 $SPARK_HOME/bin/spark-class org.apache.spark.deploy.worker.Worker $MASTER_URL -d $SPARK_WORKER_DIR &

# again, sleep a tiny little bit
sleep 5s


sparksubmitcall="python $PY_FILE --input_json $INPUT_JSON --master $MASTER_URL "

echo $sparksubmitcall
$sparksubmitcall

sleep infinity
