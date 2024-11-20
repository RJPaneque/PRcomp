#!/bin/bash
declare iso="$1"	# e.g. C11, F18, Ga68

# pennuc file for the isotope (isotope followed )
declare pennuc_file=$(echo $iso.nuc | sed -E 's/[A-Za-z]+/&-/')

# Check if the pennuc file exists
if [[ ! -f "penEasy/nuclides/$pennuc_file" ]]; then
    echo "Error: $pennuc_file not found in penEasy/nuclides directory." >&2
    exit 1
fi

# reload PENNUC (PenEasy MOD)
cd penEasy

sed -i "s/.*\.nuc/$pennuc_file/" input_decays.in 
echo \"penEasy/input_decays.in\" isotope file modified to $pennuc_file

./decays_positron.x < input_decays.in > /dev/null
echo PENNUC isotope reload done for $pennuc_file

# update pnnc_spec.dat (PenEasy SPC)
# get energy and probability from spcnuc.dat
echo "# Energy(eV) probability" > pnnc_spec.dat
awk '{print $1"\t"$6}' spcnuc.dat | sed '/^#/d' > tmp
declare s=$(awk '{sum+=$2;} END{print sum;}' tmp)
awk -vsuma=$s '{print $1"\t"$2/suma}' tmp >> pnnc_spec.dat

# add -1 probability for the last energy (EOF)
echo "# Energy(eV) probability" > pnnc_spec.dat
awk '{print $1"\t"$6}' spcnuc.dat | sed '/^#/d' > tmp
declare s=$(awk '{sum+=$2;} END{print sum;}' tmp)
awk -vsuma=$s '{print $1"\t"$2/suma}' tmp >> pnnc_spec.dat
tail -n 1 pnnc_spec.dat | awk '{$2="\t-1"}1' >> pnnc_spec.dat
rm tmp

echo \"penEasy/pnnc_spec.dat\" updated to $pennuc_file
