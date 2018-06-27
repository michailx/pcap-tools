#!/bin/bash

DAT_DIRECTORY=dat
ALPHA=0.05

# Loop through all bps series in DAT_DIRECTORY
for bps in ${DAT_DIRECTORY}/*.ts.bps.dat; do
    # read time series data and check if normal distribution
    python ./normality_tests.py ${bps} ${ALPHA}
done

# Loop through all bps series in DAT_DIRECTORY
for pps in ${DAT_DIRECTORY}/*.ts.pps.dat; do
    # read time series data and check if normal distribution
    python ./normality_tests.py ${pps} ${ALPHA}
done