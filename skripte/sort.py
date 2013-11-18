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

Es wird wahlweise nach Duden oder nach der bis März 2012 für die Wortliste
genutzten Regel sortiert. Voreinstellung ist Dudensortierung.
"""

usage = u'%prog [Optionen]\n' + __doc__


import unicodedata, sys, optparse, os
# path for local Python modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))
from werkzeug import WordFile, udiff

# Sortierschlüssel
# ================
#
# Umlautumschreibung:
#
# ::

umschrift = {
             ord(u'A'): u'A*',
             ord(u'Ä'): u'Ae',
             ord(u'O'): u'O*',
             ord(u'Ö'): u'Oe',
             ord(u'U'): u'U*',
             ord(u'Ü'): u'Ue',
             ord(u'a'): u'a*',
             ord(u'ä'): u'ae',
             ord(u'o'): u'o*',
             ord(u'ö'): u'oe',
             ord(u'u'): u'u*',
             ord(u'ü'): u'ue',
             ord(u'ß'): u'sz',
          }

# sortkey_duden
# -------------
#
# Sortiere nach erstem Feld, alphabetisch gemäß Duden-Regeln::

def sortkey_duden(entry):

# Sortieren nach erstem Feld (ungetrenntes Wort)::

    key = entry[0]

# Großschreibung ignorieren:
#
# Der Duden sortiert Wörter, die sich nur in der Großschreibung unterscheiden
# "klein vor groß" (ASCII sortiert "groß vor klein"). In der
# `Trennmuster-Wortliste` kommen Wörter nur mit der häufiger anzutreffenden
# Großschreibung vor, denn der TeX-Trennalgorithmus ignoriert Großschreibung.
# ::

    key = key.lower()

# Ersetzungen:
#
# ß -> ss ::

    skey = key.replace(u'ß', u'ss')

# Restliche Akzente weglassen: Wandeln in Darstellung von Buchstaben mit
# Akzent als "Grundzeichen + kombinierender Akzent". Anschließend alle
# nicht-ASCII-Zeichen ignorieren::

    skey = unicodedata.normalize('NFKD', skey)
    skey = unicode(skey.encode('ascii', 'ignore'))

# "Zweitschlüssel" für das eindeutige Einsortieren von Wörtern mit
# gleichem Schlüssel (Masse/Maße, waren/wären, ...):
#
# * "*" nach aou für die Unterscheidung Grund-/Umlaut
# * ß->sz
#
# ::

    if key != skey:
        subkey = key.translate(umschrift)
        skey = u' '.join([skey,subkey])

# Gib den Sortierschlüssel zurück::

    return skey

# Test:
#
# >>> from sort import sortkey_duden
# >>> sortkey_duden([u"Abflußröhren"])
# u'abflussrohren a*bflu*szroehren'
# >>> sortkey_duden([u"Abflußrohren"])
# u'abflussrohren a*bflu*szro*hren'
# >>> sortkey_duden([u"Abflussrohren"])
# u'abflussrohren'
#
# >>> s = sorted([[u"Abflußröhren"], [u"Abflußrohren"], [u"Abflussrohren"]],
# ...            key=sortkey_duden)
# >>> print ', '.join(e[0] for e in s)
# Abflussrohren, Abflußrohren, Abflußröhren
#
#
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
                      help='Ausgangsdatei (Patch), Vorgabe "wortliste-sortiert.patch"',
                      default='wortliste-sortiert.patch')
    parser.add_option('-a', '--legacy-sort', action="store_true",
                      help='alternative (historische) Sortierordnung',
                      default=False)
    parser.add_option('-d', '--dump', action="store_true", default=False,
                      help='Schreibe sortierte Liste auf die Standardausgabe.')

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

    if options.dump:
        for line in sortiert:
            print unicode(line).encode('utf8')
        sys.exit()

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
