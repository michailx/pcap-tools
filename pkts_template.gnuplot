# Gnuplot script file for plotting time series data

# print "script name        : ", ARG0
# print "number of arguments: ", ARGC

INTPUT_DATA=ARG1  # the data file which I will read for data
OUTPUT_PNG=ARG2   # the filename to use when storing the generated plot (in png format)

set terminal png size 800,600
set output OUTPUT_PNG
set style line 1 lc rgb '#dd181f' lt 1 lw 2 pt 5 ps 1.5  # Red color
set title "Traffic bandwidth over time (pps)"
set xlabel "Time (seconds)"
set ylabel "Bandwidth (packets)"
plot INTPUT_DATA using 1:3 notitle with linespoints ls 1