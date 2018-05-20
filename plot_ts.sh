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
echo Will export these statistics to text file $OUTPUT_DAT_DIRECTORY/$OUTPUT_FILE.dat
python ./pcap_stats.py $INPUT_FILE $OUTPUT_DAT_DIRECTORY/$OUTPUT_FILE.dat

# Step 2: Read text file and generate two plots; one for bps and one for pps

# X-axis: Time (seconds), Y-axis: kbits per second
gnuplot -c bits_template.gnuplot \
$OUTPUT_DAT_DIRECTORY/$OUTPUT_FILE.dat $OUTPUT_PNG_DIRECTORY/$OUTPUT_FILE-kbps.png

# X-axis: Time (seconds), Y-axis: Packets per second
gnuplot -c pkts_template.gnuplot \
$OUTPUT_DAT_DIRECTORY/$OUTPUT_FILE.dat $OUTPUT_PNG_DIRECTORY/$OUTPUT_FILE-pps.png
