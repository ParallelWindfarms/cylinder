#!/bin/sh -l

# Activate environment
conda activate cylinder
python --version

# Activate
source /opt/OpenFOAM/setImage_v1906.sh

# Check installation
blockMesh -help