#!/bin/bash
declare iso="$1"	# e.g. C11, F18, Ga68

# locate isotope id (first one)
declare iso_id=$(grep $iso penelopet/mat/isotope.inp | head -1 | awk '{print $1}')

# check if isotope exists
if [ -z "$iso_id" ]; then
  echo "Error: Isotope $iso not found in penelopet/mat/isotope.inp" >&2
  exit 1
fi

# renew isotope id in the input file
awk -viso=$iso_id '{ if (NR == 2) {$4=iso} }1' penelopet/work/main/source.inp > tmp
mv tmp penelopet/work/main/source.inp
echo \"penelopet/work/main/source.inp\" isotope modified to $iso_id \($iso\)
