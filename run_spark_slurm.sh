#!/bin/bash
#SBATCH --job-name spark-master
#SBATCH --time=00:10:00
# --- Master resources ---
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=1G
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1
# --- Worker resources ---
#SBATCH packjob
#SBATCH --job-name spark-worker
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=4G
#SBATCH --cpus-per-task=2
#SBATCH --ntasks-per-node=1
# --- Driver resources ---
#SBATCH packjob
#SBATCH --job-name spark-driver
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=2G
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1


module load Java/1.8.0_221


export SPARK_HOME=/g/emcf/software/spark-3.0.0-bin-hadoop3.2
export SPARK_CONF_DIR=/g/emcf/schorb/software/SparkConf
mkdir -p $SPARK_CONF_DIR


JOB="$SLURM_JOB_NAME-$SLURM_JOB_ID"


env=$SPARK_CONF_DIR/spark-env.sh
echo "export SPARK_LOG_DIR=$SLURM_SUBMIT_DIR/$JOB/logs" > $env
echo "export SPARK_WORKER_DIR=~$SLURM_SUBMIT_DIR/$JOB/worker" >> $env
echo "export SLURM_MEM_PER_CPU=$(( $SLURM_MEM_PER_CPU_PACK_GROUP_1 * SLURM_CPUS_PER_TASK_PACK_GROUP_1 ))M" >> $env
echo "export SPARK_WORKER_CORES=$SLURM_CPUS_PER_TASK_PACK_GROUP_1" >> $env
echo "export SPARK_WORKER_MEMORY=$(( $SPARK_WORKER_CORES*$SLURM_MEM_PER_CPU ))M" >> $env
echo "export SPARK_WORKER_CORES=$SLURM_CPUS_PER_TASK_PACK_GROUP_1" >> $env
echo "export SPARK_MEM=$(( $SLURM_MEM_PER_CPU_PACK_GROUP_1 * SLURM_CPUS_PER_TASK_PACK_GROUP_1 ))M" >> $env
echo "export SPARK_DAEMON_MEMORY=$SPARK_MEM" >> $env
echo "export SPARK_WORKER_MEMORY=$SPARK_MEM" >> $env
echo "export SPARK_EXECUTOR_MEMORY=$SPARK_MEM" >> $env
echo "export SPARK_IDENT_STRING=$SLURM_JOBID" >> $env
echo "export SPARK_TOTAL_EXECUTOR_CORES=$((SLURM_NTASKS_PACK_GROUP_1 * SLURM_CPUS_PER_TASK_PACK_GROUP_1))" >> $env


#echo "export SPARK_HOME=$SPARK_HOME" > ~/.bashrc
#echo "export JAVA_HOME=$JAVA_HOME" >> ~/.bashrc
#echo "export SPARK_CONF_DIR=$SPARK_CONF_DIR" >> ~/.bashrc


conf=$SPARK_CONF_DIR/spark-defaults.conf
echo "spark.default.parallelism" $(( $SLURM_CPUS_PER_TASK * $SLURM_NTASKS ))> $conf
echo "spark.submit.deployMode" client >> $conf
echo "spark.master" spark://`hostname`:7077 >> $conf
echo "spark.executor.cores" $SLURM_CPUS_PER_TASK >> $conf
echo "spark.executor.memory" $(( $SLURM_CPUS_PER_TASK*$SLURM_MEM_PER_CPU ))M >> $conf


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
$SPARK_HOME/sbin/start-slave.sh $*
EOF

cat << "EOF" > "$START_MASTER_SCRIPT"
#!/bin/bash
$SPARK_HOME/sbin/start-master.sh
srun --pack-group=2 \
    --job-name="spark-driver" \
   --output="$SPARK_LOG_DIR/spark-driver.out" \
"$DRIVER_SCRIPT"

#scancel ${SLURM_JOB_ID}
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
