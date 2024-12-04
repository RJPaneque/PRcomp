#!/bin/bash
declare seed1="$1"
declare seed2="$2"

# PENEASY
sed -i "s/^.*INITIAL RANDOM SEEDS/ $1  $2              INITIAL RANDOM SEEDS/" penEasy/pen*.in
echo \"penEasy/pen*.in\" random seeds modified to $1 and $2