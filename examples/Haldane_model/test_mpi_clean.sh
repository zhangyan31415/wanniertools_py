#!/bin/bash
#SBATCH -J wt_mpi_clean
#SBATCH -p h20,h200,h800,gpu4090_128
#SBATCH -N 2
#SBATCH --ntasks-per-node=20
#SBATCH -o mpi_test_%j.out
#SBATCH -e mpi_test_%j.err
#SBATCH -A hmt03
#SBATCH --time=00:10:00

echo "=== MPI Test for WannierTools ==="
echo "Nodes: $SLURM_JOB_NUM_NODES"
echo "Tasks per node: $SLURM_NTASKS_PER_NODE" 
echo "Total tasks: $SLURM_NTASKS"
echo "Node list: $SLURM_JOB_NODELIST"

# 激活环境
source $(dirname $(dirname $(which mamba)))/etc/profile.d/conda.sh
conda activate wt-py-mpi

# 运行MPI测试
echo "=== Running MPI WannierTools ==="
mpirun wt-py

echo "=== Results ==="
if [ -f WT.out ]; then
    grep "You are using" WT.out
else
    echo "No WT.out file found"
fi 