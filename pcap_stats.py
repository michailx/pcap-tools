#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dpkt
import pcap
import sys
from heapq import nlargest
from socket import getservbyport
from socket import error
from collections import OrderedDict


def read_pcap_file(input_pcap):
    """
    Reads a packet trace, i.e. a pcap file, and returns a packet capture object (see pcap library).
    """

    # Load the pcap file into a Python object
    try:
        pcap_loader = pcap.pcap(input_pcap)
    except Exception as ex:
        print "Exception while loading pcap file:", ex
        sys.exit()

    # No frames dumped
    if not pcap_loader:
        print "Loaded pcap file:", input_pcap, "is empty."
        sys.exit()

    # Check data link protocol
    if pcap_loader.datalink() == dpkt.pcap.DLT_EN10MB:
        # Ethernet
        print "Datalink is Ethernet"
    elif pcap_loader.datalink() == dpkt.pcap.DLT_RAW:
        # Raw
        print "No Datalink protocol, i.e., Raw"
    else:
        print "Datalink is (value)", pcap_loader.datalink(), ". Don't know how to handle this, exiting..."
        # See values here: https://github.com/pynetwork/pypcap/blob/master/pcap.pyx
        sys.exit()

    return pcap_loader


def _get_ip_pkt(buf, datalink, timestamp=None):
    """
    Reads the buffer and removes all protocol headers until it finds the IPv4 header. Returns the IPv4 packet.
    """
    # Check data link protocol
    if datalink == dpkt.pcap.DLT_EN10MB:
        # Ethernet
        ether_frame = dpkt.ethernet.Ethernet(buf)  # Get Ethernet frame
        if ether_frame.type == dpkt.ethernet.ETH_TYPE_IP:
            ip_pkt = ether_frame.data  # Get IPv4 Packet
        else:
            print "Ethernet Type is (value)", ether_frame.type, ". Don't know how to handle this, exiting..."
            return None

    elif datalink == dpkt.pcap.DLT_RAW:
        # Raw
        try:
            ip_pkt = dpkt.ip.IP(buf)
        except dpkt.UnpackError as ex:
            # Will trigger for non IP packets, e.g., IPv6.
            # print "Unpack error at time", '{0:.10f}'.format(timestamp), "ERR:", ex
            return None
    else:
        print "Datalink is (value)", datalink, ". Don't know how to handle this, exiting..."
        # See values here: https://github.com/pynetwork/pypcap/blob/master/pcap.pyx
        return None

    # Also need to check if packet is IPv4

    return ip_pkt


def _pkt_is_ip_fragment(ip_pkt):
    """
    Parses an IPv4 packet and decided whereather is it a fragment (or not). Returns True if Flag "More Fragments" is set
    or the "Fragment Offset" is non-zero.
    """
    # Pull out fragment information (flags and offset all packed into off field, so use bitmasks)

    more_fragments = bool(ip_pkt.off & dpkt.ip.IP_MF)
    fragment_offset = ip_pkt.off & dpkt.ip.IP_OFFMASK
    # do_not_fragment = bool(ip_pkt.off & dpkt.ip.IP_DF)  # Actually, I don't need this flag.

    if more_fragments or (fragment_offset != 0):
        return True
    else:
        return False


def _get_ip_pkt_ports(buf, datalink, timestamp=None):
    """
    Scans the IP packet and returns tuple (IP_PROTO, L4_LOW_PORT, L4_HIGH_PORT) for UDP or TCP segment. Otherwise
    returns tuple (IP_PROTO, None, None).
    """
    # Get IP Header
    ip_pkt = _get_ip_pkt(buf, datalink, timestamp)
    if ip_pkt is None:
        return None

    # Check if packet is an IP Fragment
    if _pkt_is_ip_fragment(ip_pkt):
        # FIXME: Returning -1 as ports for IPv4 fragments since I cannot get the port number
        return ip_pkt.p, -1, -1

    if ip_pkt.p in [dpkt.ip.IP_PROTO_TCP, dpkt.ip.IP_PROTO_UDP]:
        # Get Layer4 PDU
        transport = ip_pkt.data
        # Double-check that the IP payload is in fact a TCP or UDP segment:
        if (isinstance(transport, dpkt.tcp.TCP) or isinstance(transport, dpkt.udp.UDP)):
            try:
                # FIXME: Check if src < 1023 < dst OR src > 1023 > dst, in an attempt to add less tuples to the set()
                # FIXME: The basis for this assumption is the client<>server model where client port > 1023 whereas
                # FIXME: the server is using a well-known port < 1024.
                if (transport.sport < 1024) and (transport.dport >= 1024):
                    #
                    result = (ip_pkt.p, transport.sport, None)
                elif (transport.dport < 1024) and (transport.sport >= 1024):
                    #
                    result = (ip_pkt.p, transport.dport, None)
                else:
                    # FIXME: Adding both ports in the tuple since checks above were inconclusive.
                    if transport.sport < transport.dport:
                        # Always put the lower port nbr in position tuple[1]. This will avoid duplicates.
                        result = (ip_pkt.p, transport.sport, transport.dport)
                    else:
                        result = (ip_pkt.p, transport.dport, transport.sport)

            except AttributeError as ex:
                print "Exception at time", '{0:.10f}'.format(timestamp), ", ERROR:", ex
                result = (ip_pkt.p, None, None)
    else:
        result = (ip_pkt.p, None, None)

    return result


def _scan_trace_ports(input_pcap):
    """
    Reads a pcap file returns a list of tuples. Each tuple is a unique (IP_PROTO, LOW_PORT, HIGH_PORT) where LOW_PORT
    and HIGH_PORT are both UDP/TCP ports and LOW_PORT is simply a smaller number than HIGH_PORT. The latter happens to
    avoid the duplicate (IP_PROTO, HIGH_PORT, LOW_PORT)
    """
    scan = set()

    pcap_loader = read_pcap_file(input_pcap)

    for time, buf in pcap_loader:
        result = _get_ip_pkt_ports(buf, pcap_loader.datalink(), time)
        if result is None:
            continue
        scan.add(result)

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
        if (low_port, high_port) == (-1, -1):
            # FIXME: This handles IP Fragments
            apps[(ip_proto, low_port)] = _getprotobynumber(ip_proto) + "-fragment"

        if ip_proto in [dpkt.ip.IP_PROTO_TCP, dpkt.ip.IP_PROTO_UDP]:
            # TCP or UDP packet

            # Check if low_port is already cached (i.e., added to apps dict. If yes, continue to next iteration.
            if (ip_proto, low_port) in apps.keys():
                continue

            # Since low_port not cached, check if IANA has assigned this port to an application.
            low = _getservbyport(low_port, ip_proto)
            # Check if this port is both assigned by IANA and in range (1,1023). If yes, store and continue to next
            # iteration.
            if (low_port < 1024) and low:
                # This is a well-known port
                apps[(ip_proto, low_port)] = low
                continue

            # Check if high_port is already cached. If yes, continue to next iteration.
            if (ip_proto, high_port) in apps.keys():
                continue

            # Since high_port not cached, check if IANA has assigned this port to an application.
            high = _getservbyport(high_port, ip_proto)

            # Check if this port is both assigned by IANA and in range (1,1023). If yes, store and continue to next
            # iteration.
            if (high_port < 1024) and high:
                # This is a well-known port
                apps[(ip_proto, high_port)] = high
                continue

            # Last check:
            if low:
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


def _get_trace_stats(input_pcap, known_apps, n=5):
    """
    Reads a pcap file and returns a list of tuples. Each tuple represents a time window of 1-second and its values are
    the (total_number_of_bits, total_number_of_frames) during that second.
    For example, if list element 7 has value (30000, 5) this means that the input pcap has 5 frames of total 30000 bits
    during that second.
    """
    pkt_series = []
    bit_series = []
    apps_list = known_apps.values() + ['tcp-other', 'udp-other', 'app-other', 'total']

    pcap_loader = read_pcap_file(input_pcap)

    # Read frame-by-frame
    first_frame_flag = True
    pkt_counters = dict.fromkeys(apps_list, 0)
    bit_counters = dict.fromkeys(apps_list, 0)

    grand_total_pkts = dict.fromkeys(apps_list, 0)

    for timestamp, buf in pcap_loader:
        timestamp = int(timestamp)  # Floor the timestamp value, i.e., disregard milliseconds
        result = _get_ip_pkt_ports(buf, pcap_loader.datalink(), timestamp)  # (IP_PROTO, L4_LOW_PORT, L4_HIGH_PORT)
        if result is None:
            continue
        else:
            (ip_proto, low_port, high_port) = result

        # FIXME: Assumption; prioritize low_port
        if (ip_proto, low_port) in known_apps.keys():
            app = known_apps[(ip_proto, low_port)]
        elif (ip_proto, high_port) in known_apps.keys():
            app = known_apps[(ip_proto, high_port)]
        else:
            app = _getprotobynumber(ip_proto)+'-other'

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
        bit_counters[app] += len(buf) * 8  # This will also include the bits of the Layer2 header
        # Increase counters 'total per second' and 'grand total'
        pkt_counters['total'] += 1
        bit_counters['total'] += len(buf) * 8
        grand_total_pkts[app] += 1

    # Above FOR loop will miss to append the last timestamp
    pkt_series.append(pkt_counters)
    bit_series.append(bit_counters)

    # Keep counters 'total' and top N apps according to their pps
    # FIXME: Far too long code and difficult to interpret
    # FIXME: Dict does not seem to be the right choice for counters
    # FIXME: Check Counter object @ https://docs.python.org/2/library/collections.html
    popular = ['total'] + _get_popular_apps(grand_total_pkts, n)
    pkts_d = OrderedDict()
    pkts_l = []
    bits_d = OrderedDict()
    bits_l = []
    for t in xrange(0, len(pkt_series)):
        for p in popular:
            pkts_d[p] = pkt_series[t][p]  # Counter of popular app p at timeslot t
            bits_d[p] = bit_series[t][p]
        pkts_l.append(pkts_d)
        bits_l.append(bits_d)
        pkts_d = OrderedDict()
        bits_d = OrderedDict()

    print "Input trace was", len(pkts_l), "seconds long. I have summarized the results..."
    return pkts_l, bits_l


def _get_popular_apps(series_dict, n=5):
    """
    Reads a python dictionary and finds the n highest values. Returns a list with the corresponding keys.
    """
    k = series_dict.keys()
    v = series_dict.values()

    popular = nlargest(n, v)  # Find n highest values; save them to new list popular

    apps = []
    for x in popular:
        apps.append(k[v.index(x)])

    return apps


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


def _export_stats(counters_list, output_file):
    """
    Export statistics to a text file that read and plotted by Gnuplot.
    """
    # Get column names:
    if len(counters_list):
        # counters_list[0] is a Python dictionary
        columns_list = counters_list[0].keys()
    else:
        columns_list = []
        raise Exception("Input list of counters is empty, so nothing to export to file. Exiting...")

    with open(output_file, 'w') as f:
        f.write('TIME ' + ' '.join(columns_list) + '\n')
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

    scanned_ports = _scan_trace_ports(user_input['input_file'])
    print "Discovered,", len(scanned_ports), "ports (i.e., IP_PROTO, LOW_NBR_PORT, HIGH_NBR_PORT)."
    apps = _get_trace_apps(scanned_ports)
    print "Discovered", len(apps), "apps (i.e., IP_PROTO, PORT). Apps:", apps

    pps, bps = _get_trace_stats(user_input['input_file'], apps)
    # Both pps and bps are lists with index (keys) the elapsed time in seconds i.e., the x-axis of a time series.
    # Each corresponding value is a dictionary holding the pps or bps of each application during that second.
    # We are only interested in the top N apps.

    print "Exporting statistics to files..."
    # Write result to external file
    _export_stats(pps, user_input['output_file'] + '.ts.pps.dat')
    _export_stats(bps, user_input['output_file'] + '.ts.bps.dat')