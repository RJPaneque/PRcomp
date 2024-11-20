#!/bin/bash
declare iso="$1"

# check if isotope is valid
if [[ "$iso" != "Ga68" && "$iso" != "Rb82" ]]; then
    echo "Invalid isotope. Choose between Ga68 and Rb82." &>2
    exit 1
fi

# HYBRID
cp -f hybrid/espectros/$iso.txt hybrid/espectro.txt
echo \"hybrid/espectro.txt\" updated to $iso