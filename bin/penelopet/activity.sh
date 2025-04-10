#!/bin/bash
declare act="$1"      # e.g. 1e6, 100, 9.3e6

if [ -z "$act" ]; then
    echo "Usage: $0 <activity>"
    echo "Example: $0 1e6"
    exit 1
fi

# PENELOPET: change activity for the 1sec simulation, number of histories for different times
#-->WARNING: if simulation time is changed, must change $act -> $act/t in following line
declare nhist=$act
awk -vn=$nhist '{ if (NR == 2) {$2=n} }1' penelopet/work/main/source.inp > tmp
mv tmp penelopet/work/main/source.inp
echo \"penelopet/work/main/source.inp\" activity modified to $nhist
