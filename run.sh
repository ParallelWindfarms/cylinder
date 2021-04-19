#!/bin/sh -l

# Activate environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate cylinder
python --version

# Activate
source /opt/OpenFOAM/setImage_v1906.sh

# Check installation
blockMesh -help