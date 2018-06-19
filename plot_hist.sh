#!/bin/bash

DAT_DIRECTORY=dat
PNG_DIRECTORY=png

if [ $# -eq 1 ]; then
    OUTPUT_NUM_SCALE=""
elif [ $# -eq 2 ]; then
    OUTPUT_NUM_SCALE=$2
else
	echo Please provide command-line arguments: INPUT_FILE and \(optional\) OUTPUT_NUM_SCALE
	echo E.g.: uliege_in.ts.bps.dat mega
    exit
fi

INPUT_FILE=$1
IF_ARRAY=(${INPUT_FILE//./ })
X_AXIS_UNIT=${OUTPUT_NUM_SCALE}${IF_ARRAY[2]}

OUTPUT_FILE=${IF_ARRAY[0]}.histogram.${X_AXIS_UNIT}  # Example result: uliege_in.histogram.megabps.dat

# Step 1: Read the series from the input data file, compute the histogram, and output the data to a new file
echo Exporting histogram data to ${DAT_DIRECTORY}/${OUTPUT_FILE}.dat
CMD=`python ./create_histogram.py ${DAT_DIRECTORY}/${INPUT_FILE} ${DAT_DIRECTORY}/${OUTPUT_FILE}.dat ${OUTPUT_NUM_SCALE}`
echo ${CMD}

# Step 2: Read the histogram data file and generate a plot
echo Exporting histogram graph to ${PNG_DIRECTORY}/${OUTPUT_FILE}.png
gnuplot -c histogram.gnuplot \
${DAT_DIRECTORY}/${OUTPUT_FILE}.dat ${PNG_DIRECTORY}/${OUTPUT_FILE}.png ${CMD} ${X_AXIS_UNIT}