# wird von make-hyphenlist.sh verwendet. Die Pattern-Variante in Zl. 5
# muß angepaßt werden.
#
# \\usepackage{xltxtra}\

1 i\
\\documentclass{article}\
\\usepackage[german]{babel}\
\
\\begin\{document\}

/^AAAAAAAA/ d
s|^\(.*\)$|\\showhyphens{\0}|
$a\
\\end\{document\}

