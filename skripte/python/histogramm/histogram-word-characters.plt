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

set title "Zeichen-Histogramm der Wörter in den deutschen Trennmustern (von DANTE e.V.)"
set xlabel 'Zeichen'
set ylabel 'Frequenz'
set output 'histogram-wortzeichen.png'
plot 'histogram-word-characters.tsv' \
       using 3:xticlabels(2) w boxes fs solid lt rgb '#630000', \
     '' using 1:x2ticlabels(3) w d lt rgb '#630000'

set title "Histogram of characters of German words by Dante"
set xlabel 'character'
set ylabel 'frequency'
set output 'histogram-word-characters.png'
plot 'histogram-word-characters.tsv' \
       using 3:xticlabels(2) w boxes fs solid lt rgb '#630000', \
     '' using 1:x2ticlabels(3) w d lt rgb '#630000'
