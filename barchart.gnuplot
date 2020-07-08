set boxwidth 0.5
set style fill solid
set xlabel 'sector address'
set ylabel 'errors in sector'
set xrange [0:300000]

set terminal png
set output fname.'.png'
plot fname.'.dat' using 1:2 with boxes t 'c2 errors'

set terminal pdf
set output fname.'.pdf'
plot fname.'.dat' using 1:2 with boxes t 'c2 errors'
