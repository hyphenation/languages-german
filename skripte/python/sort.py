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
from werkzeug import WordFile, udiff

# Sortierschlüssel für Eintrag `entry`:
#
# Sortiere nach erstem Feld, alphabetisch, gemäß Duden-Regeln::


def sortkey_duden(entry):
    # Sortieren nach erstem Feld (ungetrenntes Wort):
    key = entry[0]
    # Großschreibung ignorieren
    key = key.lower()
    # Ersetzungen
    ersetzungen = {ord(u'ß'): u'ss'}
    key = key.translate(ersetzungen)
    # Akzente/Umlaute weglassen:
    key = unicodedata.normalize('NFKD', key) # Akzente mit 2-Zeichen-Kombi
    key = key.encode('ascii', 'ignore')     # ignoriere nicht-ASCII Zeichen

    return key

# Sortiere nach dem bisher genutzten ("Lemberg-") Algorithmus::

def sortkey_wl(entry):
    # Sortieren nach gesamter Zeile
    key = unicode(entry) 
    
    # Ersetzungen:
    ersetzungen = {ord(u'ß'): u'ss'}
    # Weglassen der Feldtrenner und Trennzeichen (Simulation von `sort -d`)
    for char in u';-·=|[]{}':
        ersetzungen[ord(char)] = None
    key = key.translate(ersetzungen)
    
    # Akzente/Umlaute weglassen:
    key = unicodedata.normalize('NFKD', key) # Akzente mit 2-Zeichen-Kombi
    key = key.encode('ascii', 'ignore')     # ignoriere nicht-ASCII Zeichen
    # Großschreibung ignorieren
    key = key.lower()

    return key

if __name__ == '__main__':

    # filename = '../../wortliste-gewichtet'
    filename = '../../wortliste'
    
    # Einlesen in eine Liste von Zeilen::
    
    wortfile = WordFile(filename)
    wortliste = list(wortfile)
    
    # Sortieren::
    
    sortiert = sorted(wortliste, key=sortkey_wl)
    # sortiert = sorted(wortliste, key=sortkey_duden)
    
    patch = udiff(wortliste, sortiert, 'wortliste', 'wortliste-sortiert')
    if patch:
        print patch
        patchfile = open('../../wortliste.patch', 'w')
        patchfile.write(patch + '\n')
    else:
        print 'keine Änderungen'


