#!/bin/bash

install_gnuplot()
{
        sudo apt-get install gnuplot
}

install_dpkt()
{
        sudo pip install dpkt
}

install_pypcap()
{
        # Install pypcap library dependencies
        sudo apt-get install libpcap-dev python-dev
        # Install pypcap itself
        sudo pip install pypcap
}

install_gnuplot
install_dpkt
install_pypcap