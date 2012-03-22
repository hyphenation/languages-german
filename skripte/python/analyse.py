#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# analyse.py: Sammeln und Sortieren von Teilwörtern
# =================================================
#
# Erstelle eine Liste der Teilwörter von in der Wortliste_ markierten
# zusammengesetzten Wörtern mit den Häufigkeiten des Auftretens als:
#
# :S: Einzelwort (Solitär)
# :E: erstes Wort in Verbindungen
# :M: mittleres Wort in Verbindungen
# :L: letztes Wort in Verbindungen
#
# Format:
#
# * Teilwort mit Trennungen. Großschreibung wie Gesamtwort
# * Leerraum (whitespace)
# * Häufigkeiten in der Reihenfolge S;E;M;L
#
# Beispiel:
#
# Ho-se 1;0;0;7
#
#
# TODO: Vorsilben, Silben
#
# .. contents::
#
# Vorspann
# ========
#
# Importiere Python Module::

import re       # Funktionen und Klassen für reguläre Ausdrücke
import sys      # sys.exit() zum Abbruch vor Ende (für Testzwecke)
from collections import defaultdict  # Wörterbuch mit Default
# from copy import deepcopy

from werkzeug import WordFile, join_word, udiff

# Globale Variablen
# -----------------
#
# Ausgangsbasis
#
# ::

wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen

# Sprachvarianten
# ---------------
#
# Sprach-Tag nach [BCP47]_::

sprachvariante = 'de-1901'         # "traditionell"
# sprachvariante = 'de-1996'         # Reformschreibung
# sprachvariante = 'de-x-GROSS'      # ohne ß (Großbuchstaben und Kapitälchen)
# sprachvariante = 'de-1901-x-GROSS'   # ohne ß (Schweiz oder GROSS)
# sprachvariante = 'de-1996-x-GROSS' # ohne ß (Schweiz oder GROSS)
# sprachvariante = 'de-CH-1901'     # ohne ß (Schweiz) ("süssauer")


# Wortkategorien:

# :S: Einzelwort (Solitär)
# :E: erstes Wort in Verbindungen
# :M: mittleres Wort in Verbindungen
# :L: letztes Wort in Verbindungen

words = {}

for key in 'SEML':
    words[key] = defaultdict(int)  # neue Einträge erhalten Ausgangswert 0


# Analyse
# =====================
#
# Durchlaufe alle Einträge::


for entry in wordfile:

# Wort mit Trennungen in Sprachvariante::

    wort = entry.get(sprachvariante)
    if wort is None: # Wort existiert nicht in der Sprachvariante
        continue

# Teilwörter suchen::

    teile = wort.split(u'=')

    # Einzelwort (Solitär)
    if len(teile) == 1:
        if u'·' not in wort:
            words['S'][wort] += 1
        continue

    gross = wort[0].istitle()

    # erstes Teilwort:
    if u'·' not in teile[0]:
        words['E'][teile[0]] += 1

    # letztes Teilwort:
    teil = teile[-1]
    if u'·' not in teil:
        if gross: # Großschreibung übertragen
            teil = teil[0].title() + teil[1:]
        words['L'][teil] += 1

    for teil in teile[1:-1]:        # mittlere Teilwörter
        if u'·' in teil:
            # unkategorisierte Trennstelle(n): es könnte sich um ein
            # zusammengesetzes Wort handeln -> überspringen
            continue
        if gross: # Großschreibung übertragen
            teil = teil[0].title() + teil[1:]
        words['M'][teil] += 1



# Ausgabe
# ==========

outfile = open('teilwoerter.txt', 'w')

# Menge aller Teilwörter::

allwords = set()

for key in 'SEML':
    allwords.update(set(words[key].keys()))

for key in sorted(allwords):
    line = '%s S%d;E%d;M%d;L%d\n' % (
           key, words['S'][key], words['E'][key],
           words['M'][key], words['L'][key])
    outfile.write(line.encode('utf8'))
