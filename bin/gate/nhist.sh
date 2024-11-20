#!/bin/bash
declare mac="$1"	    # e.g. gate/PR_GATEv70.mac
declare nhist="$2"      # e.g. 1e6, 100, 9.3e6

# GATE
if [ -z "$mac" ]; then
    echo "Usage: $0 gate/mac_file number_of_histories" >&2
    exit 1
fi

# Check if mac file exists
if [ ! -f "$mac" ]; then
    echo "Error: $mac not found." >&2
    exit 1
fi

sed -i "s/setTotalNumberOfPrimaries .*/setTotalNumberOfPrimaries $nhist/" $mac
echo \"$mac\" number of histories modified to $nhist
