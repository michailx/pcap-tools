PCAP tools
=========
The tools can achieve the following tasks:
+ Split a large _.pcap_ to smaller ones. This functionality is great if the file is too big to analyze or simply
move between computers. See [split_pcap.sh][split_script].
+ Read a _.pcap_ file to discover __(i)__ L7 apps, __(ii)__ pps and bps per app, and __(iii)__ plot this data.
See [plot_ts.sh][plot_script].


Setup
----
xxxxxxx
```bash
./start.sh
```

Run
----
xxxxxxx
```bash
./start.sh
```

Directory structure
----
+ __dat__: Contains all _.dat_ files as exported by [plot_ts.sh][plot_script]. These files hold the time series data in a format that can be read by [gnuplot][gnuplot_homepage].
+ __pcap__: Contains all _.pcap_ files as exported by [split_pcap.sh][split_script]. These files can be provided as input to [plot_ts.sh][plot_script].
+ __png__: Contains all _.png_ files as exported by [plot_ts.sh][plot_script].

TODO
----
List of things __TODO__:

x

Getting help
----
Please [raise an issue][getting_help] on Github.

[getting_help]: https://github.com/michailx/pcap-tools/issues
[plot_script]: https://github.com/michailx/pcap-tools/blob/master/plot_ts.sh
[split_script]: https://github.com/michailx/pcap-tools/blob/master/split_pcap.sh
[gnuplot_homepage]: http://www.gnuplot.info/
