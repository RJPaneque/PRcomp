#!/bin/bash
############################################
#####---JUST FOR HOMOGENOUS MEDIA!!!---#####
############################################
declare mat="$1"	# name of the .mat file without extension
change_phantom=true

if [ ! -f "penEasy/mat/$mat.mat" ]; then
    echo "Material file \"penEasy/mat/$mat.mat\" not found!" >&2
    exit 1
fi

# penEasy SPC & NUC
sed -i -E "s/mat\/[a-zA-Z0-9]+.mat/mat\/$mat.mat/" penEasy/pen??_spc.in penEasy/pen??_nuc.in
echo \"penEasy/pen??_spc.in\" and \"penEasy/pen??_nuc.in\"  material modified to $mat

# phantomN.vox
if $change_phantom; then
    dens=$(grep "Mass density" penEasy/mat/$mat.mat | awk '{printf "%f\n", $4}')
    awk -v d="$dens" '{
        if (NR > 7) {
            $3=d
        }
        print
    }' penEasy/phantomN.vox > tmp
    mv tmp penEasy/phantomN.vox
    echo \"penEasy/phantomN.vox\" density modified to $dens
fi