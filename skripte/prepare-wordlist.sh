LC_COLLATE=de_DE.UTF8

#     $ sh prepare-wordlist.sh < Textdatei
#
# listet alle Wörter mit mindestens vier Buchstaben, die keine römischen 
# Zahlen sind, aus einer gegebenen Textdatei auf und …
#
#     $ sh prepare-wordlist.sh < Textdatei | grep -Fixvf Prüfliste
# 
# … prüft sie gegen eine ebenfalls gegebene Prüfliste:

sed -f ~/git/tl-script/strippunct.sed \
| sed '/..../!d' \
| sort -i \
| uniq -i
