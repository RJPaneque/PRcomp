#!/bin/bash

# Read the input file
input_file="all_spc.txt"

# Define the output files
output_files=("C11.txt" "N13.txt" "O15.txt" "F18.txt" "Cu64.txt" "Ga68.txt" "Rb82.txt" "I124.txt")

# Initialize column index
col_index=1

# Loop through the output files and extract the corresponding columns
for output_file in "${output_files[@]}"; do
    awk -v i=$col_index -v j=$(($col_index + 1)) '{print $i,$j}' "$input_file" > "$output_file"
    col_index=$((col_index + 2))
done

# Convert the first column from eV to MeV in each output file
for output_file in "${output_files[@]}"; do
    awk '{ $1 = $1 / 1000000; print }' "$output_file" > tmp && mv tmp "$output_file"
done

# Add header for interpolation spectrum
for output_file in "${output_files[@]}"; do
    sed -i '1i3\t0' "$output_file"
done

# Print a message indicating the completion of the script
echo "Splitting to"
echo "    ${output_files[@]}"
echo "completed and conversion from eV to MeV fulfilled."