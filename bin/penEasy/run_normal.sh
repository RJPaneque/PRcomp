#!/bin/bash

# Check if the user provided an input
if [ -z "$1" ] || ! [[ "$1" =~ ^(spc|nuc)$ ]] || ! [[ "$2" =~ ^(20|24)$ ]]; then
    echo "Usage: $0 <spc or nuc> <20 or 24>" >&2
    exit 1
fi

# Assign the input to variables
mode=$1
ver=$2

# Get the number of histories from the input file
nhist=$(grep "NUMBER OF HISTORIES TO DISPLAY" pen${ver}_${mode}.in | awk '{print $1}')
nhist=$(awk '{printf "%d", $1}' <<< "$nhist")   # As integer

# Run simulation from inside the penEasy directory
# cd penEasy
./pen${ver}.x < pen${ver}_${mode}.in #>/dev/null
rm tallyParticleTrackStructure.dat

# Extract voxel size and dims from phantomN.vox
dimX=$(grep "No. OF VOXELS" phantomN.vox | awk '{print $1}')
dimY=$(grep "No. OF VOXELS" phantomN.vox | awk '{print $2}')
dimZ=$(grep "No. OF VOXELS" phantomN.vox | awk '{print $3}')
dx=$(grep "VOXEL SIZE" phantomN.vox | awk '{print $1}')
dy=$(grep "VOXEL SIZE" phantomN.vox | awk '{print $2}')
dz=$(grep "VOXEL SIZE" phantomN.vox | awk '{print $3}')

# Get the midpoints
midx=$(echo | awk -vN=$dimX -vd=$dx '{print N*d/2}')
midy=$(echo | awk -vN=$dimY -vd=$dy '{print N*d/2}')
midz=$(echo | awk -vN=$dimZ -vd=$dz '{print N*d/2}')

# Set positron range coords in PosRange.dat around 0,0,0
awk -vmx=$midx -vmy=$midy -vmz=$midz '{print $1-mx,$2-my,$3-mz}' annihilation.dat > tmp && mv tmp annihilation.dat
