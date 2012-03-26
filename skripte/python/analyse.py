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


# teilwoerter
# -----------

# Sammlung von `dictionaries` mit Info über Teilwörter::

class teilwoerter(object):

# Liste möglicher Trennungen. Es kann unterschiedlche Trennungen eines
# identischen Teilworts geben, z.B. "Ba-se" (keine Säure) vs. "Base" (in
# Base=ball)::

    trennungen = defaultdict(list)

# Häufigkeiten des Auftretens der Teilwörter::

    S = defaultdict(int)   # Einzelwort (Solitär)
    E = defaultdict(int)   # erstes Wort in Verbindungen
    M = defaultdict(int)   # mittleres Wort in Verbindungen
    L = defaultdict(int)   # letztes Wort in Verbindungen


def read_teilwoerter(path='teilwoerter-%s.txt'%sprachvariante):

    words = teilwoerter()

    for line in open(path):
        line = line.decode('utf8')
        wort, flags = line.split()
        
        key = join_word(wort)
        if u'.' not in wort:
            words.trennungen[key].append(wort)
        
        flags = [int(n) for n in flags.split(u';')]
        
        for kategorie, n in zip([words.S, words.E, words.M, words.L], flags):
            if n > 0:
                kategorie[key] += n

    return words


# Analyse
# =====================
#
# Zerlege Wörter der Wortliste (unter `path`). Gib eine "teilwoerter"-Instanz
# mit dictionaries mit getrennten Teilwörtern als key und deren Häufigkeiten
# an der entsprechenden Position als Wert zurück::

def analyse(path='../../wortliste', sprachvariante=sprachvariante):

    wordfile = WordFile(path)
    words = teilwoerter()

    for entry in wordfile:

# Wort mit Trennungen in Sprachvariante::

        wort = entry.get(sprachvariante)
        if wort is None: # Wort existiert nicht in der Sprachvariante
            continue

# Teilwörter suchen::

        teile = wort.split(u'=')

        # Einzelwort
        if len(teile) == 1:
            if u'·' not in wort:
                words.S[wort] += 1
            continue

        gross = wort[0].istitle()

        # erstes Teilwort:
        if u'·' not in teile[0]:
            words.E[teile[0]] += 1

        # letztes Teilwort:
        teil = teile[-1]
        if u'·' not in teil:
            if gross: # Großschreibung übertragen
                teil = teil[0].title() + teil[1:]
            words.L[teil] += 1

        # mittlere Teilwörter
        for teil in teile[1:-1]:
            if u'·' in teil:
                # unkategorisierte Trennstelle(n): es könnte sich um ein
                # zusammengesetzes Wort handeln -> überspringen
                continue
            if gross: # Großschreibung übertragen
                teil = teil[0].title() + teil[1:]
            words.M[teil] += 1

    return words


# Ausgabe
# ==========

# Schreibe das Resultat von `analyse` in eine Datei `path`::

def write_teilwoerter(words, path='teilwoerter-%s.txt'%sprachvariante):

    outfile = open(path, 'w')

    # Menge aller Teilwörter:
    allwords = set()

    for kategorie in (words.S, words.E, words.M, words.L):
        allwords.update(set(kategorie.keys()))

    for key in sorted(allwords):
        line = '%s %d;%d;%d;%d\n' % (
            key, words.S[key], words.E[key], words.M[key], words.L[key])
        outfile.write(line.encode('utf8'))


# Bei Aufruf (aber nicht bei Import):;

if __name__ == '__main__':

# erstelle/aktualisiere die Datei ``teilwoerter.txt`` mit den Häufigkeiten
# nicht zusammengesetzer Wörter als Einzelwort oder in erster, mittlerer,
# oder letzeter Position in Wortverbindungen ::

    words = analyse()
    write_teilwoerter(words)
    sys.exit()
    

# Test::

    words = read_teilwoerter()
    
    for key in sorted(words.trennungen):
        line = u' '.join([key]+words.trennungen[key]) + u'\n'
        print line.encode('utf8'), 
    
