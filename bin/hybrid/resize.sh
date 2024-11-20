#!/bin/bash
declare dimXY="$1"
declare dimZ="$2"
declare dxy="$3"
declare dz="$4"

# HYBRID
sed -i "1s/.*/$dimXY $dimXY $dimZ/" hybrid/hybrid.in
sed -i "2s/.*/$dxy $dxy $dz/" hybrid/hybrid.in
echo \"hybrid/hybrid.in\" voxel dimensions modified to \($dimXY, $dimXY, $dimZ\) and voxel size to \($dxy, $dxy, $dz\)