#!/bin/bash
declare mac="$1"	# e.g. gate/PR_GATEv70.mac
declare emis="$2"	# SPC or NUC

# GATE >9.0
if [ -z "$mac" ]; then
    echo "Usage: $0 gate/mac_file emission_mode" >&2
    exit 1
fi

# Check if mac file exists
if [ ! -f "$mac" ]; then
    echo "Error: $mac not found." >&2
    exit 1
fi

# Check mac file version
if [[ "$mac" == *"7"* ]]; then
    echo "Error: $mac cannot be edited with $0." >&2
    exit 1
fi

# update mode in mac file
if [ "$emis" == "SPC" ]; then
    sed -i "s/sources\/emission.*/sources\/emission\/spc_user9.mac/" $mac
    echo \"$mac\" mode modified to SPC

elif [ "$emis" == "NUC" ]; then
    sed -i "s/sources\/emission.*/sources\/emission\/nuc.mac/" $mac
    echo \"$mac\" mode modified to NUC

else
    echo "Error: mode must be SPC or NUC" >&2
    exit 1
fi