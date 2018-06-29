#!/usr/bin/env python
# -*- coding: utf-8 -*-


from collections import OrderedDict
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
def anderson_darling_test(data, distribution='norm'):
    statistic, critical_values, significance_level = anderson(data, distribution)
    # statistic is a float, whereas both critical_values and significance_level are Numpy arrays

    result = OrderedDict()

    for i in range(len(critical_values)):
        sl = significance_level[i]
        cv = critical_values[i]
        if statistic < cv:
            # Fails to reject the null hypothesis, therefore it matches the selected distribution
            result[(sl, cv)] = True
        else:
            # Rejects the null hypothesis, therefore it doesn't match the distribution
            result[(sl, cv)] = False

    return result


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
    print "\n"
    line = (len("Series:" + user_input['input_file']) + 1)*'='
    print line
    print "Series:", user_input['input_file']
    print line

    print "\n"
    print "Checking if distribution is Gaussian ..."
    print "* Shapiro-Wilk test:", shapiro_wilk_test(series, user_input['alpha'])
    print "* D’Agostino’s K^2 test:", d_agostino_k_squared_test(series, user_input['alpha'])
    print "* Anderson-Darling test:"
    for k, v in anderson_darling_test(series).viewitems():
        print 'significance level: {0}, critical value: {1}, result: {2}'.format(k[0], k[1], v)

    print "\n"
    print "Checking if distribution is Exponential ..."
    print "* Anderson-Darling test:"
    for k, v in anderson_darling_test(series, 'expon').viewitems():
        print 'significance level: {0}, critical value: {1}, result: {2}'.format(k[0], k[1], v)

    print "\n"
    print "Checking if distribution is Logistic ..."
    print "* Anderson-Darling test:"
    for k, v in anderson_darling_test(series, 'logistic').viewitems():
        print 'significance level: {0}, critical value: {1}, result: {2}'.format(k[0], k[1], v)

    print "\n"
    print "Checking if distribution is Gumbel (Extreme Value Type I) ..."
    print "* Anderson-Darling test:"
    for k, v in anderson_darling_test(series, 'gumbel').viewitems():
        print 'significance level: {0}, critical value: {1}, result: {2}'.format(k[0], k[1], v)
