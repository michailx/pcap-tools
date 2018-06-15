# PCAP tools
The tools can achieve the following tasks:
+ Split a large _.pcap_ into smaller ones. This functionality is great if the file is too big to analyze or simply
move between computers. See [split_pcap.sh][split_script].
+ Read a _.pcap_ file to discover __(i)__ L7 apps, __(ii)__ pps and bps per app, and __(iii)__ plot this data.
See [plot_ts.sh][plot_script].


## Build
In order to install all necessary programs and libraries on an Ubuntu machine, please execute script:
```bash
./build/build_dependencies.sh
```

## Run

### Split

In order to split a _.pcap_ file into smaller ones, please execute script:  
```bash
./split_pcap.sh pcap/<INPUT_PCAP_FILENAME> <OUTPUT_PCAP_FILENAME_SUFFIX> <OUTPUT_PCAP_SIZE_MB>
```

e.g., 

```bash
./split_pcap.sh pcap/caida-20140711-095700.UTC.pcap caida-2014 100
```

will read _caida-20140711-095700.UTC.pcap_ and split it into smaller _.pcap_ files. Each file will have the suffix
_caida-2014-partXXX_ and will be 100MB in size.



### Plot

In order to read a _.pcap_ file and plot the traffic load per app (as already described), please execute script:  
```bash
./plot_ts.sh pcap/<INPUT_PCAP_FILENAME> <OUTPUT_PNG_FILENAME_SUFFIX>
```

e.g., 

```bash
./plot_ts.sh pcap/uliege_in.pcap uliege_in
```

will read _uliege_in.pcap_ and will create __two__ plot files; _uliege_in-bps.png_ and _uliege_in-pps.png_



## Directory structure
+ __dat__: Contains all _.dat_ files as exported by [plot_ts.sh][plot_script]. These files hold the time series data in a format that can be read by [gnuplot][gnuplot_homepage].
+ __pcap__: Contains all _.pcap_ files as exported by [split_pcap.sh][split_script]. These files can be provided as input to [plot_ts.sh][plot_script].
+ __png__: Contains all _.png_ files as exported by [plot_ts.sh][plot_script].

## TODO
List of things __TODO__:

x

## Getting help
Please [raise an issue][getting_help] on Github.

[getting_help]: https://github.com/michailx/pcap-tools/issues
[plot_script]: https://github.com/michailx/pcap-tools/blob/master/plot_ts.sh
[split_script]: https://github.com/michailx/pcap-tools/blob/master/split_pcap.sh
[gnuplot_homepage]: http://www.gnuplot.info/
