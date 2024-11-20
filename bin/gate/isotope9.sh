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

# Extract isotope information
declare -A atomic_numbers=(
    ["H"]=1 ["He"]=2 ["Li"]=3 ["Be"]=4 ["B"]=5 ["C"]=6 ["N"]=7 ["O"]=8 ["F"]=9 ["Ne"]=10
    ["Na"]=11 ["Mg"]=12 ["Al"]=13 ["Si"]=14 ["P"]=15 ["S"]=16 ["Cl"]=17 ["Ar"]=18 ["K"]=19 ["Ca"]=20
    ["Sc"]=21 ["Ti"]=22 ["V"]=23 ["Cr"]=24 ["Mn"]=25 ["Fe"]=26 ["Co"]=27 ["Ni"]=28 ["Cu"]=29 ["Zn"]=30
    ["Ga"]=31 ["Ge"]=32 ["As"]=33 ["Se"]=34 ["Br"]=35 ["Kr"]=36 ["Rb"]=37 ["Sr"]=38 ["Y"]=39 ["Zr"]=40
    ["Nb"]=41 ["Mo"]=42 ["Tc"]=43 ["Ru"]=44 ["Rh"]=45 ["Pd"]=46 ["Ag"]=47 ["Cd"]=48 ["In"]=49 ["Sn"]=50
    ["Sb"]=51 ["Te"]=52 ["I"]=53
)

element=$(echo "$iso" | tr -d '0-9')
Z=${atomic_numbers[$element]}
A=$(echo "$iso" | tr -d 'aA-zZ')

# Check if element is in the periodic table
if [ -z "$Z" ]; then
    echo "Element not found in the periodic table." >&2
    exit 1
fi

# Check if isotope is in data directory
if [ ! -f "gate/data/$iso.txt" ]; then
    echo "Isotope spectrum not found in gate/data directory."   >&2
    exit 1
fi

# update isotope in mac files
sed -i "s/gps\/ion.*/gps\/ion          $Z $A 0 0/" gate/mac/sources/emission/nuc.mac
echo \"gate/mac/sources/emission/nuc.mac\" isotope modified to atomic number $Z and mass number $A

sed -i "s/data\/.*/data\/$iso.txt/" gate/mac/sources/emission/spc_user.mac
echo \"gate/mac/sources/emission/spc_user.mac\" isotope modified to $iso
