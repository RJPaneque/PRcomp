#!/bin/bash
declare seed1="$1"
declare seed2="$2"

# PENEASY
sed -i "s/^.*INITIAL RANDOM SEEDS/ $1  $2              INITIAL RANDOM SEEDS/" penEasy/normal_nuc.in
echo \"penEasy/normal_nuc.in\" random seeds modified to $1 and $2

sed -i "s/^.*INITIAL RANDOM SEEDS/ $1  $2              INITIAL RANDOM SEEDS/" penEasy/normal_spc.in
echo \"penEasy/normal_spc.in\" random seeds modified to $1 and $2

sed -i "s/^.*INITIAL RANDOM SEEDS/ $1  $2              INITIAL RANDOM SEEDS/" penEasy/modified.in
echo \"penEasy/modified.in\" random seeds modified to $1 and $2