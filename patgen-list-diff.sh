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
if git checkout $1
then
  make dehyphn-x/words.hyphenated.refo
  make dehypht-x/words.hyphenated.trad
  make dehyphts-x/words.hyphenated.swiss
  mv dehyphn-x/words.hyphenated.refo dehyphn-x/words.hyphenated.refo.$1
  mv dehypht-x/words.hyphenated.trad dehypht-x/words.hyphenated.trad.$1
  mv dehyphts-x/words.hyphenated.swiss dehyphts-x/words.hyphenated.swiss.$1
  git checkout master
  make dehyphn-x/words.hyphenated.refo
  make dehypht-x/words.hyphenated.trad
  make dehyphts-x/words.hyphenated.swiss
  diff dehyphn-x/words.hyphenated.refo.$1 dehyphn-x/words.hyphenated.refo > dehyphn-x/$1.diff
  diff dehypht-x/words.hyphenated.trad.$1 dehypht-x/words.hyphenated.trad > dehypht-x/$1.diff
  diff dehyphts-x/words.hyphenated.swiss.$1 dehyphts-x/words.hyphenated.swiss > dehyphts-x/$1.diff
fi
