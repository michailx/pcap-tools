#!/bin/bash
# The purpose of this script is to break a large pcap file to smaller ones for easier storage/transfer/plotting.
# Please note that a TCP session may end up in consecutive files, i.e., the script does not attempt to maintain a
# session in a single pcap file.

PCAP_DIRECTORY=pcap

echo User provided $# input arguments: $@
if [ $# -ne 2 ]; then
	echo Please provide 2 command-line arguments: INPUT_FILE and OUTPUT_FILE_SIZE_MB
	echo E.g.: uliege_in.pcap 50
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
OUTPUT_FILES=${1%?????}
OUTPUT_FILE_SIZE_MB=$2  # Technically, millions of bytes, i.e., 10 is 1,000,000 bytes, not 1,048,576 bytes.

echo Splitting file ${PCAP_DIRECTORY}/${INPUT_FILE} in multiple pcap files ${OUTPUT_FILE_SIZE_MB} MByte each \(maximum\)

tcpdump -r ${PCAP_DIRECTORY}/${INPUT_FILE} -w ${PCAP_DIRECTORY}/${OUTPUT_FILES}-part -C ${OUTPUT_FILE_SIZE_MB}
# Savefiles after the first savefile will have the name specified with the -w flag,
# with a number after it, starting at 1 and continuing upward.

# Add .pcap extension to all files in output directory
for f in ${PCAP_DIRECTORY}/${OUTPUT_FILES}-part*;do mv "$f" "$f.pcap"; done
