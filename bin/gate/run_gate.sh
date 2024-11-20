#!/bin/bash

declare mac="$1"        # e.g. PR_GATEv70.mac

# Check if mac file exists
if [ ! -f "$mac" ]; then
    echo "Error: $mac not found." >&2
    exit 1
fi

# Specify execution by version
if [ "$mac" == *"7"* ]; then
    ./Gate $mac | grep annihil | grep -v applyCuts | awk '{print $2,$3,$4}' > output/annihilation.dat

else if [ "$mac" == *"9"* ]; then
    Gate $mac | grep annihilation | grep -v applyCuts | awk '{print $2,$3,$4}' > output/annihilation.dat
else
    echo "Error: $mac version not matched." >&2
    exit 1
fi
fi
awk '{print $1 / 10, $2 / 10, $3 / 10}' output/annihilation.dat > tmp && mv tmp output/annihilation.dat