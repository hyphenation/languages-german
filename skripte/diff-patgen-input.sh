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
# Aufruf:  sh diff-patgen-input.sh <start commit> [<ziel commit>]
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
  echo 'usage: diff-patgen-input <start commit> [<target commit>]'
  echo ''
  echo 'Create diffs for patgen input lists between <start commit> and'
  echo '<target commit> (by default "master") and save them as files'
  echo 'dehyph*-x/<start commit hash>-<target commit hash>.diff in'
  echo 'directories corresponding to the spelling.'
  exit 1
fi
FROMCOMMIT=$1
if test $# -eq 1
then
  TOCOMMIT=HEAD
else
  TOCOMMIT=$2
fi
typeset GITDATA=`git log -1 --format=%ci-%H $FROMCOMMIT --`
FROMDATE=${GITDATA:0:10}+${GITDATA:11:2}-${GITDATA:14:2}-${GITDATA:17:2}
FROMHASH=${GITDATA:26}
if test -z $FROMHASH
then
  echo 'diff-patgen-input.sh: error identifying start commit hash: ' $FROMCOMMIT
  exit 1
fi
typeset GITDATA=`git log -1 --format=%ci-%H $TOCOMMIT --`
TODATE=${GITDATA:0:10}+${GITDATA:11:2}-${GITDATA:14:2}-${GITDATA:17:2}
TOHASH=${GITDATA:26}
if test -z $TOHASH
then
  echo 'diff-patgen-input.sh: error identifying target commit hash: ' $TOCOMMIT
  exit 1
fi
# Change to repository root directory.  Double quotes are intentional to
# avoid an empty argument to cd.
cd "`git rev-parse --show-toplevel`"
# Write all output to a single top-level directory.
typeset OUTPUTDIR="+++diff-patgen-input+++"



# Function definition.  If not already present, place a copy of a
# commit's working copy in a directory 'wl-<commit hash>'.
get_working_copy() {
    typeset commit=$1 commitdate=$2
    typeset commitdir=${OUTPUTDIR}/$commitdate-$commit
    if test ! -d $commitdir
    then
        git archive --format=tar --prefix=$commitdir/ $commit | tar xf -
    fi
}

# Function definition.
create_patgen_list() {
    typeset commit=$1 commitdate=$2 patgenlist=$3
    typeset commitdir=${OUTPUTDIR}/$commitdate-$commit
    echo "Making ${commit:0:7} file $patgenlist."
    if test ! -e $commitdir/$patgenlist
    then
        # 'make -C $commitdir $patgenlist' doesn't work reliably on Git
        # for Windows shell.
        (cd $commitdir && make $patgenlist > /dev/null)
    fi
}

# Function definition.
diff_patgen_list() {
    typeset fromcommit=$1 fromcommitdate=$2 tocommit=$3 tocommitdate=$4 dehyph=$5 spell=$6
    typeset fromcommitdir=${OUTPUTDIR}/$fromcommitdate-$fromcommit tocommitdir=${OUTPUTDIR}/$tocommitdate-$tocommit patgenlist=$dehyph/words.hyphenated.$spell difffile=${fromcommit:0:7}-${tocommit:0:7}.diff
    create_patgen_list $fromcommit $fromcommitdate $patgenlist
    create_patgen_list $tocommit $tocommitdate $patgenlist
    if test ! -d ${OUTPUTDIR}/$dehyph; then mkdir ${OUTPUTDIR}/$dehyph; fi
    diff $fromcommitdir/$patgenlist $tocommitdir/$patgenlist > ${OUTPUTDIR}/$dehyph/$difffile
    gawk -f skripte/diff-patgen-input.awk -v ftr=daten/german.tr ${OUTPUTDIR}/$dehyph/$difffile
}

# Function definition.
count_differences() {
    typeset fromcommit=$1 tocommit=$2 dehyph=$3 variety=$4 summaryfile=$5
    typeset difffile=${fromcommit:0:7}-${tocommit:0:7}.diff
    n_added=`wc -l ${OUTPUTDIR}/$dehyph/$difffile.added`
    n_added=${n_added%% *}
    n_removed=`wc -l ${OUTPUTDIR}/$dehyph/$difffile.removed`
    n_removed=${n_removed%% *}
    n_hyph=`wc -l ${OUTPUTDIR}/$dehyph/$difffile.hyph`
    n_hyph=${n_hyph%% *}
    printf "      %-21s   %11d   %8d   %10d\n" "${variety}" $n_added $n_removed $n_hyph >> ${summaryfile}
}




echo "Diff'ing patgen input files."
printf "from: %7s  %10s  %s\n" ${FROMHASH:0:7} ${FROMDATE:0:10} $FROMCOMMIT
printf "to:   %7s  %10s  %s\n" ${TOHASH:0:7}   ${TODATE:0:10}   $TOCOMMIT
# Get commit's working copies.
get_working_copy $FROMHASH $FROMDATE
get_working_copy $TOHASH $TODATE
# Diff patgen lists.
diff_patgen_list $FROMHASH $FROMDATE $TOHASH $TODATE dehypht-x trad
diff_patgen_list $FROMHASH $FROMDATE $TOHASH $TODATE dehyphts-x swiss
diff_patgen_list $FROMHASH $FROMDATE $TOHASH $TODATE dehyphn-x refo
# Write summary file.
typeset SUMMARYFILE=${OUTPUTDIR}/CHANGES.table.txt
echo "      Rechtschreibung         hinzugefügt   entfernt   korrigiert" > $SUMMARYFILE
echo "    ---------------------------------------------------------------" >> $SUMMARYFILE
count_differences $FROMHASH $TOHASH dehypht-x "traditionell (DE, AT)" $SUMMARYFILE
count_differences $FROMHASH $TOHASH dehyphts-x "traditionell (CH)" $SUMMARYFILE
count_differences $FROMHASH $TOHASH dehyphn-x "reformiert" $SUMMARYFILE
