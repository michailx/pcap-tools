#!/bin/bash

# The purpose of this script is to merge several pcap files into a single one. The packets are rearranged according to
# their timestamps. See mergecap application for more information.
# Link: https://www.wireshark.org/docs/man-pages/mergecap.html

echo User provided $# input arguments: $@
if [ $# -ne 2 ]; then
	echo Please provide 2 command-line arguments: PCAP_FILES_DIRECTORY and OUTPUT_FILENAME
	echo E.g.: ./pcap output.pcap
	exit
fi

# Directory where the pcap files are stored
PCAP_FILES_DIRECTORY=$1
OUTPUT_FILENAME=$2

# Check if directory exists
if [ -d "${PCAP_FILES_DIRECTORY}" ]; then
	echo Successfully located directory "${PCAP_FILES_DIRECTORY}"
else
    echo Cannot locate directory "${PCAP_FILES_DIRECTORY}" ... Aborting!
    exit
fi

echo ... Creating file ./${OUTPUT_FILENAME}
mergecap "${PCAP_FILES_DIRECTORY}"/*.pcap -w ${OUTPUT_FILENAME}