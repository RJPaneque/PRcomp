#!/bin/bash
declare seed1="$1"
declare seed2="$2"

# PENELOPET
sed -i "s/^.*\[Random number generator seeds\]/$1 $2 		\[Random number generator seeds\]/" penelopet/work/main/main.inp
echo \"penelopet/work/main/main.inp\" random seeds modified to $1 and $2
