ver=24

for E in $(seq 0 5 100); do
    E=$((E > 1 ? E : 1))
    echo "Energy: $E keV"
    sed -i "s/.*Spectrum.*/ $E.0e3      1.0                   Spectrum table, arbitrary normalization. Example: a single channel [10,10]MeV of null width/" pen${ver}_spc.in
    sed -i "s/.*Enter a negative prob.*/ $E.0e3      -1                   Enter a negative prob. to signal the end of the table/" pen${ver}_spc.in 
    cd ..; ./bin/penEasy/seeds.sh $RANDOM $RANDOM  > /dev/null; cd penEasy
    ./run_normal.sh spc $ver > /dev/null

    # Convert to radial coordinates
    awk '{r=sqrt($1^2 + $2^2 + $3^2); printf "%.6e\n", r}' annihilation.dat > annihilation_r.dat
    mv annihilation.dat ../RESULTS/PRofE/Water/PenEasy20${ver}_xyz/${E}keV.dat
done
