#!/bin/bash
declare iso="$1"	# e.g. C11, F18, Ga68

# pennuc file for the isotope (isotope followed )
declare pennuc_file=$(echo $iso.nuc | sed -E 's/[A-Za-z]+/&-/')

# Check if the pennuc file exists
if [[ ! -f "penEasy/nuclides/$pennuc_file" ]]; then
    echo "Error: $pennuc_file not found in penEasy/nuclides directory." >&2
    exit 1
fi

# PenEasy NUC
sed -i "/SECTION SOURCE BOX ISOTROPIC GAUSS/{n;n;s/.*/ $pennuc_file                               PARTICLE TYPE (1=ELECTRON, 2=PHOTON, 3=POSITRON) OR RADIONUCLIDE FILENAME (e.g., Co-60.nuc)/}" penEasy/pen??_nuc.in
echo \"penEasy/pen??_nuc.in\" isotope file modified to $pennuc_file
