#!/bin/sh
#
# merge-wordlists.sh
#
# Fügt mehrere Wortlisten zu einer sortierten Gesamtliste der einfachen
# (ungetrennten) Wörter)zusammen.
# 
# Eingabe: ein oder mehrere Dateinamen.
# Ausgabe ist nach stdout.

LANG=de_DE.utf-8
export LANG

cat $@ \
| sed -e '/^#/d' \
      -e 's/     /\
/' \
| sed -e 's/;.*//' \
      -e 's/[-=·.|]//g' \
| sort \
| uniq -i

# eof