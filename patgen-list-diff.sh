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
FROMHASH=`git log -1 --format=%H $FROMCOMMIT`
if test -z $FROMHASH
then
  echo 'patgen-list-diff.sh: error identifying start commit hash: ' $FROMCOMMIT
  exit 1
fi
TOHASH=`git log -1 --format=%H $TOCOMMIT`
if test -z $TOHASH
then
  echo 'patgen-list-diff.sh: error identifying target commit hash: ' $TOCOMMIT
  exit 1
fi



# Function definition.  If not already present, place a copy of a
# commit's working copy in a directory 'wl-<commit hash>'.
get_working_copy() {
    typeset commit=$1
    typeset commitdir=wl-$commit
    if test ! -d $commitdir
    then
        git archive --format=tar --prefix=$commitdir/ $commit | tar xf -
    fi
}

# Function definition.
create_patgen_list() {
    typeset commit=$1 patgenlist=$2
    typeset commitdir=wl-$commit
    if test ! -e $commitdir/$patgenlist
    then
        # 'make -C $commitdir $patgenlist' doesn't work reliably on Git
        # for Windows shell.
        (cd $commitdir && make $patgenlist)
    fi
}

# Function definition.
diff_patgen_list() {
    typeset fromcommit=$1 tocommit=$2 dehyph=$3 spell=$4
    typeset fromcommitdir=wl-$fromcommit tocommitdir=wl-$tocommit patgenlist=$dehyph/words.hyphenated.$spell difffile=${fromcommit:0:7}-${tocommit:0:7}.diff
    create_patgen_list $fromcommit $patgenlist
    create_patgen_list $tocommit $patgenlist
    if test ! -d $dehyph; then mkdir $dehyph; fi
    diff $fromcommitdir/$patgenlist $tocommitdir/$patgenlist > $dehyph/$difffile
    gawk -f patgen-list-diff.awk -v ftr=daten/german.tr $dehyph/$difffile
}



echo "Diff'ing patgen input files between commits $FROMHASH ($FROMCOMMIT) and $TOHASH ($TOCOMMIT)."
# Get commit's working copies.
get_working_copy $FROMHASH
get_working_copy $TOHASH
# Write header to summary table file.
PLDTABLE=CHANGES.table.txt
echo "      Rechtschreibung         hinzugefügt   entfernt   korrigiert" > $PLDTABLE
echo "    ---------------------------------------------------------------" >> $PLDTABLE
# Diff patgen lists and write results to summary table file.
echo -n "      traditionell (DE, AT)" >> $PLDTABLE
diff_patgen_list $FROMHASH $TOHASH dehypht-x trad
echo -n "      traditionell (CH)    " >> $PLDTABLE
diff_patgen_list $FROMHASH $TOHASH dehyphts-x swiss
echo -n "      reformiert           " >> $PLDTABLE
diff_patgen_list $FROMHASH $TOHASH dehyphn-x refo
