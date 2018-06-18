# PCAP tools
The tools can achieve the following tasks:
+ Split a large _.pcap_ into smaller ones. This functionality is great if the file is too big to analyze or simply
move between computers. See [split_pcap.sh][split_script].
+ Read a _.pcap_ file to discover __(i)__ L7 apps, __(ii)__ pps and bps per app, and __(iii)__ plot this data.
See [plot_ts.sh][plot_script].
+ Read a time series _.dat_ file and create a histogram. See [plot_hist.sh][plot_histogram].


## Build
In order to install all necessary programs and libraries on an Ubuntu machine, please execute script:
```bash
./build/build_dependencies.sh
```

## Run

### Split

In order to split a _.pcap_ file into smaller ones, please make sure it's stored under directory __./pcap/__. <br/>
Then execute script:  
```bash
./split_pcap.sh <INPUT_PCAP_FILENAME> <OUTPUT_PCAP_SIZE_MB>
```

e.g., 

```bash
./split_pcap.sh uliege_in.pcap 50
```

will read _uliege_in.pcap_ and split it into smaller _.pcap_ files.<br/>
Each file will be named _uliege_in-partXXX.pcap_ and will be 50MB in size.



### Plot time series

In order to read a _.pcap_ file and plot the traffic load (as already described), please make sure it's stored under
directory __./pcap/__. <br/>
Then execute script:  
```bash
./plot_ts.sh <INPUT_PCAP_FILENAME>
```

e.g., 

```bash
./plot_ts.sh uliege_in.pcap
```

will read _uliege_in.pcap_ and create __two__ plot files; _uliege_in.ts.bps.png_ and _uliege_in.ts.pps.png_



### Histogram of time series

In order to produce a histogram of the time series (as already described), please execute script:  
```bash
./plot_ts.sh <INPUT_TS_FILE> <OPTIONAL_X_AXIS_SCALE>
```

e.g., 

```bash
./plot_hist.sh uliege_in.ts.bps.dat mega
```

will read _uliege_in.ts.bps.dat_ and create a histogram _uliege_in.histogram.megabps.png_ where x-axis is in mega bps.
<br/>If the second input argument (e.g., mega) was omitted, the x-axis would have been bps instead. 



## Directory structure
+ __dat__: Contains all _.dat_ files as exported by [plot_ts.sh][plot_script] and [plot_hist.sh][plot_histogram].
+ __pcap__: Contains all _.pcap_ files as exported by [split_pcap.sh][split_script]. Input _.pcap_ files should be
placed here as well.
+ __png__: Contains all _.png_ files as exported by [plot_ts.sh][plot_script] and [plot_hist.sh][plot_histogram].

## TODO
List of things __TODO__:

x

## Getting help
Please [raise an issue][getting_help] on Github.

[getting_help]: https://github.com/michailx/pcap-tools/issues
[plot_script]: https://github.com/michailx/pcap-tools/blob/master/plot_ts.sh
[plot_histogram]: https://github.com/michailx/pcap-tools/blob/master/plot_hist.sh
[split_script]: https://github.com/michailx/pcap-tools/blob/master/split_pcap.sh
[gnuplot_homepage]: http://www.gnuplot.info/
