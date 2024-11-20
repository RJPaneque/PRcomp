#!/bin/bash
declare seed1="$1"
declare seed2="$2"

# GATE
macs=$(ls gate/PR_GATEv*.mac)
sed -i "s/setEngineSeed.*/setEngineSeed $seed1/" $macs
echo \"$macs\" random seed modified to $seed1
