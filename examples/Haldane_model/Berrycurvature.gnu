set encoding iso_8859_1
set terminal  pngcairo  truecolor enhanced size 3680, 1920 font ",40"
#set terminal  png       truecolor enhanced size 3680, 1920 font ",40"
set output 'Berrycurvature.png'
if (!exists("MP_LEFT"))   MP_LEFT = .12
if (!exists("MP_RIGHT"))  MP_RIGHT = .92
if (!exists("MP_BOTTOM")) MP_BOTTOM = .12
if (!exists("MP_TOP"))    MP_TOP = .88
if (!exists("MP_GAP"))    MP_GAP = 0.08
set label 1 "Sum over all bands below Occupied'th band " at screen 0.5 ,0.98 center
set multiplot layout 1,3 rowsfirst \
              margins screen MP_LEFT, MP_RIGHT, MP_BOTTOM, MP_TOP spacing screen MP_GAP
 
set palette rgbformulae 33,13,10
unset ztics
unset key
set pm3d
#set zbrange [ -10: 10] 
set cbrange [ -0.324E+01: 0.244E+01 ] 
set view map
set size ratio -1
set border lw 3
set xlabel 'k (1/{\305})'
set ylabel 'k (1/{\305})'
unset colorbox
#unset xtics
#unset xlabel
set xrange [] noextend
set yrange [] noextend
set ytics 0.5 nomirror scale 0.5
set pm3d interpolate 2,2
set title 'Berry Curvature {/Symbol W}_x ({\305}^2)'
splot 'Berrycurvature.dat' u 4:5:7 w pm3d
unset ylabel
unset ytics
set title 'Berry Curvature {/Symbol W}_y ({\305}^2)'
splot 'Berrycurvature.dat' u 4:5:8 w pm3d
set title 'Berry Curvature {/Symbol W}_z ({\305}^2)'
set colorbox
splot 'Berrycurvature.dat' u 4:5:9 w pm3d
unset multiplot
unset label 1
set label 2 "Sum over all bands below Fermi level E\\_arc" at screen 0.5 ,0.98 center
set output 'Berrycurvature_EF.png'
set multiplot layout 1,3 rowsfirst \
              margins screen MP_LEFT, MP_RIGHT, MP_BOTTOM, MP_TOP spacing screen MP_GAP
set cbrange [ -0.324E+01: 0.244E+01 ] 
set title 'Berry Curvature {/Symbol W}_x ({\305}^2)'
splot 'Berrycurvature.dat' u 4:5:10 w pm3d
unset ylabel
unset ytics
set title 'Berry Curvature {/Symbol W}_y ({\305}^2)'
splot 'Berrycurvature.dat' u 4:5:11 w pm3d
set title 'Berry Curvature {/Symbol W}_z ({\305}^2)'
set colorbox
splot 'Berrycurvature.dat' u 4:5:12 w pm3d
