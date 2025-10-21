ver=24EPR
for par in "e-" "e+"; do
echo "Particle: $par"

if [ "$par" = "e-" ]; then
    sed -i 's/.*ELECTRON.*/ 1                               PARTICLE TYPE (1=ELECTRON, 2=PHOTON, 3=POSITRON) OR RADIONUCLIDE FILENAME (e.g., Co-60.nuc)/' pen${ver}_spc.in
elif [ "$par" = "e+" ]; then
    sed -i 's/.*ELECTRON.*/ 3                               PARTICLE TYPE (1=ELECTRON, 2=PHOTON, 3=POSITRON) OR RADIONUCLIDE FILENAME (e.g., Co-60.nuc)/' pen${ver}_spc.in
fi

for E in $(seq 5 5 95) $(seq 100 50 1500); do #
    E=$((E > 1 ? E : 1))
    sed -i "s/.*Spectrum.*/ $E.0e3      1.0                   Spectrum table, arbitrary normalization. Example: a single channel [10,10]MeV of null width/" pen${ver}_spc.in
    sed -i "s/.*Enter a negative prob.*/ $E.0e3      -1                   Enter a negative prob. to signal the end of the table/" pen${ver}_spc.in 
    cd ..; ./bin/penEasy/seeds.sh $RANDOM $RANDOM  > /dev/null; cd penEasy

    SECONDS=0
    ./run_normal.sh spc $ver > /dev/null
    duration=$SECONDS
    hours=$((duration / 3600))
    minutes=$(( (duration % 3600) / 60 ))
    seconds=$((duration % 60))
    printf "Energy: %s keV (%d:%02d:%02d)\n" "$E" "$hours" "$minutes" "$seconds"

    #awk '{r=sqrt($1^2 + $2^2 + $3^2); printf "%.6e\n", r}' range.dat > range_r.dat
    mv range.dat ../RESULTS/PRofE/Water/PenEasy2024_xyz/${par}/${E}keV-range.dat
    mv eloss.dat ../RESULTS/PRofE/Water/PenEasy2024_xyz/${par}/${E}keV-eloss.dat
    mv nint.dat ../RESULTS/PRofE/Water/PenEasy2024_xyz/${par}/${E}keV-nint.dat
done
echo
done
