#!/bin/bash
# The purpose of this script is to read a trace (.pcap file) and plot a time series, e.g., packets per second.

DAT_DIRECTORY=dat
PCAP_DIRECTORY=pcap
PNG_DIRECTORY=png

echo User provided $# input arguments: $@
if [ $# -ne 1 ]; then
	echo Please provide 1 command-line argument: the INPUT_FILE under directory ./pcap/
    exit
fi

# Input file name
INPUT_FILE=$1

# Check if input file in directory PCAP_DIRECTORY exists
if [ -f ${PCAP_DIRECTORY}/${INPUT_FILE} ]; then
	echo Successfully located file ${INPUT_FILE} in directory ${PCAP_DIRECTORY}
else
    echo Cannot locate file ${INPUT_FILE} in directory ${PCAP_DIRECTORY} ... Aborting!
    exit
fi

# Input file name without the .pcap extension
INPUT_FILE_NE=${1%?????}
# In case there are any dots in the file name, replace them with underscores
OUTPUT_FILE=${INPUT_FILE_NE//./_}

# Step 1: Read trace and export statistics to a text file
echo Reading pcap file $INPUT_FILE and generating traffic statistics \(bps, pps\)...
python ./pcap_stats.py ${PCAP_DIRECTORY}/${INPUT_FILE} ${DAT_DIRECTORY}/${OUTPUT_FILE}

# Step 2: Read text file and generate two plots; one for bps and one for pps
gnuplot -c template.gnuplot \
${DAT_DIRECTORY}/${OUTPUT_FILE}.ts.pps.dat ${PNG_DIRECTORY}/${OUTPUT_FILE}.ts.pps.png 5 pps

gnuplot -c template.gnuplot \
${DAT_DIRECTORY}/${OUTPUT_FILE}.ts.bps.dat ${PNG_DIRECTORY}/${OUTPUT_FILE}.ts.bps.png 5 bps
