# SheepDogAI - Evolutionary Robotics Herding Simulator

## Installation

**Note:** All of these instructions are intended for use on a Linux system.

### Step 1: Log into cluster 

Start by logging into the relevant cluster account being used to run simulations. Here is an example of how to SSH onto the CHPC cluster:

```
ssh shallauer@lengau.chpc.ac.za
```

### Step 2: Install conda

Check that conda is installed in your cluster environment:

```
conda list
```

If not, you will need to install it before continuing. The process will probably differ between cluster envirnoments, but here is how it is done on the CHPC:

```
# check available python modules
module avail chpc/python

# install the appropriate anaconda version
module purge
module load chpc/python/anaconda/3-2021.11
python3 --version
```

### Step 3: Install roborobo

If roborobo4 is not installed, you need to activate the necessary module. This is how it is done on the CHPC:

```
module load chpc/BIOMODULES roborobo4
```

### Step 4: Upload source code

From a new terminal session (i.e. a session that is not logged into the cluster via SSH), upload the source code as follows:

```
scp -r "/Users/scott/Local/GitHub Projects/scotthallauer/msc-project" shallauer@lengau.chpc.ac.za:~/msc-project
```