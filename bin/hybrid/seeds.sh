#!/bin/bash
declare seed1="$1"
declare seed2="$2"

# HYBRID
sed -i "3s/.*/$seed1 $seed2/" hybrid/hybrid.in
echo \"hybrid/hybrid.in\" random seeds modified to $1 and $2
