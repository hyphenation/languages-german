#!/bin/sh
#
# Dieses Skript erzeugt Differenzbilder (diff) für die
# Patgen-Eingabelisten zwischen einem angegebenen Commits und "master".
# Die Ausgabedateien werden als Dateien
#
#   dehyph*-x/<commit hash>.diff
#
# in Verzeichnissen gespeichert, die der jeweiligen Rechtschreibung
# entsprechen.  Der Commit kann in jeder gültigen Git-Syntax angegeben
# werden.  Für die Dateinamen wird der entsprechende abgekürzte
# alphanumerische Commit-Hash verwendet.
#
# Aufruf:  sh patgen-list-diff.sh <commit>
#
#
# Eingabe:  <commit>               Ein Git-Commit.
#
# Ausgabe:
#   dehyphn-x/<commit hash>.diff   Differenzbild refromierte Rechtschreibung
#   dehypht-x/<commit hash>.diff   Differenzbild traditionelle Rechtschreibung
#   dehyphts-x/<commit hash>.diff  Differenzbild traditionelle Rechtschreibung
#                                  in der Schweiz.
#
if test $# -eq 0
then
  echo 'usage: patgen-list-diff <commit>'
  echo 'Create diffs for patgen input lists between <commit> and "master" and'
  echo 'save them as files dehyph*-x/<commit hash>.diff in directories'
  echo 'corresponding to the spelling.'
  exit 1
fi
FROMCOMMIT=$1
FROMHASH=$(git log -1 --format=%h $FROMCOMMIT)
if test -z $FROMHASH
then
  echo 'patgen-list-diff.sh: error identifying commit hash: ' $FROMCOMMIT
  exit 1
fi
echo "Diff'ing patgen input files between commits $FROMHASH ($FROMCOMMIT) and master."
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
exec $TEMPSCRIPT $FROMHASH
