#!/bin/sh -l

# Activate environment
source ~/miniconda3/etc/profile.d/conda.sh
conda info --envs
conda activate
python --version

# Activate OpenFOAM
source /opt/OpenFOAM/setImage_v1906.sh

# Check installation
blockMesh -help