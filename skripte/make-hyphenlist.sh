LC_COLLATE=de_DE.UTF-8

sort \
| uniq \
| sed -f words2tex.sed > temp.tex
lualatex temp.tex > /dev/null
#rm temp.tex temp.aux
cat temp.log \
| sed -f log2words.sed
#rm temp.log

