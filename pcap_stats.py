#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pcap
import sys


def get_pcap_stas(input_pcap):
    """
    Reads a pcap file and returns a list of tuples. Each tuple represents a time window of 1-second and its values are
    the (total_number_of_bits, total_number_of_frames) during that second.
    For example, if list element 7 has value (30000, 5) this means that the input pcap has 5 frames of total 30000 bits
    during that second.
    """
    result = []

    # Load the pcap file into a Python object
    try:
        pcap_loader = pcap.pcap(input_pcap)
    except Exception as ex:
        print "Exception while loading pcap file:", ex
        return []

    # No frames dumped
    if not pcap_loader:
        print "Loaded pcap file:", input_pcap, "is empty."
        return []

    # Read frame-by-frame
    first_frame_flag = True
    timeslot = 0  # This value will never be used
    bytes_counter = 0
    packets_counter = 0

    for timestamp, frame in pcap_loader:
        timestamp = int(timestamp)  # Floor of timestamp, don't care for milliseconds

        if first_frame_flag:
            timeslot = timestamp
            first_frame_flag = False
            print "First frame had timestamp", timestamp, "and length", len(frame)

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

    print "Input trace was", len(result), "seconds long. I have summarized the results..."
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
