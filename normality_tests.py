#!/usr/bin/env python
# -*- coding: utf-8 -*-


from numpy import amin
from scipy.stats import shapiro
from scipy.stats import normaltest
from scipy.stats import anderson
from sys import argv
from create_histogram import read_series_file


# Shapiro-Wilk Test
def shapiro_wilk_test(data, alpha=0.05):
    _, p = shapiro(data)
    # Check p-value
    if p > alpha:
        # Fails to reject the null hypothesis, therefore it looks Gaussian
        gaussian_like = True
    else:
        # Rejects the null hypothesis, therefore it doesn't look Gaussian
        gaussian_like = False

    return gaussian_like


# D’Agostino’s K^2 Test
def d_agostino_k_squared_test(data, alpha=0.05):
    _, p = normaltest(data)
    # Check p-value
    if p > alpha:
        # Fails to reject the null hypothesis, therefore it looks Gaussian
        gaussian_like = True
    else:
        # Rejects the null hypothesis, therefore it doesn't look Gaussian
        gaussian_like = False

    return gaussian_like


# Anderson-Darling Test
def anderson_darling_test(data):
    statistic, critical_values, significance_level = anderson(data)
    # statistic is a float, whereas both critical_values and significance_level are Numpy arrays
    # The Anderson test returns a critical value for each significance level. The significance levels for a Gaussian
    # distribution are 15%, 10%, 5%, 2.5% and 1%, i.e., both arrays will have 5 elements.

    # Instead of comparing the statistics against each critical value (and getting a separate result for each
    # significance level) I will just return True if the series are Gaussian-like for ALL significance levels.
    minimum_cv = amin(critical_values)
    if statistic < minimum_cv:
        # Fails to reject the null hypothesis, therefore it looks Gaussian
        gaussian_like = True
    else:
        # Rejects the null hypothesis, therefore it doesn't look Gaussian
        gaussian_like = False

    return gaussian_like


if __name__ == "__main__":
    if len(argv) != 3:
        print "Running script", argv[0]
        print "User provided", (len(argv) - 1), "command-line arguments:"
        print str(argv[1:])
        print "These arguments are invalid. Aborting ..."
        exit()

    user_input = {'input_file': argv[1], 'alpha': float(argv[2])}

    # Read time series data from file
    series = read_series_file(user_input['input_file'])

    # Run tests and print result
    print "Series:", user_input['input_file']
    print "Distribution is Gaussian (or Gaussian-like) ..."
    print "* Shapiro-Wilk test:", shapiro_wilk_test(series, user_input['alpha'])
    print "* D’Agostino’s K^2 test:", d_agostino_k_squared_test(series, user_input['alpha'])
    print "* Anderson-Darling test:", anderson_darling_test(series)
