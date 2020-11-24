#!/bin/bash
#SBATCH --job-name=spark-master      # create a short name for your job
#SBATCH --time=00:30:00          # total run time limit (HH:MM:SS)
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=schorb@embl.de
# #  --- Master resources ---
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=8G
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1
# # --- Worker resources ---
#SBATCH packjob
#SBATCH --job-name spark-worker
#SBATCH --nodes=5
#SBATCH --mem-per-cpu=8G
#SBATCH --cpus-per-task=10
#SBATCH --ntasks-per-node=1



#module load Java/1.8.0_221
#module load X11

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
export SPARK_MEM=$(( $SLURM_MEM_PER_CPU_PACK_GROUP_1 * $SLURM_CPUS_PER_TASK_PACK_GROUP_1 ))m
export SPARK_DAEMON_MEMORY=$SPARK_MEM
export SPARK_WORKER_MEMORY=$SPARK_MEM



CLASS="org.janelia.saalfeldlab.hotknife.SparkConvertRenderStackToN5"
JARFILE="/g/emcf/schorb/code/hot-knife/target/hot-knife-0.0.4-SNAPSHOT.jar"
RENDERPARAMS="--baseUrl http://pc-emcf-16.embl.de:8080/render-ws/v1 --owner SBEM --stack testsolve_results --project tests"
PARAMS="--n5Path /g/emcf/schorb/render-output/test-3D-downsampling1.n5 --n5Dataset setup0/timepoint0 --tileSize 2048,1536 --min -1071,-21047,442 --size 7555,6918,9  --blockSize 64,64,16 --factors 2,2,2"

# start MASTER

$SPARK_HOME/sbin/start-master.sh

# sleep a tiny little bit to allow master to start
sleep 5s

#echo Starting slaves
srun --pack-group=1 $SPARK_HOME/bin/spark-class org.apache.spark.deploy.worker.Worker $MASTER_URL -d $SPARK_WORKER_DIR &

# again, sleep a tiny little bit
sleep 5s


$SPARK_HOME/bin/spark-submit --master $MASTER_URL --driver-memory 6g --conf spark.default.parallelism=$SPARK_WORKER_CORES --conf spark.executor.cores=$SPARK_WORKER_CORES --executor-memory $SPARK_MEM --class $CLASS $JARFILE $RENDERPARAMS $PARAMS

sleep infinity
