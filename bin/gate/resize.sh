#!/bin/bash
declare dimXY="$1"
declare dimZ="$2"
declare dxy="$3"
declare dz="$4"

if [ -z "$dimXY" ] || [ -z "$dimZ" ] || [ -z "$dxy" ] || [ -z "$dz" ]; then
    echo "Usage: $0 dimXY dimZ dxy dz" >&2
    exit 1
fi

# GATE
declare TrFOV=$(awk "BEGIN {print $dimXY * $dxy}")
declare AxFOV=$(awk "BEGIN {print $dimZ * $dz}")

# actors
sed -i "s/setSize.*/setSize                          $TrFOV $TrFOV $AxFOV cm/" gate/mac/actors/ProdStop.mac
sed -i "s/setResolution.*/setResolution                    $dimXY $dimXY $dimZ/" gate/mac/actors/ProdStop.mac
echo \"gate/mac/actors/ProdStop.mac\" voxel dimensions modified to \($dimXY, $dimXY, $dimZ\) and total size to \($TrFOV, $TrFOV, $AxFOV\) cm

# phantoms
## voxelized
### h33 files
declare dxy_mm=$(awk "BEGIN {print $dxy * 10}")
declare dz_mm=$(awk "BEGIN {print $dz * 10}")

sed -i "10,11s/:= .*/:= $dimXY/" gate/phantom/MATERIAL.h33 gate/phantom/ACTIVITY.h33 
sed -i "4b1;5b1;12b1; b ;:1;s/:= .*/:= $dimZ/" gate/phantom/MATERIAL.h33 gate/phantom/ACTIVITY.h33 
echo \"gate/phantom/ACTIVITY.h33\" and \"gate/phantom/MATERIAL.h33\"  voxel dimensions modified to \($dimXY, $dimXY, $dimZ\)

sed -i "13,14s/:= .*/:= $dxy_mm/" gate/phantom/MATERIAL.h33 gate/phantom/ACTIVITY.h33 
sed -i "15s/:= .*/:= $dz_mm/" gate/phantom/MATERIAL.h33 gate/phantom/ACTIVITY.h33 
echo \"gate/phantom/ACTIVITY.h33\" and \"gate/phantom/MATERIAL.h33\" voxel size modified to \($dxy_mm, $dxy_mm, $dz_mm\) mm

## analytical
### 1mat
sed -i "s/setXLength.*/setXLength          $TrFOV cm/" gate/mac/phantoms/analytical/1mat.mac
sed -i "s/setYLength.*/setYLength          $TrFOV cm/" gate/mac/phantoms/analytical/1mat.mac
sed -i "s/setZLength.*/setZLength          $AxFOV cm/" gate/mac/phantoms/analytical/1mat.mac
echo \"gate/mac/phantoms/analytical/1mat.mac\" resized

### 2mat
declare AxFOV_half=$(awk "BEGIN {print $AxFOV / 2}")
declare AxFOV_quarter=$(awk "BEGIN {print $AxFOV / 4}")

sed -i "s/setXLength.*/setXLength          $TrFOV cm/" gate/mac/phantoms/analytical/2mat.mac
sed -i "s/setYLength.*/setYLength          $TrFOV cm/" gate/mac/phantoms/analytical/2mat.mac
sed -i "s/setZLength.*/setZLength          $AxFOV_half cm/" gate/mac/phantoms/analytical/2mat.mac

sed -i "s/mat1\/placement\/setTranslation.*/mat1\/placement\/setTranslation     0.0 0.0 -$AxFOV_quarter cm/" gate/mac/phantoms/analytical/2mat.mac
sed -i "s/mat2\/placement\/setTranslation.*/mat2\/placement\/setTranslation     0.0 0.0 +$AxFOV_quarter cm/" gate/mac/phantoms/analytical/2mat.mac
echo \"gate/mac/phantoms/analytical/2mat.mac\" resized

### 3mat
declare AxFOV_third=$(awk "BEGIN {print $AxFOV / 3}")

sed -i "s/setXLength.*/setXLength          $TrFOV cm/" gate/mac/phantoms/analytical/3mat.mac
sed -i "s/setYLength.*/setYLength          $TrFOV cm/" gate/mac/phantoms/analytical/3mat.mac
sed -i "s/setZLength.*/setZLength          $AxFOV_third cm/" gate/mac/phantoms/analytical/3mat.mac

sed -i "s/mat1\/placement\/setTranslation.*/mat1\/placement\/setTranslation     0.0 0.0 -$AxFOV_third cm/" gate/mac/phantoms/analytical/3mat.mac
sed -i "s/mat3\/placement\/setTranslation.*/mat3\/placement\/setTranslation     0.0 0.0 +$AxFOV_third cm/" gate/mac/phantoms/analytical/3mat.mac
echo \"gate/mac/phantoms/analytical/3mat.mac\" resized

# sources
sed -i "s/halfz.*/halfz    $AxFOV_half cm/" gate/mac/sources/shape/cylinder*.mac
echo \"gate/mac/sources/shape/cylinder\*.mac\" halfz resized