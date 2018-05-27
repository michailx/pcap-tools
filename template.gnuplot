# Gnuplot script file for plotting time series data

# print "script name        : ", ARG0
# print "number of arguments: ", ARGC

INTPUT_DATA=ARG1  # the data file which I will read for data
OUTPUT_PNG=ARG2   # the filename to use when storing the generated plot (in png format)
SERIES_NBR=2+ARG3 # number of series to plot. Columns 'time' (x-axis) and 'total' will always be included.
YAXIS_UNIT=ARG4

set terminal png size 800,600
set output OUTPUT_PNG

# styles
set style line 1 lc rgb '#0060ad' lt 1 lw 2 pt 7 ps 1.5  # Blue color
set style line 2 lc rgb '#daa520' lt 1 lw 2 pt 7 ps 1.5  # Golden color
set style line 3 lc rgb '#7f7f7f' lt 1 lw 2 pt 7 ps 1.5  # Hoar color
set style line 4 lc rgb '#dd181f' lt 1 lw 2 pt 7 ps 1.5  # Red color
set style line 5 lc rgb '#ff00ff' lt 1 lw 2 pt 7 ps 1.5  # Magenta color
set style line 6 lc rgb '#dc3912' lt 1 lw 2 pt 7 ps 1.5  # Dark Red color

set title "Traffic bandwidth over time (".YAXIS_UNIT.")"
set xlabel "Time (seconds)"
set ylabel "Bandwidth (".YAXIS_UNIT.")"
set key autotitle columnheader
set style data points
plot for [i=2:SERIES_NBR] INTPUT_DATA using 1:i with points ls i-1