#!/usr/bin/env bash
# The purpose of this script is to read a trace (.pcap file) and plot a time series, e.g., packets per second.

OUTPUT_DAT_DIRECTORY=dat
OUTPUT_PNG_DIRECTORY=png

echo User provided $# input arguments: $@
if [ $# -ne 2 ]; then
	echo Please provide 2 command-line arguments: INPUT_FILE and OUTPUT_FILE
    exit
fi

INPUT_FILE=$1
OUTPUT_FILE=$2

# Step 1: Read trace and export statistics to a text file
echo Reading pcap file $INPUT_FILE and generating traffic statistics \(bpps,pps\)...
python ./pcap_stats.py $INPUT_FILE $OUTPUT_DAT_DIRECTORY/$OUTPUT_FILE

# Step 2: Read text file and generate two plots; one for bps and one for pps
gnuplot -c template.gnuplot \
$OUTPUT_DAT_DIRECTORY/$OUTPUT_FILE-pps.dat $OUTPUT_PNG_DIRECTORY/$OUTPUT_FILE-pps.png 5 pps

gnuplot -c template.gnuplot \
$OUTPUT_DAT_DIRECTORY/$OUTPUT_FILE-bps.dat $OUTPUT_PNG_DIRECTORY/$OUTPUT_FILE-bps.png 5 bps
