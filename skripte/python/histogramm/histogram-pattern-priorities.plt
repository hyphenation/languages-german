set nokey
set grid
set xrange [-1:]
set yrange [1:]
set x2range [-1:]
set x2tics rotate by 90
set mytics 10
set logscale y 10
set boxwidth .5
set term png size 1024 font 'FreeSerif'

set title "Prioritäten-Histogramm der deutschen Trennmuster (von DANTE e.V.)"
set xlabel 'Zeichen'
set ylabel 'Frequenz'
set output 'histogram-musterprioritaeten.png'
plot 'histogram-pattern-priorities.tsv' \
       using 3:xticlabels(2) w boxes fs solid lt rgb '#630000', \
     '' using 1:x2ticlabels(3) w d lt rgb '#630000'

set title "Histogram of priorities in German hyphenation pattern definitions by Dante"
set xlabel 'character'
set ylabel 'frequency'
set output 'histogram-pattern-priorities.png'
plot 'histogram-pattern-priorities.tsv' \
       using 3:xticlabels(2) w boxes fs solid lt rgb '#630000', \
     '' using 1:x2ticlabels(3) w d lt rgb '#630000'
