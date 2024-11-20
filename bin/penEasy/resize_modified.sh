#!/bin/bash
declare dimXY="$1"
declare dimZ="$2"
declare dxy="$3"
declare dz="$4"

# PENEASY MOD
#-since phantom.vox is specifically done for some predefined voxel numbers, we dont change it, just their size
#-if want to do so, then remake the raw files and save their respective vox file
sed -i "/SECTION VOXELS HEADER/{n;n;s/.*/ $dxy  $dxy  $dz    VOXEL SIZE (cm) ALONG X,Y,Z/}" penEasy/phantom.vox
echo \"penEasy/phantom.vox\" voxel size modified to \($dxy, $dxy, $dz\)
