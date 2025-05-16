ver=24

D=($(seq 0 25 50))
S=${#D[@]}
rm annihilation_xyz.dat
for iso in "F18" "Ga68" "Rb82"; do
    echo "###########-iso: $iso"
    cd ..; ./bin/penEasy/isotope_nuc.sh $iso > /dev/null; cd penEasy
    for dx in ${D[@]}; do
        x=$(awk -v dx=$dx 'BEGIN{printf "%.3f", 4+(dx-25)/1000}')
        for dy in ${D[@]}; do
            y=$(awk -v dy=$dy 'BEGIN{printf "%.3f", 4+(dy-25)/1000}')
            for dz in ${D[@]}; do
                z=$(awk -v dz=$dz 'BEGIN{printf "%.3f", 4+(dz-25)/1000}')
                echo "dx: $x, dy: $y, dz: $z"
                sed -i "s/.*COORDINATES (cm) OF BOX CENTER/ $x  $y  $z                COORDINATES (cm) OF BOX CENTER/" pen${ver}_nuc.in
                cd ..; ./bin/penEasy/seeds.sh $RANDOM $RANDOM  > /dev/null; cd penEasy

                ./run_normal.sh nuc $ver > /dev/null
                awk '{printf "%.6e %.6e %.6e\n", $1, $2, $3}' annihilation.dat >> annihilation_xyz.dat
                wc -l annihilation_xyz.dat
            done
        done
    done
    mv annihilation_xyz.dat ../RESULTS/kernel/Water/PenEasy20${ver}_xyz/simulated_${iso}_S$S.dat
done
