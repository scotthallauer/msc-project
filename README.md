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

If not, you will need to install it before continuing. The process will probably differ between cluster envirnoments, but here is how it done on the CHPC:

```
# check available python modules
module avail chpc/python

# install the appropriate anaconda version
module purge
module load chpc/python/anaconda/3-2021.11
python3 --version
```

### Step 3: Install roborobo

Create a conda environment:

```
conda create --name roborobo numpy pybind11 
conda activate roborobo
```

Install Python dependencies for Roborobo (numpy, pybind11, sphinx, etc.):

```
conda install numpy setuptools
conda install -c conda-forge pybind11
conda install sphinx recommonmark sphinx_rtd_theme numpydoc
```

Install C++ dependencies for Roborobo (Cmake, SDL2, boost and eigen):

```
# if you have sudo access...
sudo apt install git build-essential cmake
sudo apt-get install libsdl2-dev libsdl2-image-dev libboost-dev libeigen3-dev

# alternatively...
module load chpc/git/2.14
module load chpc/build-essentials/gnu_0.1
module load chpc/cmake/3.20.0/gcc-6.1.0

git clone https://github.com/libsdl-org/SDL
cd SDL
mkdir build
cd build
../configure
make
```

