# PCAP tools
The tools can achieve the following tasks:
+ Split a large _.pcap_ into smaller ones. This functionality is great if the file is too big to analyze or simply
move between computers. See [split_pcap.sh][split_script].
+ Merge several _.pcap_ files into one (_.pcap_ file), while rearranging the packets according to their timestamps.
move between computers. See [merge_pcap.sh][merge_script].
+ Read a _.pcap_ file to discover __(i)__ L7 apps, __(ii)__ pps and bps per app, and __(iii)__ plot this data.
See [plot_ts.sh][plot_script].
+ Read a time series _.dat_ file and create a histogram. See [plot_hist.sh][plot_histogram].


## Build
In order to install all necessary programs and libraries on an Ubuntu machine, please execute script:
```bash
./build/build_dependencies.sh
```

## Run


### Split PCAP

In order to split a _.pcap_ file into smaller ones, please make sure it's stored under directory __./pcap/__. <br/>
Then execute script [split_pcap.sh][split_script] with the following two input arguments:

```bash
./split_pcap.sh INPUT_PCAP_FILENAME OUTPUT_PCAP_SIZE_MB
```

E.g., 

```bash
./split_pcap.sh uliege_in.pcap 50
```

will read _uliege_in.pcap_ and split it into smaller _.pcap_ files.<br/>
Each file will be named _uliege_in-partXXX.pcap_ and will be 50MB in size.


### Merge PCAP

In order to merge several _.pcap_ files into one (as already described), please execute script
[merge_pcap.sh][merge_script] with the following two input arguments:

```bash
./merge_pcap.sh PCAP_FILES_DIRECTORY DESIRED_FILENAME_FOR_OUTPUT
```

E.g., 

```bash
./merge_pcap.sh ./pcap merged_trace.pcap
```

will create a new _.pcap_ file named _merged_trace.pcap_ by merging all _.pcap_ files under directory _./pcap/_<br/>
The new file, _merged_trace.pcap_, will be stored in the current directory (i.e., ./)


### Plot time series

In order to read a _.pcap_ file and plot the traffic load (as already described), please make sure it's stored under
directory __./pcap/__ <br/>
Then execute script [plot_ts.sh][plot_script] with the following two input arguments:  
```bash
./plot_ts.sh INPUT_PCAP_FILENAME
```

E.g., 

```bash
./plot_ts.sh uliege_in.pcap
```

will read _uliege_in.pcap_ and create __two__ plot files; _uliege_in.ts.bps.png_ and _uliege_in.ts.pps.png_


### Histogram of time series

In order to produce a histogram of the time series (as already described), please execute script [plot_hist.sh][plot_histogram]
with the following input argument(s):  

```bash
./plot_ts.sh INPUT_TS_FILE OPTIONAL_X_AXIS_SCALE
```
The second argument is __optional__!

E.g., 

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
[merge_script]: https://github.com/michailx/pcap-tools/blob/master/merge_pcap.sh
[gnuplot_homepage]: http://www.gnuplot.info/
