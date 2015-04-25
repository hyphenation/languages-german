LC_COLLATE=de_DE.UTF8

#     $ sh prepare-wordlist.sh < Textdatei
#
# listet alle Wörter mit mindestens vier Buchstaben, die keine römischen 
# Zahlen sind, aus einer gegebenen Textdatei auf und …
#
#     $ sh prepare-wordlist.sh < Textdatei | grep -Fixvf Prüfliste
# 
# … prüft sie gegen eine ebenfalls gegebene Prüfliste:

p=$(echo $0 | sed "s|\(.*\)/.*|\1|")  # der Pfad zu den Skripten

sed -f $p/strippunct.sed \
| sed '/..../!d' \
| sort -i \
| uniq -i
