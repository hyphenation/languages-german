LC_COLLATE=de_DE.UTF-8

p=$(echo $0 | sed "s|\(.*\)/.*|\1|")  # der Pfad zu den Skripten

sort \
| uniq \
| sed -f $p/words2tex.sed > temp.tex
lualatex temp.tex > /dev/null
#rm temp.tex temp.aux
cat temp.log \
| sed -f log2words.sed
#rm temp.log

