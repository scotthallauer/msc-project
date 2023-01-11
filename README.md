# SheepDogAI - Evolutionary Robotics Herding Simulator

## Installation

**Note:** All of these instructions are intended for use on a Linux system.

### Step 1: Log into cluster 

Start by logging into the relevant cluster account being used to run simulations. Here is an example of how to SSH onto the CHPC cluster:

```
ssh shallauer@lengau.chpc.ac.za
```

### Step 2: Install conda

First remove any conda config from .bashrc (normally at end of file).

The installation process will probably differ between cluster envirnoments, but here is how it is done on the CHPC:

```
module purge
module load chpc/BIOMODULES anaconda/3
```

Verify that both Python and Conda are installed correctly:

```
python --version
conda list
```

Refresh the shell environment by executing the following command and then exiting and logging in again:

```
conda init bash
```

### Step 3: Install roborobo

If roborobo4 is not installed, you need to activate the necessary module. This is how it is done on the CHPC:

```
module purge
module load chpc/BIOMODULES anaconda/3
module load chpc/BIOMODULES roborobo4
```

Run the following command if in PBS:

```
eval "$(conda shell.bash hook)"
```

Verify that the conda, python and roborobo modules are all installed correctly:

```
which conda # expected: /apps/chpc/bio/anaconda3-2020.02/bin/conda
conda activate roborobo
which python # expected: /apps/chpc/bio/anaconda3-2020.02/envs/roborobo/bin/python
python -c 'import pyroborobo'
```

### Step 4: Install Python packages

Make sure the roborobo conda environment is activated and then install the 
necessary Python packages as follows:

```
pip install deap
pip install qdpy
pip install torch
pip install scikit-learn
```

### Step 5: Upload source code

From a new terminal session (i.e. a session that is not logged into the cluster via SSH), upload the source code as follows:

```
scp -r "/Users/scott/Local/GitHub Projects/scotthallauer/msc-project" shallauer@lengau.chpc.ac.za:~/lustre/msc-project
```