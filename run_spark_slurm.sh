#!/bin/bash
#SBATCH --job-name spark-cluster
#SBATCH --time=00:20:00
# --- Master resources ---
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=1G
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1
# --- Worker resources ---
#SBATCH packjob
#SBATCH --nodes=4
#SBATCH --mem-per-cpu=4G
#SBATCH --cpus-per-task=2
#SBATCH --ntasks-per-node=1


# --- Driver resources ---
#SBATCH packjob
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=2G
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1


module load Java

export SPARK_ROOT=/g/emcf/schorb/software/spark
export SPARK_HOME=/g/emcf/software/spark-3.0.0-bin-hadoop3.2



JOB="$SLURM_JOB_NAME-$SLURM_JOB_ID"
export MASTER_URL="spark://$(hostname):7077"
export SPARK_LOG_DIR="$SLURM_SUBMIT_DIR/$JOB/logs"
export SPARK_WORKER_DIR="$SLURM_SUBMIT_DIR/$JOB/worker"
export START_WORKER_SCRIPT="$SLURM_SUBMIT_DIR/$JOB/.worker.sh"
export START_MASTER_SCRIPT="$SLURM_SUBMIT_DIR/$JOB/.master.sh"
export SPARK_LOCAL_DIRS="$TMPDIR/$JOB"
export SPARK_WORKER_CORES=$SLURM_CPUS_PER_TASK_PACK_GROUP_1
export SPARK_MEM=$(( $SLURM_MEM_PER_CPU_PACK_GROUP_1 * SLURM_CPUS_PER_TASK_PACK_GROUP_1 ))M
export SPARK_DAEMON_MEMORY=$SPARK_MEM
export SPARK_WORKER_MEMORY=$SPARK_MEM
export SPARK_EXECUTOR_MEMORY=$SPARK_MEM
export SPARK_IDENT_STRING=$SLURM_JOBID
export SPARK_TOTAL_EXECUTOR_CORES=$((SLURM_NTASKS_PACK_GROUP_1 * SLURM_CPUS_PER_TASK_PACK_GROUP_1))

mkdir -p "$SPARK_LOG_DIR" "$SPARK_WORKER_DIR"

cat << "EOF" > "$START_WORKER_SCRIPT"
#!/bin/bash
function finish {
   rm -rf "$SPARK_LOCAL_DIRS"
}
trap finish EXIT
mkdir -p "$SPARK_LOCAL_DIRS"
export SPARK_NO_DAEMONIZE=1
$SPARK_HOME/start-slave.sh $*
EOF

cat << "EOF" > "$START_MASTER_SCRIPT"
#!/bin/bash
$SPARK_HOME/start-master.sh
srun --pack-group=2 \
     --job-name="spark-driver" \
     --output="$SPARK_LOG_DIR/spark-driver.out" \
     "$DRIVER_SCRIPT"
scancel ${SLURM_JOB_ID}
EOF

chmod +x "$START_WORKER_SCRIPT" "$START_MASTER_SCRIPT"

srun --pack-group=0 \
     --job-name="spark-master" \
     "$START_MASTER_SCRIPT" &

srun --pack-group=1 \
     --job-name="spark-worker" \
     --output="$SPARK_LOG_DIR/spark-workers.out" \
     --label \
     "$START_WORKER_SCRIPT" "$MASTER_URL"
