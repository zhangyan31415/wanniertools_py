set encoding iso_8859_1
#set terminal  postscript enhanced color
#set output 'bulkek_plane.eps'
set terminal  png truecolor enhanced size 1920, 1680 font ",36"
set output 'bulkek_plane.png'
set palette rgbformulae 33,13,10
unset key
set pm3d
set origin 0.2, 0
set size 0.8, 1
set border lw 3
#set xtics font ",24"
#set ytics font ",24"
set size ratio -1
set ticslevel 0
unset xtics
unset ytics
set view 80,60
set xlabel "k_1"
set ylabel "k_2"
set zlabel "Energy (eV)" rotate by 90
unset colorbox
set autoscale fix
set pm3d interpolate 4,4
splot 'bulkek_plane.dat' u 4:5:8 w pm3d, \
      'bulkek_plane.dat' u 4:5:9 w pm3d
