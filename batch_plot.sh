#!/bin/bash

DAT_DIRECTORY=dat
PCAP_DIRECTORY=pcap

# Loop through all pcap files in PCAP_DIRECTORY
for p in ${PCAP_DIRECTORY}/*.pcap; do
    # strip directory name from p
    PCAP_NAME=`basename ${p}`

    # read PCAP and plot time series
    bash ./plot_ts.sh ${PCAP_NAME}
done

# Histograms for bps series
for bps in ${DAT_DIRECTORY}/*.ts.bps.dat; do
    # strip directory name from bps
    ts_bps_name=`basename ${bps}`

    # read time series data and plot histogram
    bash ./plot_hist.sh ${ts_bps_name} mega
done

# Histograms for pps series
for pps in ${DAT_DIRECTORY}/*.ts.pps.dat; do
    # strip directory name from pps
    ts_pps_name=`basename ${pps}`

    # read time series data and plot histogram
    bash ./plot_hist.sh ${ts_pps_name} kilo
done