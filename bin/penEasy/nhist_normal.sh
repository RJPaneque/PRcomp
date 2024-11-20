#!/bin/bash
declare nhist="$1"      # e.g. 1e6, 100, 9.3e6

# PENEASY NUC&SPC: change number of histories simulated and tallied tracks
# note: annihilation points will be taken from tallied tracks, which is limited to 1e4.
#       Larger nhist will only impact in histories simulated, thus time consumed, but
#       will have no effect in final results

if (( $(awk 'BEGIN{print ('$nhist' > 1e4)}') )); then
  nhist_sim=1e4
else
  nhist_sim=$nhist
fi

sed -i "/SECTION CONFIG/{n;s/.*/ $nhist_sim             NUMBER OF HISTORIES (1.0e15 MAX)/}" penEasy/normal_nuc.in
sed -i "/SECTION TALLY PARTICLE TRACK STRUCTURE/{n;n;s/.*/ $nhist                             NUMBER OF HISTORIES TO DISPLAY (~100 RECOMMENDED)/}" penEasy/normal_nuc.in
echo \"penEasy/normal_nuc.in\" number of histories modified to $nhist

sed -i "/SECTION CONFIG/{n;s/.*/ $nhist_sim             NUMBER OF HISTORIES (1.0e15 MAX)/}" penEasy/normal_spc.in
sed -i "/SECTION TALLY PARTICLE TRACK STRUCTURE/{n;n;s/.*/ $nhist                             NUMBER OF HISTORIES TO DISPLAY (~100 RECOMMENDED)/}" penEasy/normal_spc.in
echo \"penEasy/normal_spc.in\" number of histories modified to $nhist
