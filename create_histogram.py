#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import histogram
from numpy import array
import sys


def read_series_file(input_data_file):
    series = []

    with open(input_data_file, 'r') as f:
        for line in f:
            data_point = _parse_line(line)  # Read a line from the file and parse it to find the series data point
            if data_point is not None:
                series.append(data_point)

    return array(series)  # Return NumPy array


def _parse_line(line):
    """
    Parse a string to find the series data point. This implementation is specific to the .dat file as created by
    pcap_stats.py
    """
    values = line.split()  # Delimiter is whitespace

    # column "total" is values[1]
    try:
        data_point = int(values[1])

    except ValueError as ex:
        print "Data point is NOT an integer... ERROR:", ex
        print "This is expected only at the start of a .dat file as column headers are strings."
        data_point = None

    return data_point


def compute_histogram(series, bin_width_method='auto', number_scale='unchanged'):
    scales = {'unchanged': 0, 'kilo': 1000, 'mega': 1000000, 'giga': 1000000000}
    divide = scales[number_scale]

    hist_array, bin_edges_array = histogram(series, bins=bin_width_method, density=False)

    # bin_edges_array must be equal to len(hist_array)+1
    assert (len(bin_edges_array) == len(hist_array)+1),\
        "Error as number of bin edges is not equal to the number of histogram values plus 1. Aborting..."

    result = []  # This is a list of tuples
    for x in xrange(0, len(hist_array)):
        bin_label = '[{0},{1})'.format(int(bin_edges_array[x]/divide), int(bin_edges_array[x+1]/divide))
        result.append((bin_label, hist_array[x]))

    return result


def write_hist_file(hist, output_data_file):
    with open(output_data_file, 'w') as f:
        for i in hist:
            line = '{0} {1}\n'.format(*i)
            f.write(line)


if __name__ == "__main__":
    print "Running script", sys.argv[0]
    print "User provided", (len(sys.argv)-1), "command-line arguments:"

    if len(sys.argv) != 4:
        print str(sys.argv[1:])
        print "These arguments are invalid. Exiting..."
        sys.exit()

    user_input = {'input_file': sys.argv[1], 'output_file': sys.argv[2], 'x-axis_num_scale': sys.argv[3]}
    print "* Input file (dat):", user_input['input_file']
    print "* Output file (dat):", user_input['output_file']
    print "* Histogram x-axis number scale:", user_input['x-axis_num_scale']

    series = read_series_file(user_input['input_file'])

    # FIXME: Divide with 1000000 to convert bps to Mbps.
    hist = compute_histogram(series, number_scale=user_input['x-axis_num_scale'])
    write_hist_file(hist, user_input['output_file'])


