#!/bin/bash
#SBATCH --job-name=spark-pi      # create a short name for your job
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=2048
#SBATCH --time=00:20:00          # total run time limit (HH:MM:SS)
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=schorb@embl.de

module load Java/1.8.0_221

export SPARK_HOME=/g/emcf/software/spark-3.0.0-bin-hadoop3.2
JOB="$SLURM_JOB_NAME-$SLURM_JOB_ID"




export MASTER_URL="spark://$(hostname):7077"

export MASTER=$(hostname -f):7077

echo $MASTER > ./$JOB/master
export SPARK_LOG_DIR="./$JOB/logs"
export SPARK_WORKER_DIR="./$JOB/worker"
export START_WORKER_SCRIPT="./$JOB/.worker.sh"
export START_MASTER_SCRIPT="./$JOB/.master.sh"
export SPARK_LOCAL_DIRS="$TMPDIR/$JOB"


export SPARK_WORKER_CORES=$SLURM_CPUS_PER_TASK
export SPARK_MEM=$(( $SLURM_MEM_PER_CPU * SLURM_CPUS_PER_TASK ))M
export SPARK_DAEMON_MEMORY=$SPARK_MEM
export SPARK_WORKER_MEMORY=$SPARK_MEM
export SPARK_EXECUTOR_MEMORY=$SPARK_MEM

# start MASTER

srun $SPARK_HOME/sbin/start-master.sh

# sleep a tiny little bit to allow master to start
sleep 10s
echo Starting slaves
srun $SPARK_HOME/bin/spark-class org.apache.spark.deploy.worker.Worker $MASTER -d $SPARK_WORKER_DIR &
# again, sleep a tiny little bit
sleep 10s
