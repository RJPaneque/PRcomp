#!/bin/bash
declare mac="$1"	# e.g. gate/PR_GATEv70.mac
declare iso="$2"	# e.g. C11, F18, Ga68

# GATE
if [ -z "$mac" ]; then
    echo "Usage: $0 gate/mac_file isotope" >&2
    exit 1
fi

# Check if mac file exists
if [ ! -f "$mac" ]; then
    echo "Error: $mac not found." >&2
    exit 1
fi

# Check if isotope available for GATE v7.0 and mac file is GATE v7.0
if [ "$mac" == *"7"* && -f "gate/mac/sources/emission/spc_fixed_$iso.mac" ]; then
    sed -i "s/spc_fixed.*/spc_fixed_$iso.mac/" $mac
    echo \"$mac\" isotope modified to $iso
fi
