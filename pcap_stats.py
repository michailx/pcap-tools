#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dpkt
import pcap
import sys
from socket import getservbyport
from socket import error


def _get_pkt_ports(ip_pkt):
    """
    Scans the IP packet and returns tuple (IP_PROTO, L4_LOW_PORT, L4_HIGH_PORT) for UDP or TCP segment. Otherwise
    returns tuple (IP_PROTO, None, None).
    """
    if ip_pkt.p in [dpkt.ip.IP_PROTO_TCP, dpkt.ip.IP_PROTO_UDP]:
        # Get Layer4 PDU
        transport = ip_pkt.data

        if transport.sport < transport.dport:
            # Always put the lower port nbr in position tuple[1]. This will avoid duplicates.
            result = (ip_pkt.p, transport.sport, transport.dport)
        else:
            result = (ip_pkt.p, transport.dport, transport.sport)

    else:
        result = (ip_pkt.p, None, None)

    return result


def _get_trace_ports(input_pcap):
    """
    Reads a pcap file returns a list of tuples. Each tuple is a unique (IP_PROTO, LOW_PORT, HIGH_PORT) where LOW_PORT
    and HIGH_PORT are both UDP/TCP ports and LOW_PORT is simply a smaller number than HIGH_PORT. The latter happens to
    avoid the duplicate (IP_PROTO, HIGH_PORT, LOW_PORT)
    """
    scan = set()

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

    for _, buf in pcap_loader:
        ether_frame = dpkt.ethernet.Ethernet(buf)  # Get Ethernet frame
        ip_pkt = ether_frame.data  # Get IPv4 Packet
        scan.add(_get_pkt_ports(ip_pkt))

    print 'All ports', len(scan)
    return scan


def _get_trace_apps(ports=set()):
    """
    Parses a set() of tuples (ip_proto, low_port, high_port) to discover which L7 Apps are present. It uses socket lib's
    getservbyport function to map (ip_proto, port_nbr) to the service name, e.g. (6, 80) is 'http'.
    It returns a dictionary with (ip_proto, port_nbr) as keys and the corresponding service name as value, e.g.,
    {(6, 80): 'http', ...}
    """
    # ports is a set(), so all tuples (ip_proto, low_port, high_port) are unique
    apps = {}

    for (ip_proto, low_port, high_port) in ports:
        if ip_proto in [dpkt.ip.IP_PROTO_TCP, dpkt.ip.IP_PROTO_UDP]:
            # TCP or UDP packet
            # FIXME: Assumption; prioritize low_port
            if (ip_proto, low_port) in apps.keys():
                continue
            low = _getservbyport(low_port, ip_proto)
            high = _getservbyport(high_port, ip_proto)
            if (low_port < 1024) and low:
                # This is a well-known port
                apps[(ip_proto, low_port)] = low
            elif (high_port < 1024) and high:
                # This is a well-known port
                apps[(ip_proto, high_port)] = high
            elif low:
                apps[(ip_proto, low_port)] = low
            elif high:
                apps[(ip_proto, high_port)] = high
            else:
                # Both ports are > 1023 and not assigned by IANA. Do nothing for this tuple of ports.
                pass
        else:
            # Other IP_PROTO
            apps[(ip_proto, None)] = _getprotobynumber(ip_proto)

    return apps


def get_trace_stats(input_pcap, known_apps):
    """
    Reads a pcap file and returns a list of tuples. Each tuple represents a time window of 1-second and its values are
    the (total_number_of_bits, total_number_of_frames) during that second.
    For example, if list element 7 has value (30000, 5) this means that the input pcap has 5 frames of total 30000 bits
    during that second.
    """
    pkt_series = []
    bit_series = []
    apps_list = known_apps.values() + ['tcp_other', 'udp_other', 'app_other']

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
    pkt_counters = dict.fromkeys(apps_list, 0)
    bit_counters = dict.fromkeys(apps_list, 0)

    for timestamp, buf in pcap_loader:
        timestamp = int(timestamp)  # Floor the timestamp value, i.e., disregard milliseconds
        ether_frame = dpkt.ethernet.Ethernet(buf)  # Get Ethernet frame
        ip_pkt = ether_frame.data  # Get IPv4 Packet
        (ip_proto, low_port, high_port) = _get_pkt_ports(ip_pkt)  # (IP_PROTO, L4_LOW_PORT, L4_HIGH_PORT)
        # FIXME: Assumption; prioritize low_port
        if (ip_proto, low_port) in known_apps.keys():
            app = known_apps[(ip_proto, low_port)]
        elif (ip_proto, high_port) in known_apps.keys():
            app = known_apps[(ip_proto, high_port)]
        else:
            app = _getprotobynumber(ip_proto)+'_other'

        if first_frame_flag:
            # The timestamp of the first frame in the trace might not be zero. It can be seconds since Epoch.
            # Regardless the value, I will consider this timestamp as the "beginning of time" for my results.
            timeslot = timestamp
            first_frame_flag = False
            print "First frame had timestamp", timestamp, "and length", len(buf)

        while timestamp > timeslot:
            # Save result for current time slot
            pkt_series.append(pkt_counters)
            bit_series.append(bit_counters)
            # Next time slot
            timeslot += 1
            # Reset counters
            pkt_counters = dict.fromkeys(apps_list, 0)
            bit_counters = dict.fromkeys(apps_list, 0)

        # timestamp == timeslot so increase the counters for this App
        pkt_counters[app] += 1
        bit_counters[app] += len(buf)*8  # This will also include the bits of the Layer2 header

    # Above FOR loop will miss to append the last timestamp
    pkt_series.append(pkt_counters)
    bit_series.append(bit_counters)

    print "Input trace was", len(pkt_series), "seconds long. I have summarized the results..."
    return pkt_series, bit_series


def _getprotobynumber(ip_proto):
    """
    Returns the name of the transport layer protocol as a string. Only input argument is the IP Protocol number.
    For example, providing input argument 6 will return 'tcp'.
    FIXME: Isn't there a better way to do this?
    """
    transport_protocols = {1: 'icmp', 6: 'tcp', 17: 'udp', 41: 'ipv6ip', 47: 'gre', 50: 'esp'}
    try:
        return transport_protocols[ip_proto]
    except KeyError as ex:
        print "Cannot recognize IP_PROTO value", ip_proto, "ERROR:", ex
        return str(ip_proto)


def _getservbyport(tsp_port, ip_proto):
    """
    Wrapper for function socket.getservbyport(port[, protocolname]).
    """
    # I will try to identify Layer7 Application by looking at transport layer:
    app_name = None
    try:
        app_name = getservbyport(tsp_port, _getprotobynumber(ip_proto))
    except error as ex:
        # print "Undefined service (TSANSPORT_PORT_NBR, IP_PROTO_NBR)", (tsp_port, ip_proto), "ERROR:", ex
        pass
    finally:
        # return app_name, regardless if an exception occurred or not
        return app_name


def _export_stats_file(counters_list, output_file):
    """
    Export statistics to a text file that read and plotted by Gnuplot.
    """
    # Get column names:
    if len(counters_list):
        # counters_list[0] is a Python dictionary
        columns_list = counters_list[0].keys()
    else:
        # FIXME: Throw some error as no stats were gathered
        columns_list = []

    with open(output_file, 'w') as f:
        f.write('# TIME ' + ' '.join(columns_list) + '\n')
        for timeslot, stats_dict in enumerate(counters_list):
            line = ''
            for column in columns_list:
                line += ' ' + str(stats_dict[column])
            f.write(str(timeslot) + line + '\n')


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

    apps = _get_trace_apps(_get_trace_ports(user_input['input_file']))
    print apps
    # The index (keys) of this list is the elapsed time in seconds, i.e., the x-axis of a time series graph.
    # The elements (values) of this list is a tuple with two elements: the number of bits and the number of packets
    # during that second, i.e., (bits, packets). E.g., histogram = [(12000, 1), (36000, 3), ... ]
    pps, bps = get_trace_stats(user_input['input_file'], apps)

    # Write result to external file
    _export_stats_file(pps, user_input['output_file'] + '_pps')
    _export_stats_file(bps, user_input['output_file'] + '_bps')