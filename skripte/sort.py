#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2012 Günter Milde.
# :Licence:   This work may be distributed and/or modified under
#             the conditions of the `LaTeX Project Public License`,
#             either version 1.3 of this license or (at your option)
#             any later  version.
# :Version:   0.2 (2012-03-16)

# sort.py
# *******
#
# ::

u"""
Sortiere eine Wortliste und erstelle einen Patch im "unified diff" Format.
Ohne Angabe einer Eingangsdatei wird von der Standardeingabe gelesen.

Die Kodierung ist UTF8.

Es wird wahlweise nach Duden oder nach der bis März 2012 für die Wortliste
genutzten Regel sortiert. Voreinstellung ist Dudensortierung.
"""

usage = u'%prog [Optionen] [Eingangsdatei]\n' + __doc__


import unicodedata, sys, optparse, os

# path for local Python modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

from edit_tools.wortliste import (WordFile, WordEntry, 
                                  join_word, udiff, sortkey_duden)

# sortkey_wl
# ----------
#
# Sortierschlüssel für den früher genutzten ("W.-Lemberg-") Algorithmus,
# d.h Emulation von:
#
# * Sortieren nach gesamter Zeile
# * mit dem Unix-Aufruf `sort -d`
# * und locale DE.
#
# ::

def sortkey_wl(entry):
    # Sortieren nach gesamter Zeile
    key = unicode(entry)

    # Ersetzungen:
    ersetzungen = {ord(u'ß'): u'ss'} # ß -> ss
    # Feldtrenner und Trennzeichen ignorieren (Simulation von `sort -d`)
    for char in u';-·=|[]{}':
        ersetzungen[ord(char)] = None
    key = key.translate(ersetzungen)

    # Akzente/Umlaute weglassen:
    key = unicodedata.normalize('NFKD', key) # Akzente mit 2-Zeichen-Kombi
    key = key.encode('ascii', 'ignore')     # ignoriere nicht-ASCII Zeichen
    # Großschreibung ignorieren
    key = key.lower()

    return key


# Aufruf von der Kommandozeile
# ============================
#
# ::

if __name__ == '__main__':

    # Optionen:

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-o', '--outfile', dest='patchfile',
                      help='Ausgangsdatei (Patch), Vorgabe "wortliste-sortiert.patch"',
                      default='wortliste-sortiert.patch')
    parser.add_option('-a', '--legacy-sort', action="store_true",
                      help='alternative (obsolete) Sortierordnung',
                      default=False)
    parser.add_option('-d', '--dump', action="store_true", default=False,
                      help='Schreibe die sortierte Liste '
                      'auf die Standardausgabe.')

    (options, args) = parser.parse_args()

    # Achtung: bool(options.legacy_sort) ist immer True, daher nicht
    # ``if options.legacy_sort: ...`` verwenden!
    if options.legacy_sort is True:
        sortkey = sortkey_wl
    else:
        sortkey = sortkey_duden

    # Einlesen in eine Liste::
    
    if args:
        eingangsdateiname = args[0]
        wordfile = WordFile(eingangsdateiname)
        wortliste = list(wordfile)
    else:
        eingangsdateiname = 'stdin'
        wortliste = [WordEntry(line.rstrip().decode('utf-8'))
                     for line in sys.stdin]

    # Sortieren::

    sortiert = sorted(wortliste, key=sortkey)

    if options.dump:
        for line in sortiert:
            print unicode(line).encode('utf8')
        sys.exit()

    patch = udiff(wortliste, sortiert,
                  eingangsdateiname, eingangsdateiname+'-sortiert',
                  encoding='utf-8')
    if patch:
        print patch
        if options.patchfile:
            patchfile = open(options.patchfile, 'w')
            patchfile.write(patch + '\n')
    else:
        print 'keine Änderungen'
