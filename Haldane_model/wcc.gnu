# gnuplot version > 5.4
set encoding iso_8859_1
set terminal pdf enhanced color font ",24" size 5, 4
set output 'wcc.pdf'
unset key 
set border lw 3 
set xtics offset 0, 0.2
set xtics format "%4.1f" nomirror out 
set xlabel "k in unit of line 3 of KPLANE BULK" font ",18"
set xlabel offset 0, 0.7 
set ytics 0.5 
set ytics format "%4.1f" nomirror out
set ylabel "WCC"
set ylabel offset 2, 0.0 
set xrange [0: 1.0]
set yrange [0:1]
plot for [i=4:     4] 'wcc.dat' u 1:i w p  pt 7  ps 0.5 lc 'black'
