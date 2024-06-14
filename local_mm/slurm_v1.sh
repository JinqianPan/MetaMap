#!/bin/bash
#SBATCH --job-name=imp_1                     # Job name
#SBATCH --mail-type=ALL                    # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=     # Where to send mail
#SBATCH --cpus-per-task=2                  # Number of cores per MPI rank 
#SBATCH --ntasks=1                         # Number of MPI ranks
#SBATCH --nodes=1                          # Number of nodes
#SBATCH --mem-per-cpu=10gb
#SBATCH --time=300:00:00                    # Time limit hrs:min:sec
#SBATCH --array=1-100                 # Array range
#SBATCH --output=../slurm_output/imp_1_1_%a.out                # Standard output and error log

module load java
module load conda
conda activate py39

API_PATH=ADD_PATH
CODE_PATH=ADD_PATH

cd $API_PATH
./bin/skrmedpostctl start
./bin/wsdserverctl start

cd $CODE_PATH
python main_code.py --save_num 100 --total_machine 100 --num_machine $SLURM_ARRAY_TASK_ID --data_name order_impression_1.tsv

cd $API_PATH
./bin/skrmedpostctl stop
./bin/wsdserverctl stop
