#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pcap
import sys


def get_pcap_stas(input_pcap):
    """
    Whatever may roam
    """
    result = []

    # Load the pcap file into a Python object
    try:
        pcap_loader = pcap.pcap(input_pcap)
    except Exception as ex:
        print "Exception while loading pcap file:", ex
        return []

    # No packets dumped
    if not pcap_loader:
        print "Loaded pcap file:", input_pcap, "is empty."
        return []

    # Read packet by packet
    timeslot = 0
    bytes_counter = 0
    packets_counter = 0

    for timestamp, frame in pcap_loader:
        timestamp = int(timestamp)  # Floor of timestamp, don't care for milliseconds

        while timestamp > timeslot:
            # Save result for current time slot
            result.append((bytes_counter*8, packets_counter))
            # Next time slot
            timeslot += 1
            # Reset counters
            bytes_counter = 0
            packets_counter = 0

        # timestamp == timeslot:
        bytes_counter += len(frame)
        packets_counter += 1

    # Above for loop will miss to append the last timestamp
    result.append((bytes_counter * 8, packets_counter))

    return result


if __name__ == "__main__":
    print "Running script", sys.argv[0]
    print "User provided", (len(sys.argv)-1), "command-line arguments:"

    if len(sys.argv) != 3:
        print str(sys.argv[1:])
        print "These arguments are invalid. Exiting..."
        sys.exit()

    user_input = {'input_file': sys.argv[1], 'output_file': sys.argv[2]}
    print "* Input file (pcap):", user_input['input_file']
    print "* Output file (dat):", user_input['output_file']

    # The index (keys) of this list is the elapsed time in seconds, i.e., the x-axis of a time series graph.
    # The elements (values) of this list is a tuple with two elements: the number of bits and the number of packets
    # during that second, i.e., (bits, packets). E.g., histogram = [(12000, 1), (36000, 3), ... ]
    histogram = get_pcap_stas(user_input['input_file'])

    # Write result to external file
    with open(user_input['output_file'], 'w') as f:
        # Write kbps instead of bps
        f.write('# Time_Slot kbps pps\n')
        for timeslot, (bits, packets) in enumerate(histogram):
            f.write(str(timeslot) + ' ' + str(bits/10.0**3) + ' ' + str(packets) + '\n')
