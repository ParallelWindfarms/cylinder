#!/bin/sh -l

source /opt/OpenFOAM/setImage_v1906.sh

cd data/cavity
blockMesh
icoFoam