#!/bin/bash

OUTPUT_DAT_DIRECTORY=dat
OUTPUT_PNG_DIRECTORY=png

echo User provided $# input arguments: $@
if [ $# -ne 3 ]; then
	echo Please provide 3 command-line arguments: INPUT_FILE, OUTPUT_FILE and NUM_SCALE
	echo Example values: ./dat/uliege_in-bps.dat uliege_in-bps mega
    exit
fi

INPUT_FILE=$1
OUTPUT_FILE=$2-hist
NUM_SCALE=$3

# Step 1: Read the series from the input data file, compute the histogram, and output the data to a new file
python ./create_histogram.py $INPUT_FILE $OUTPUT_DAT_DIRECTORY/$OUTPUT_FILE.dat $NUM_SCALE

# Step 2: Read the histogram data file and generate a plot
gnuplot -c histogram.gnuplot \
$OUTPUT_DAT_DIRECTORY/$OUTPUT_FILE.dat $OUTPUT_PNG_DIRECTORY/$OUTPUT_FILE.png $NUM_SCALE-bps