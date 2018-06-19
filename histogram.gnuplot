# Gnuplot script file for plotting time series data

# print "script name        : ", ARG0
# print "number of arguments: ", ARGC

INTPUT_DATA=ARG1  # the data file which I will read for data
OUTPUT_PNG=ARG2   # the filename to use when storing the generated plot (in png format)
X_STAT_PROP=ARG3  # statistical properties of series (x-axis)
X_AXIS_UNIT=ARG4  # unit for x-axis, e.g., bps

set terminal png size 1024,768
set output OUTPUT_PNG

# styles
set style line 1 lc rgb '#dc3912' lt 1 lw 1 pt 9 ps 1.25  # Dark Red color

set title "Histogram of observed traffic load (".X_AXIS_UNIT.")\n".X_STAT_PROP."
set xlabel "Traffic load (".X_AXIS_UNIT.")"
set xtic rotate by -45 scale 0
set ylabel "Count"
set grid
set key off
set style data histogram
set boxwidth 0.95 relative
set style fill solid border -1
plot INTPUT_DATA using 2:xtic(1) ls 1 with boxes