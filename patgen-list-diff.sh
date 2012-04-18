#!/bin/sh
#
# Dieses Skript erzeugt Differenzbilder (diff) für die
# Patgen-Eingabelisten zwischen einem angegebenen Commit und "master".
# Die Ausgabedateien werden als dehyph*-x/<commit hash>.diff in
# Verzeichnissen gespeichert, die der jeweiligen Rechtschreibung
# entsprechen.
#
# Aufruf:  sh patgen-list-diff <commit hash>
#
#
# Eingabe:  <commit hash>          Ein Git-Commit-Hash.
#
# Ausgabe:
#   dehyphn-x/<commit hash>.diff   Differenzbild refromierte Rechtschreibung
#   dehypht-x/<commit hash>.diff   Differenzbild traditionelle Rechtschreibung
#   dehyphts-x/<commit hash>.diff  Differenzbild traditionelle Rechtschreibung
#                                  in der Schweiz.
#
# Achtung: Der <commit hash> sollte nur Zeichen enthalten, welche in
#          Dateinamen zulässig sind!
#

if test $# -eq 0
then
  echo 'usage: patgen-list-diff <commit hash>'
  echo 'Create diffs for patgen input lists between <commit hash> and "master" and'
  echo 'save them as files dehyph*-x/<commit hash>.diff in directories'
  echo 'corresponding to the spelling.'
  exit 1
fi
TEMPSCRIPT=temp-patgen-list-diff.sh
echo 'if git checkout $1' > $TEMPSCRIPT
echo 'then' >> $TEMPSCRIPT
echo '  make dehyphn-x/words.hyphenated.refo' >> $TEMPSCRIPT
echo '  make dehypht-x/words.hyphenated.trad' >> $TEMPSCRIPT
echo '  make dehyphts-x/words.hyphenated.swiss' >> $TEMPSCRIPT
echo '  mv dehyphn-x/words.hyphenated.refo dehyphn-x/words.hyphenated.refo.$1' >> $TEMPSCRIPT
echo '  mv dehypht-x/words.hyphenated.trad dehypht-x/words.hyphenated.trad.$1' >> $TEMPSCRIPT
echo '  mv dehyphts-x/words.hyphenated.swiss dehyphts-x/words.hyphenated.swiss.$1' >> $TEMPSCRIPT
echo '  git checkout master' >> $TEMPSCRIPT
echo '  make dehyphn-x/words.hyphenated.refo' >> $TEMPSCRIPT
echo '  make dehypht-x/words.hyphenated.trad' >> $TEMPSCRIPT
echo '  make dehyphts-x/words.hyphenated.swiss' >> $TEMPSCRIPT
echo '  diff dehyphn-x/words.hyphenated.refo.$1 dehyphn-x/words.hyphenated.refo > dehyphn-x/$1.diff' >> $TEMPSCRIPT
echo '  diff dehypht-x/words.hyphenated.trad.$1 dehypht-x/words.hyphenated.trad > dehypht-x/$1.diff' >> $TEMPSCRIPT
echo '  diff dehyphts-x/words.hyphenated.swiss.$1 dehyphts-x/words.hyphenated.swiss > dehyphts-x/$1.diff' >> $TEMPSCRIPT
echo 'fi' >> $TEMPSCRIPT
echo 'exec rm -f ' $TEMPSCRIPT >> $TEMPSCRIPT
exec $TEMPSCRIPT $1
