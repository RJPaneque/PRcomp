#!/bin/bash
declare dimXY="$1"
declare dimZ="$2"
declare dxy="$3"
declare dz="$4"

# PENEASY
declare midxy=$(echo | awk -vN=$dimXY -vd=$dxy '{print N*d/2}')
declare midz=$(echo | awk -vN=$dimZ -vd=$dz '{print N*d/2}')

sed -i "/SUBSECTION FOR PARTICLE POSITION/{n;s/.*/ $midxy  $midxy  $midz                COORDINATES (cm) OF BOX CENTER/}" penEasy/normal_nuc.in
echo \"penEasy/normal_nuc.in\" coordinates of box center modified to \($midxy, $midxy, $midz\)

sed -i "/SUBSECTION FOR PARTICLE POSITION/{n;s/.*/ $midxy  $midxy  $midz                COORDINATES (cm) OF BOX CENTER/}" penEasy/normal_spc.in
echo \"penEasy/normal_spc.in\" coordinates of box center modified to \($midxy, $midxy, $midz\)

#-since phantom.vox is specifically done for some predefined voxel numbers, we dont change it, just their size
#-if want to do so, then remake the raw files and save their respective vox file
sed -i "/SECTION VOXELS HEADER/{n;n;s/.*/ $dxy  $dxy  $dz    VOXEL SIZE (cm) ALONG X,Y,Z/}" penEasy/phantomN.vox
echo \"penEasy/phantomN.vox\" voxel size modified to \($dxy, $dxy, $dz\)