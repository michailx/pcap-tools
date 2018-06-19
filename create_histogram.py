#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import array
from numpy import float64
from numpy import histogram
from numpy import std
from numpy import mean
from scipy.stats import skew
from scipy.stats import kurtosis
import sys


def read_series_file(input_data_file):
    series = []

    with open(input_data_file, 'r') as f:
        for line in f:
            data_point = _parse_line(line)  # Read a line from the file and parse it to find the series data point
            if data_point is not None:
                series.append(data_point)

    return array(series, dtype=float64)  # Return NumPy array


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
        # print "Data point is NOT an integer... ERROR:", ex
        # print "This is expected only at the start of a .dat file as column headers are strings."
        data_point = None

    return data_point


def compute_histogram(series, bin_width_method='auto'):
    hist_array, bin_edges_array = histogram(series, bins=bin_width_method, density=False)

    # bin_edges_array must be equal to len(hist_array)+1
    assert (len(bin_edges_array) == len(hist_array)+1),\
        "Error as number of bin edges is not equal to the number of histogram values plus 1. Aborting..."

    result = []  # This is a list of tuples
    for z in xrange(0, len(hist_array)):
        # Each bin has edges a and b, where:
        a = int(bin_edges_array[z])
        b = int(bin_edges_array[z + 1])

        if z == len(hist_array) - 1:
            # label [a, b] for last bin
            bin_label = '[{0},{1}]'.format(a, b)
        else:
            # label [a, b) for the rest
            bin_label = '[{0},{1})'.format(a, b)

        result.append((bin_label, hist_array[z]))

    return result


def compute_kurtosis(series):
    return kurtosis(series)


def compute_mean(series):
    return mean(series, dtype=float64)


def compute_skewness(series):
    return skew(series)


def compute_standard_deviation(series):
    return std(series, dtype=float64)


def write_hist_file(hist, output_data_file):
    with open(output_data_file, 'w') as f:
        for i in hist:
            line = '{0} {1}\n'.format(*i)
            f.write(line)


if __name__ == "__main__":
    if len(sys.argv) not in [3, 4]:
        print "Running script", sys.argv[0]
        print "User provided", (len(sys.argv) - 1), "command-line arguments:"
        print str(sys.argv[1:])
        print "These arguments are invalid. Aborting ..."
        sys.exit()

    user_input = {'input_file': sys.argv[1], 'output_file': sys.argv[2]}

    # Read time series data from file
    series = read_series_file(user_input['input_file'])

    # If user provided a new scale, then convert values. E.g., from bps to Mbps
    scales = {'kilo': 1000, 'mega': 1000000, 'giga': 1000000000}
    if len(sys.argv) == 4:
        # Check if user input is valid
        if sys.argv[3] in scales.keys():
            # print "Converting time series values to", sys.argv[3]
            denominator = scales[sys.argv[3]]
            series = series / denominator
        else:
            print "Invalid number scale. Possible values:", scales.keys()
            print "Aborting ..."
            sys.exit()

    # Only print 3 decimal places
    # I purposefully did NOT leave any spaces as it causes an issue to Gnuplot when trying to write this on the graph
    print 'mean:{0:.3f},st.d:{1:.3f},skew:{2:.3f},kurt:{3:.3f}'.format(compute_mean(series),
                                                                       compute_standard_deviation(series),
                                                                       compute_skewness(series),
                                                                       compute_kurtosis(series))

    hist = compute_histogram(series)

    write_hist_file(hist, user_input['output_file'])


