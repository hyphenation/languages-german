#!/bin/sh
# -*- coding: utf-8 -*-
#
# Dieses Skript erzeugt Differenzbilder (diff) für die
# Patgen-Eingabelisten zwischen zwei angegebenen Commits.  Wird nur ein
# Commit angegeben, wird als Zielcommit "master" verwendet.  Die
# Ausgabedateien werden als Dateien
#
#   dehyph*-x/<Start-Commit-Hash>-<Ziel-Commit-Hash>.diff
#
# in Verzeichnissen gespeichert, die der jeweiligen Rechtschreibung
# entsprechen.  Start- und Ziel-Commit können in jeder gültigen
# Git-Syntax angegeben werden.  Für die Dateinamen werden die
# entsprechenden abgekürzten alphanumerischen Commit-Hashes
# verwendet.
#
# Aufruf:  sh patgen-list-diff.sh <start commit> [<ziel commit>]
#
#
# Eingabe:  <start commit>      Ein Start-Commit.
#           <ziel commit>       Ein optionaler Ziel-Commit.
#
# Ausgabe:
#   dehyphn-x/<hashes>.diff     Differenzbild refromierte Rechtschreibung
#   dehypht-x/<hashes>.diff     Differenzbild traditionelle Rechtschreibung
#   dehyphts-x/<hashes>.diff    Differenzbild traditionelle Rechtschreibung
#                               in der Schweiz.
#
if test $# -eq 0
then
  echo 'usage: patgen-list-diff <start commit> [<target commit>]'
  echo 'Create diffs for patgen input lists between <start commit> and'
  echo '<target commit> (by default "master") and save them as files'
  echo 'dehyph*-x/<start commit hash>-<target commit hash>.diff in'
  echo 'directories corresponding to the spelling.'
  exit 1
fi
FROMCOMMIT=$1
if test $# -eq 1
then
  TOCOMMIT=master
else
  TOCOMMIT=$2
fi
FROMHASH=$(git log -1 --format=%h $FROMCOMMIT)
if test -z $FROMHASH
then
  echo 'patgen-list-diff.sh: error identifying start commit hash: ' $FROMCOMMIT
  exit 1
fi
TOHASH=$(git log -1 --format=%h $TOCOMMIT)
if test -z $TOHASH
then
  echo 'patgen-list-diff.sh: error identifying target commit hash: ' $TOCOMMIT
  exit 1
fi
echo "Diff'ing patgen input files between commits $FROMHASH ($FROMCOMMIT) and $TOHASH ($TOCOMMIT)."
TEMPSCRIPT=temp-patgen-list-diff.sh
(
    echo 'if git checkout $1'
    echo 'then'
    echo '  make dehyphn-x/words.hyphenated.refo'
    echo '  make dehypht-x/words.hyphenated.trad'
    echo '  make dehyphts-x/words.hyphenated.swiss'
    echo '  mv dehyphn-x/words.hyphenated.refo dehyphn-x/words.hyphenated.refo.$1'
    echo '  mv dehypht-x/words.hyphenated.trad dehypht-x/words.hyphenated.trad.$1'
    echo '  mv dehyphts-x/words.hyphenated.swiss dehyphts-x/words.hyphenated.swiss.$1'
    echo '  git checkout $2'
    echo '  make dehyphn-x/words.hyphenated.refo'
    echo '  make dehypht-x/words.hyphenated.trad'
    echo '  make dehyphts-x/words.hyphenated.swiss'
    echo '  diff dehyphn-x/words.hyphenated.refo.$1 dehyphn-x/words.hyphenated.refo > dehyphn-x/$1-$2.diff'
    echo '  diff dehypht-x/words.hyphenated.trad.$1 dehypht-x/words.hyphenated.trad > dehypht-x/$1-$2.diff'
    echo '  diff dehyphts-x/words.hyphenated.swiss.$1 dehyphts-x/words.hyphenated.swiss > dehyphts-x/$1-$2.diff'
    echo '  gawk -f patgen-list-diff.awk -v ftr=daten/german.tr dehyphn-x/$1-$2.diff'
    echo '  gawk -f patgen-list-diff.awk -v ftr=daten/german.tr dehypht-x/$1-$2.diff'
    echo '  gawk -f patgen-list-diff.awk -v ftr=daten/german.tr dehyphts-x/$1-$2.diff'
    echo 'fi'
    echo 'exec rm -f ' $TEMPSCRIPT
) > $TEMPSCRIPT
exec $TEMPSCRIPT $FROMHASH $TOHASH
