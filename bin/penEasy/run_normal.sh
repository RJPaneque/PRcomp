#!/bin/bash

# Check if the user provided an input
if [ -z "$1" ] || ! [[ "$1" =~ ^(spc|nuc)$ ]]; then
    echo "Usage: $0 <spc or nuc>"
    exit 1
fi

# Assign the input to variables
mode=$1

# Get the number of histories from the input file
nhist=$(grep "NUMBER OF HISTORIES TO DISPLAY" normal_${mode}.in | awk '{print $1}')
nhist=$(awk '{printf "%d", $1}' <<< "$nhist")   # As integer

# Run simulation from inside the penEasy directory
# cd penEasy
./normal.x < normal_${mode}.in #>/dev/null

# Extract last positron position from the tallyParticleTrackStructure.dat file
grep -B 1 "^ " tallyParticleTrackStructure.dat | grep "3 1 1" | awk '{print $4"\t"$5"\t"$6}' > PosRange.dat

while [[ $nhist -gt $(wc -l PosRange.dat | awk '{print $1 + 200}') ]]; do
    # Modify the random seed
    r1=$RANDOM
    r2=$RANDOM
    sed -i "s/^.*INITIAL RANDOM SEEDS/ ${r1}  ${r2}              INITIAL RANDOM SEEDS/" normal_${mode}.in
    echo \"penEasy/normal_${mode}.in\" random seeds modified to ${r1} and ${r2}

    # Run and extract
    ./normal.x < normal_${mode}.in #>/dev/null
    grep -B 1 "^ " tallyParticleTrackStructure.dat | grep "3 1 1" | awk '{print $4"\t"$5"\t"$6}' >> PosRange.dat
done
# Simulate the remaining histories
# # echo $nhist
# r1=$RANDOM
# r2=$RANDOM
# sed -i "s/^.*INITIAL RANDOM SEEDS/ ${r1}  ${r2}              INITIAL RANDOM SEEDS/" normal_${mode}.in
# echo \"penEasy/normal_${mode}.in\" random seeds modified to ${r1} and ${r2}
# sed -i "/SECTION CONFIG/{n;s/.*/ $nhist             NUMBER OF HISTORIES (1.0e15 MAX)/}" normal_${mode}.in
# ./normal.x < normal_${mode}.in  #>/dev/null
# grep -B 1 "^ " tallyParticleTrackStructure.dat | grep "3 1 1" | awk '{print $4"\t"$5"\t"$6}' >> PosRange.dat

# # Recover the original number of histories
# sed -i "/SECTION CONFIG/{n;s/.*/ 1.0e4             NUMBER OF HISTORIES (1.0e15 MAX)/}" normal_${mode}.in


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
awk -vmx=$midx -vmy=$midy -vmz=$midz '{print $1-mx,$2-my,$3-mz}' PosRange.dat > tmp
mv tmp PosRange.dat
