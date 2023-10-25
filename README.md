# SheepDogAI - Evolutionary Robotics Herding Simulator

## Development Environment

**Note:** All of these instructions are intended for use on a macOS system (or other Linux-based system).

### Step 1: Install packages

The following packages (and associated versions) have been verified to work with the codebase. It is recommended to use pip to install all Python packages within the roborobo conda environment.

#### Direct Dependencies
- conda 4.11.0
- roborobo 4.0
- python 3.9.7
- numpy 1.21.5
- scipy 1.7.3
- deap 1.3.3
- qdpy 0.1.2.1
- torch 1.12.1
- scikit-learn 1.1.3
- seaborn 0.12.2
- matplotlib 3.6.2

#### All Dependencies
Once you have set up your roborobo conda environment and installed the necessary direct package dependencies, you can verify that environment contains all the correct package versions by referring to list below. This is obtained by running the first two commands, i.e., `conda activate roborobo` followed by `conda list`.
```
% conda activate roborobo
(roborobo) % conda list
# packages in environment at /Users/scott/opt/anaconda3/envs/roborobo:
#
# Name                    Version                   Build  Channel
alabaster                 0.7.12             pyhd3eb1b0_0  
babel                     2.9.1              pyhd3eb1b0_0  
blas                      1.0                    openblas  
brotlipy                  0.7.0           py39h9ed2024_1003  
ca-certificates           2022.10.11           hecd8cb5_0  
certifi                   2022.9.24        py39hecd8cb5_0  
cffi                      1.14.6           py39h2125817_0  
charset-normalizer        2.0.4              pyhd3eb1b0_0  
colorama                  0.4.4              pyhd3eb1b0_0  
commonmark                0.9.1              pyhd3eb1b0_0  
contourpy                 1.0.6                    pypi_0    pypi
cryptography              36.0.0           py39hf6deb26_0  
cycler                    0.11.0                   pypi_0    pypi
deap                      1.3.3                    pypi_0    pypi
docutils                  0.17.1           py39hecd8cb5_1  
fonttools                 4.38.0                   pypi_0    pypi
future                    0.18.2           py39hecd8cb5_1  
greenlet                  2.0.1                    pypi_0    pypi
idna                      3.3                pyhd3eb1b0_0  
imagesize                 1.3.0              pyhd3eb1b0_0  
intel-openmp              2021.4.0          hecd8cb5_3538  
jinja2                    3.0.2              pyhd3eb1b0_0  
joblib                    1.1.1            py39hecd8cb5_0  
kiwisolver                1.4.4                    pypi_0    pypi
libcxx                    12.0.0               h2f01273_0  
libffi                    3.3                  hb1e8313_2  
libgfortran               3.0.1                h93005f0_2    anaconda
libopenblas               0.3.20               h9a5756b_0  
llvm-openmp               14.0.6               h0dcd299_0  
markupsafe                2.0.1            py39h9ed2024_0  
matplotlib                3.6.2                    pypi_0    pypi
mkl                       2021.4.0           hecd8cb5_637  
mkl-service               2.4.0            py39h9ed2024_0  
ncurses                   6.3                  hca72f7f_2  
nomkl                     3.0                           0  
numpy                     1.21.5           py39h0f1bd0b_3  
numpy-base                1.21.5           py39hbda7086_3  
numpydoc                  1.1.0              pyhd3eb1b0_1  
openssl                   1.1.1s               hca72f7f_0  
packaging                 21.3               pyhd3eb1b0_0  
pandas                    1.5.2                    pypi_0    pypi
pillow                    9.2.0                    pypi_0    pypi
pip                       21.2.4           py39hecd8cb5_0  
psutil                    5.9.4                    pypi_0    pypi
pybind11                  2.8.1            py39hf018cea_1    conda-forge
pybind11-global           2.8.1            py39hf018cea_1    conda-forge
pycparser                 2.21               pyhd3eb1b0_0  
pygments                  2.10.0             pyhd3eb1b0_0  
pyopenssl                 21.0.0             pyhd3eb1b0_1  
pyparsing                 3.0.4              pyhd3eb1b0_0  
pysocks                   1.7.1            py39hecd8cb5_0  
python                    3.9.7                h88f2d9e_1  
python-dateutil           2.8.2                    pypi_0    pypi
python_abi                3.9                      2_cp39    conda-forge
pytz                      2021.3             pyhd3eb1b0_0  
pyyaml                    6.0                      pypi_0    pypi
pyzmq                     24.0.1                   pypi_0    pypi
qdpy                      0.1.2.1                  pypi_0    pypi
readline                  8.1                  h9ed2024_0  
recommonmark              0.6.0              pyhd3eb1b0_0  
requests                  2.26.0             pyhd3eb1b0_0  
roborobo                  4.0.0                    pypi_0    pypi
scikit-learn              1.1.3            py39he9d5cce_0  
scipy                     1.7.3            py39hfb86763_0  
scoop                     0.7.2.0                  pypi_0    pypi
seaborn                   0.12.2                   pypi_0    pypi
setuptools                58.0.4           py39hecd8cb5_0  
six                       1.16.0             pyhd3eb1b0_0  
sklearn                   0.0.post1                pypi_0    pypi
snowballstemmer           2.2.0              pyhd3eb1b0_0  
sphinx                    4.2.0              pyhd3eb1b0_1  
sphinx_rtd_theme          0.4.3              pyhd3eb1b0_0  
sphinxcontrib-applehelp   1.0.2              pyhd3eb1b0_0  
sphinxcontrib-devhelp     1.0.2              pyhd3eb1b0_0  
sphinxcontrib-htmlhelp    2.0.0              pyhd3eb1b0_0  
sphinxcontrib-jsmath      1.0.1              pyhd3eb1b0_0  
sphinxcontrib-qthelp      1.0.3              pyhd3eb1b0_0  
sphinxcontrib-serializinghtml 1.1.5              pyhd3eb1b0_0  
sqlite                    3.37.0               h707629a_0  
threadpoolctl             2.2.0              pyh0d69192_0  
tk                        8.6.11               h7bc2e8c_0  
torch                     1.12.1                   pypi_0    pypi
torchaudio                0.12.1                   pypi_0    pypi
torchvision               0.13.1                   pypi_0    pypi
typing-extensions         4.3.0                    pypi_0    pypi
tzdata                    2021e                hda174b7_0  
urllib3                   1.26.7             pyhd3eb1b0_0  
wheel                     0.37.0             pyhd3eb1b0_1  
xz                        5.2.5                h1de35cc_0  
zlib                      1.2.11               h4dc903c_4  
```

### Step 2: Run the simulator
Once you have activated the roborobo conda environment (by running `conda activate roborobo`) and are in the root directory of this repository, there are number of relevant commands for running the extended simulator:

| Action | Command |
|--------|---------|
| Start Evolution | `python run.py -s <config file> <run id>` |
| Resume Evolution | `python run.py -r <checkpoint file>` |
| Export Results | `python run.py -e <checkpoint file>` |
| Aggregate Archives | `python run.py -a <aggregate prefix> <generation>` |
| Plot Figures | `python run.py -p <graph type> [variant options]` |
| View Simulation | `python run.py -v <checkpoint file>` |

**Note:** The command to plot figures is expects a specific naming format for run IDs since its aggregate prefixes have been hardcoded (e.g. "shom-e", "shet-m", "mhom-d", "ashet-e", etc.). If you want to use a different naming format, please update the relevant `process/plot_*.py` files

## Cluster Environment

**Note:** All of these instructions are intended for use on a Linux system that uses the PBS queuing system.

### Step 1: Log into cluster 

Start by logging into the relevant cluster account being used to run simulations. Here is an example of how to SSH onto the CHPC cluster:

```
ssh username@lengau.chpc.ac.za
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
pip install seaborn
```

### Step 5: Upload source code

From a new terminal session (i.e. a session that is not logged into the cluster via SSH), upload the source code as follows:

```
scp -r "/Users/user/Local/GitHub Projects/username/msc-project" username@lengau.chpc.ac.za:~/lustre/msc-project
```

### Step 6: Queue a simulation job
After having defined the necessary job script (see under `jobs/` for examples), you will need to submit a request to add your simulation job to the queue.

Make sure you are SSH'ed into the cluster enviroment and located at the root directory of this repository, then run the following command if in PBS:

```
qsub jobs/default.job
```