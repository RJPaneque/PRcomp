#!/bin/bash	
declare mac="$1"        # e.g. gate/PR_GATEv70.mac
shift
declare -a mats=("$@")  # e.g. WaterTFM, Water, Bone, Lung

# GATE
if [ -z "$mac" ]; then
    echo "Usage: $0 gate/mac_file material1 material2 ..." >&2
    exit 1
fi

# Check if mac file exists
if [ ! -f "$mac" ]; then
    echo "Error: $mac not found." >&2
    exit 1
fi

# check all mats are valid
num_mats=${#mats[@]}
for i in $(seq 1 $num_mats); do
    mat=${mats[$i-1]}
    if ! grep -q "$mat:" gate/data/GateMaterials.db; then
        echo "Error: '$mat' not found in gate/data/GateMaterials.db" >&2
        exit 1
    fi
done

# update materials in phantom/mac file
for i in $(seq 1 $num_mats); do
    mat=${mats[$i-1]}
    sed -i "s/mat$i\/setMaterial.*/mat$i\/setMaterial                  $mat/" gate/mac/phantoms/analytical/${num_mats}mat.mac 
done

# update mat file in main macro
sed -i "s/mac\/phantoms\/analytical\/.*/mac\/phantoms\/analytical\/${num_mats}mat.mac/" $mac

echo \"mac/phantoms/analytical/${num_mats}mat.mac\" materials modified to ${mats[@]} "(case $num_mats)"

