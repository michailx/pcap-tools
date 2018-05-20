# Gnuplot script file for plotting time series data

# print "script name        : ", ARG0
# print "number of arguments: ", ARGC

INTPUT_DATA=ARG1  # the data file which I will read for data
OUTPUT_PNG=ARG2   # the filename to use when storing the generated plot (in png format)

set terminal png size 800,600
set output OUTPUT_PNG
set style line 1 lc rgb '#0060ad' lt 1 lw 2 pt 7 ps 1.5  # Blue color
set title "Traffic bandwidth over time (kbps)"
set xlabel "Time (seconds)"
set ylabel "Bandwidth (kbits)"
plot INTPUT_DATA using 1:2 notitle with linespoints ls 1