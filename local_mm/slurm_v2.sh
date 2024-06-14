#!/bin/bash
#SBATCH --job-name=n_25_r                     # Job name
#SBATCH --output=../slurm_output/nav_2_5_%a.out  # Standard output and error log
#SBATCH --array=1-2                         # Array range
#SBATCH --mail-type=ALL                      # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=       # Where to send mail
#SBATCH --cpus-per-task=2                    # Number of cores per MPI rank 
#SBATCH --ntasks=1                           # Number of MPI ranks
#SBATCH --nodes=1                            # Number of nodes
#SBATCH --mem-per-cpu=10gb                   # Memory per CPU
#SBATCH --time=300:00:00                     # Time limit hrs:min:sec

commands=(
    "python main_code.py --begin_num 9594 --finish_num 9828 --num_machine 42 --data_name order_narratives_2.tsv"
    "python main_code.py --begin_num 9594 --finish_num 9828 --num_machine 42 --data_name order_narratives_2.tsv"
)

API_PATH=ADD_PATH
CODE_PATH=ADD_PATH

module load java
module load conda
conda activate py39

cd $API_PATH
./bin/skrmedpostctl start
./bin/wsdserverctl start

cd $CODE_PATH
${commands[$SLURM_ARRAY_TASK_ID-1]}  # Array indexes start at 1

cd $API_PATH
./bin/wsdserverctl stop
