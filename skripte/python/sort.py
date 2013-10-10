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
Sortiere die Wortliste und erstelle einen Patch im "unified diff" Format.

Es wird wahlweise nach Duden, oder nach der bis März 2012 für die Wortliste
genutzten Regel sortiert. Voreinstellung ist Dudensortierung.
"""

usage = '%prog [Optionen]\n' + __doc__


import unicodedata, sys, optparse
from werkzeug import WordFile, udiff

# Sortierschlüssel
# ================
#
# sortkey_duden
# -------------
#
# Sortiere nach erstem Feld, alphabetisch gemäß Duden-Regeln::

def sortkey_duden(entry):

# Sortieren nach erstem Feld (ungetrenntes Wort)::

    key = entry[0]

# Großschreibung ignorieren:
#
# (Der Duden sortiert Wörter, die sich nur in der Großschreibung
# unterscheiden "klein vor groß". In der `Trennmuster-Wortliste`
# kommen diese Wörter nur mit der häufiger anzutreffenden
# Großschreibung vor.) ::

    key = key.lower()

# Ersetzungen
#
# ß -> ss
#
# Ein Nachsatz nach einem Leerzeichen sorgt für das
# Einsortieren nach einem gleichen Wort mit ss im Original
# (Masse < Maße):
#
# ::

    if u'ß' in key:
        key = key.replace(u'ß', u'ss')
        key += u' ß'

# Akzente/Umlaute weglassen:
#
# Wandeln in Darstellung von Buchstaben mit Akzent als "Grundzeichen +
# kombinierender Akzent". Anschließend alle nicht-ASCII-Zeichen ignorieren::

    key = unicodedata.normalize('NFKD', key)
    key = key.encode('ascii', 'ignore')

# Gib den Sortierschlüssel zurück::

    return key

# sortkey_wl
# ----------
#
# Sortierschlüssel für den bisher genutzten ("W.-Lemberg-") Algorithmus,
# d.h # Emulation von:
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
    parser.add_option('-i', '--file', dest='wortliste',
                      help='Eingangsdatei, Vorgabe "../../wortliste"',
                      default='../../wortliste')
    parser.add_option('-o', '--outfile', dest='patchfile',
                      help='Ausgangsdatei (Patch), Vorgabe "wortliste.patch"',
                      default='wortliste.patch')
    parser.add_option('-a', '--legacy-sort', action="store_true",
                      help='alternative (historische) Sortierordnung',
                      default=False)

    (options, args) = parser.parse_args()

    # Achtung: bool(options.legacy_sort) ist immer True, daher nicht
    # ``if options.legacy_sort: ...`` verwenden!
    if options.legacy_sort is True:
        sortkey = sortkey_wl
    else:
        sortkey = sortkey_duden

    # Einlesen in eine Liste::

    wordfile = WordFile(options.wortliste)
    wortliste = list(wordfile)

    # Sortieren::

    sortiert = sorted(wortliste, key=sortkey)

    patch = udiff(wortliste, sortiert,
                  options.wortliste, options.wortliste+'-sortiert',
                  encoding=wordfile.encoding)
    if patch:
        print patch
        if options.patchfile:
            patchfile = open(options.patchfile, 'w')
            patchfile.write(patch + '\n')
    else:
        print 'keine Änderungen'
