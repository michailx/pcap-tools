#!/usr/bin/env bash
# The purpose of this script is to break a large pcap file to smaller ones for easier storage/transfer/plotting.
# Please note that a TCP session may end up in consecutive files, i.e., the script does not attempt to maintain a
# session in a single pcap file.

OUTPUT_PCAP_DIRECTORY=pcap

echo User provided $# input arguments: $@
if [ $# -ne 3 ]; then
	echo Please provide 3 command-line arguments: INPUT_FILE, OUTPUT_FILES and OUTPUT_FILE_SIZE_MB
    exit
fi

INPUT_FILE=$1
OUTPUT_FILES=$2
OUTPUT_FILE_SIZE_MB=$3  # Technically, millions of bytes, i.e., 10 is 1,000,000 bytes, not 1,048,576 bytes.

echo Splitting file ${INPUT_FILE} in multiple pcap files ${OUTPUT_FILE_SIZE_MB} MByte each \(maximum\)

tcpdump -r ${INPUT_FILE} -w ${OUTPUT_PCAP_DIRECTORY}/${OUTPUT_FILES}-part -C ${OUTPUT_FILE_SIZE_MB}
# Savefiles after the first savefile will have the name specified with the -w flag,
# with a number after it, starting at 1 and continuing upward.

# Add .pcap extension to all files in output directory
for f in ${OUTPUT_PCAP_DIRECTORY}/${OUTPUT_FILES}-part*;do mv "$f" "$f.pcap"; done