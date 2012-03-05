#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2012 Günter Milde.
# :Licence:   This work may be distributed and/or modified under
#             the conditions of the `LaTeX Project Public License`,
#             either version 1.3 of this license or (at your option)
#             any later  version.
# :Version:   0.1 (2012-02-15)

# sort.py
# ***********
# 
# ::

"""Sortieren der `Wortliste` nach Duden-Regeln"""

import unicodedata
from werkzeug import WordFile

# Erstelle einen Sortierschlüssel für die Zeile `line`:
#
# Sortiere nach erstem Feld, alphabetisch, gemäß Duden-Regeln.

def sortkey_duden(line):
    ersetzungen = {
                   # ord(u'ä'): u'a',
                   # ord(u'é'): u'e',
                   # ord(u'ö'): u'o',
                   # ord(u'ó'): u'o',
                   # ord(u'ü'): u'u',
                   # + weitere Akzente: -> siehe unten
                   ord(u'ß'): u'ss',
                  }
    
    # Sortieren nach erstem Feld (ungetrenntes Wort):
    key = line.split(';')[0]
    # Großschreibung ignorieren
    key = key.lower()
    # Ersetzungen
    key = key.translate(ersetzungen)
    # Akzente/Umlaute weglassen:
    key = unicodedata.normalize('NFKD', key) # Akzente mit 2-Zeichen-Kombi
    key = key.encode('ascii', 'ignore')     # ignoriere nicht-ASCII Zeichen

    return key

def sortkey_wl(line):
    ersetzungen = {ord(u'ß'): u'ss'}
    # Weglassen der Feldtrenner und Trennzeichen
    # (Simulation von `sort -d`)
    for char in u';-·=|[]{}':
        ersetzungen[ord(char)] = None
    # Sortieren nach gesamter Zeile, Großschreibung ignorieren
    key = line.lower()
    key = key.translate(ersetzungen)
    # Akzente/Umlaute weglassen:
    key = unicodedata.normalize('NFKD', key) # Akzente mit 2-Zeichen-Kombi
    key = key.encode('ascii', 'ignore')     # ignoriere nicht-ASCII Zeichen

    return key

if __name__ == '__main__':

    import difflib

    # filename = '../../wortliste-gewichtet'
    filename = '../../wortliste'
    
    # Einlesen in eine Liste von Zeilen::
    
    wordfile = WordFile(filename)
    lines = wordfile.readlines(keepends=True)
    
    # Sortieren::
    
    sortiert = sorted(lines, key=sortkey_wl)
    # sortiert = sorted(lines, key=sortkey_duden)
    
    diff = ''.join(difflib.unified_diff(lines, sortiert,
                                        filename, '*sortiert*', n=1))
    if diff:
        print diff.encode('utf8')
    else:
        print 'no differences after round trip'


# wordfile.writelines(sortiert, filename+'-sortiert')


