#!/bin/bash
folder=$1
if [[ -z $folder ]]; then
  echo "Usage: $0 <folder>"
  exit 1
fi

# Check if folder exists
if [[ ! -d $folder ]]; then
	echo "$folder not present in current directory"
	exit 1
fi

# Get annihilation points and elapsed time
times_path="$folder/PHITS_xyz/PHITS_times.txt"
if [[ -f $times_path ]]; then
  rm $times_path
fi

for f in "$folder"/PHITS_xyz/MSKCC/*/*_dmp.out; do 
  # Get current isotope and name the destinantion file
  # where all the annihilation points will be stored
  # (including 'long-range' events) 
  iso=$(echo $f | sed -e "s/.*\///" -e "s/_.*//" -e "s/-//" ); 
  iso_path="$folder/PHITS_xyz/$iso.dat.original"

  # Get annihilation points and change expontential notation
  cp "$f" $iso_path 
  sed -i "s/D/E/g" $iso_path

  # Get elapsed time from batch.out in the same folder
  tim=$(dirname "$f")/batch.out
  tim_ful=$(grep "cpu time" "$tim" | sed -e "s/.*=//" -e "s/ //g" )
  # Convert time to seconds
  tim_sec=$(echo $tim_ful | sed -e "s/h./*3600+/" -e "s/m./*60+/" -e "s/s.//")
  tim_sec=$(awk "BEGIN {print $tim_sec}")
  # Save time in seconds
  echo "$iso $tim_sec" >> $times_path
done

# Get times
# times_path="$folder/PHITS_xyz/PHITS_times.txt"

# for f in "$folder"/PHITS_xyz/MSKCC/*/*_dmp.out; do 
#   iso=$(echo $f | sed -e "s/.*\///" -e "s/_.*//" -e "s/-//" ); 
#   tim=$(dirname "$f")/batch.out
#   tim_ful=$(grep "cpu time" "$tim" | sed -e "s/.*=//" -e "s/ //g" )
#   tim_sec=$(echo $tim_ful | sed -e "s/h./*3600+/" -e "s/m./*60+/" -e "s/s.//")
#   tim_sec=$(awk "BEGIN {print $tim_sec}")
#   echo "$iso $tim_sec" >> $times_path
# done
