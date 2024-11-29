#!/bin/bash
############################################
#####---JUST FOR HOMOGENOUS MEDIA!!!---#####
############################################
declare mat="$1"	# JUST ONE; e.g. water, bone, lung

# PENELOPET: locate material and isotope ids (if bone, selects bone_cor)
declare mat_id=$(grep -wn $mat penelopet/mat/mat_names.inp | sed 's/:.*//')

# check if material exists
if [ -z "$mat_id" ]; then
  echo "Error: Material $mat not found in penelopet/mat/mat_names.inp" >&2
  exit 1
fi

# ensure object.inp is the one for homogeneous media
#cp -f penelopet/work/object.inp.1 penelopet/work/main/object.inp

# PENELOPET
# awk -velem=$elem_id -vmat=$mat_id '{ if (NR == 2) {$5=mat} }1' penelopet/work/main/source.inp > tmp
# mv tmp penelopet/work/main/source.inp
# echo \"penelopet/work/main/source.inp\" material modified to $mat_id \( $mat\)

awk -vmat=$mat_id '{ if (NR == 2) {$3=mat} }1' penelopet/work/main/object.inp > tmp
mv tmp penelopet/work/main/object.inp
echo \"penelopet/work/main/object.inp\" material modified to $mat_id \($mat\)