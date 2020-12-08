#!/bin/bash
#SBATCH --job-name=spark-master      # create a short name for your job
#SBATCH --time=00:30:00          # total run time limit (HH:MM:SS)
# #  --- Master resources ---
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=1G
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1
# # --- Worker resources ---
#SBATCH hetjob
#SBATCH --job-name spark-worker
#SBATCH --nodes=30
#SBATCH --mem-per-cpu=4G
#SBATCH --cpus-per-task=10
#SBATCH --ntasks-per-node=1
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=schorb@embl.de



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


export SPARK_WORKER_CORES=$SLURM_CPUS_PER_TASK_HET_GROUP_1

export TOTAL_CORES=$(($SPARK_WORKER_CORES * $SLURM_JOB_NUM_NODES_HET_GROUP_1))

# export SPARK_DRIVER_MEM=$((4 * 1024))

export SPARK_MEM=$(( $SLURM_MEM_PER_CPU_HET_GROUP_1 * $SLURM_CPUS_PER_TASK_HET_GROUP_1))m
export SPARK_DAEMON_MEMORY=$SPARK_MEM
export SPARK_WORKER_MEMORY=$SPARK_MEM



CLASS="org.janelia.render.client.spark.SIFTPointMatchClient"
JARFILE="/g/emcf/software/render/render-ws-spark-client/target/render-ws-spark-client-2.3.1-SNAPSHOT-standalone.jar"
RENDERPARAMS="--baseDataUrl http://pc-emcf-16.embl.de:8080/render-ws/v1 --owner SBEM_seaurchin --collection giovanna_test0_translation --pairJson /g/emcf/schorb/render-output/tile_pairs_giovanna_test0_mipmaps_z_0_to_2348_dist_1_p000.json --pairJson /g/emcf/schorb/render-output/tile_pairs_giovanna_test0_mipmaps_z_0_to_2348_dist_1_p001.json --pairJson /g/emcf/schorb/render-output/tile_pairs_giovanna_test0_mipmaps_z_0_to_2348_dist_1_p002.json --pairJson /g/emcf/schorb/render-output/tile_pairs_giovanna_test0_mipmaps_z_0_to_2348_dist_1_p003.json --pairJson /g/emcf/schorb/render-output/tile_pairs_giovanna_test0_mipmaps_z_0_to_2348_dist_1_p004.json
"
PARAMS=`cat /g/emcf/schorb/code/volumealign/JSON_parameters/SBEMImage/SIFTparams_2D`


# start MASTER

$SPARK_HOME/sbin/start-master.sh

# sleep a tiny little bit to allow master to start
sleep 5s

#echo Starting slaves
srun --pack-group=1 $SPARK_HOME/bin/spark-class org.apache.spark.deploy.worker.Worker $MASTER_URL -d $SPARK_WORKER_DIR &

# again, sleep a tiny little bit
sleep 5s


sparksubmitcall="$SPARK_HOME/bin/spark-submit --master $MASTER_URL --driver-memory 2g --conf spark.default.parallelism=$TOTAL_CORES --conf spark.executor.cores=$SPARK_WORKER_CORES --executor-memory $SPARK_MEM --class $CLASS $JARFILE $RENDERPARAMS $PARAMS"

echo $sparksubmitcall
$sparksubmitcall

sleep infinity
