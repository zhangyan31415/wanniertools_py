# requirement: gnuplot version>5.4
set encoding iso_8859_1
#set terminal  postscript enhanced color
#set output 'slabek.eps'
#set terminal  pngcairo truecolor enhanced  font ",60" size 1920, 1680
set terminal  png truecolor enhanced  font ",60" size 1920, 1680
set output 'slabek.png'
set palette defined ( 0  "green", 5 "yellow", 10 "red" )
set style data linespoints
unset ztics
unset key
set pointsize 0.8
set border lw 3 
set view 0,0
#set xtics font ",36"
#set ytics font ",36"
#set ylabel font ",36"
#set xtics offset 0, -1
set ylabel offset -0.5, 0 
set xrange [0:    2.54543]
set ylabel "Energy (eV)"
set yrange [  -3.50577:   3.50577]
set xtics ("  0"    0.00000,"  1"    2.54543)
#rgb(r,g,b) = int(r)*65536 + int(g)*256 + int(b)
#plot 'slabek.dat' u 1:2:(rgb(255,$3, 3)) w lp lw 2 pt 7  ps 1 lc rgb variable
# (a) 
# plot the top and bottom surface's weight together
#plot 'slabek.dat' u 1:2:($3+$4) w lp lw 2 pt 7  ps 1 lc palette
# (b) 
# plot top and bottom surface's weight with red and blue respectively
set palette defined ( -1  "blue", 0 "grey", 1 "red" )
plot 'slabek.dat' u 1:2:($4-$3) w lp lw 2 pt 7  ps 1 lc palette
